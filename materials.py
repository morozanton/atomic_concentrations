import pandas as pd
import re

NIST_DATA = pd.read_csv("data/nist_isotopic_compositions.csv")
NIST_DATA[["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]] = (
    NIST_DATA[
        ["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]
    ].apply(pd.to_numeric)
)


class Isotope:
    """Represents an isotope with physical properties."""

    def __init__(
        self,
        atomic_number: int,
        mass_number: int,
        atomic_mass: float,
        atomic_weight: float,
        abundance: float = 1.0,
    ):
        self.atomic_number = atomic_number
        self.mass_number = mass_number
        self.isotope_code = str(int(self.atomic_number)) + f"{int(self.mass_number):03}"
        self.atomic_mass = atomic_mass
        self.atomic_weight = atomic_weight
        self.abundance = abundance
        self.concentration = None

    @property
    def isotope_code(self) -> str:
        """
        Returns the isotope code in the MCNP format.
        """
        return f"{self.atomic_number}{self.mass_number:03}"

    @isotope_code.setter
    def isotope_code(self, value: str):
        self._isotope_code = value


class Element:
    """Represents a chemical element, handling both natural and specific radioactive isotopes."""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.isotopes = []
        self._retrieve_composition()

    def _retrieve_composition(self):
        """
        Retrieves the isotopic composition of the element from the NIST database.
        """
        mass_number = None

        if self.symbol in ["D", "T"]:
            mass_number = 2 if self.symbol == "D" else 3
            search_symbol = "H"
        if match := re.search(r"\d+", self.symbol):
            mass_number = int(match.group(0))
            search_symbol = re.sub(r"\d+", "", self.symbol)
        else:
            search_symbol = self.symbol

        params = NIST_DATA["element"] == search_symbol
        if mass_number:
            params &= NIST_DATA["mass_number"] == mass_number

        data = NIST_DATA[params]

        if data.empty:
            raise ValueError(f"Element/Isotope not found: {self.symbol}")

        for _, row in data.iterrows():
            if mass_number or pd.notna(row["isotopic_composition"]):
                self.isotopes.append(
                    Isotope(
                        atomic_number=int(row["atomic_number"]),
                        mass_number=int(row["mass_number"]),
                        atomic_mass=float(row["isotope_atomic_mass"]),
                        atomic_weight=float(row["element_atomic_weight"]),
                        abundance=float(row["isotopic_composition"])
                        if not mass_number
                        else 1.0,
                    )
                )


class Mixture:
    """
    Represents a mixture of elements with specified formula, density, and optional name.
    Calculates the nuclear concentrations of each isotope in the mixture.
    """

    def __init__(
        self,
        formula: str,
        density: float,
        name: str | None = None,
        use_weight_fractions: bool = False,
    ):
        """
        Initializes the Mixture object with the given formula, density, name, and optional use_weight_fractions flag.
        formula: the chemical formula of the mixture
        density: the density of the mixture in g/cm^3
        name (optional): the name of the mixture. If not defined, the formula is used as the name
        use_weight_fractions (optional): whether to use weight fractions instead of molar fractions
        """

        self.name = name if name else formula
        self.formula = formula
        self.density = density
        self.AVOGADRO = 0.602214076
        self.use_weight_fractions = use_weight_fractions

        self.element_amounts = re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", self.formula)
        self.isotopes = []

        if not self.use_weight_fractions:
            self.compound_molar_mass = self.calculate_molar_mass()
        else:
            self.compound_molar_mass = None
            self.total_weight_parts = sum(
                float(x[1]) if x[1] else 1.0 for x in self.element_amounts
            )

        self.update_isotope_concentrations()

    def _get_element(self, element_symbol: str):
        """
        Returns an Element object for the given element symbol.
        """
        return Element(element_symbol)

    def calculate_molar_mass(self) -> float:
        """
        Calculates the molar mass of the compound.
        """
        mass = 0
        for sym, fraction in self.element_amounts:
            element = self._get_element(sym)
            fraction = float(fraction) if fraction else 1.0
            mass += element.isotopes[0].atomic_weight * fraction
        return mass

    def update_isotope_concentrations(self) -> None:
        """
        Calculates the isotope concentrations based on the density and element amounts.
        """
        for sym, fraction in self.element_amounts:
            element = self._get_element(sym)
            fraction = float(fraction) if fraction else 1.0
            for isotope in element.isotopes:
                if self.use_weight_fractions:
                    w_i = fraction / self.total_weight_parts
                    isotope.concentration = (
                        self.AVOGADRO * self.density * isotope.abundance * w_i
                    ) / isotope.atomic_weight
                else:
                    isotope.concentration = (
                        self.AVOGADRO * self.density * isotope.abundance * fraction
                    ) / self.compound_molar_mass
                self.isotopes.append(isotope)

    def __mul__(self, other):
        """
        Multiplies the mixture by a scalar fraction.
        Returns a Material with scaled density and concentrations.
        """
        if isinstance(other, (int, float)):
            factor = float(other)
            new_mat = Material(name=self.name, density=self.density * factor)

            new_mat.isotopes = {}
            for iso in self.isotopes:
                if iso.concentration:
                    new_mat.isotopes[iso.isotope_code] = iso.concentration * factor
            return new_mat
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        """
        Implements addition. Logic is delegated to Material additive properties.
        Effectively converts self to Material and calls Material.__add__.
        """
        return (self * 1.0) + other


class Material:
    """
    Represents a homogenized material combining multiple components.
    Stores accumulated density and isotopic concentrations directly.
    """

    def __init__(
        self,
        name: str | Mixture | None = None,
        density: float = 0.0,
        concentration_threshold: float = 0.0,
        formula: str | None = None,
    ):
        """
        Initialize a Material object.
        name: Name of the material.
        density: Initial density (g/cm3).
        concentration_threshold: Threshold to drop low concentrations.
        formula: Optional shortcut to create from formula (creates internal Mixture first).
        """
        self.name = name
        self.density = density
        self.concentration_threshold = concentration_threshold
        self.isotopes = {}  # Map: isotope_code -> concentration

        initial_mix = None
        if isinstance(name, Mixture):
            # Create a one-component material from a Mixture
            initial_mix = name
            self.name = name.name

        elif formula:
            # Create a one-component material from a formula string
            if density is None or density == 0.0:
                raise ValueError("Density required for formula init")
            self.name = name if name else formula
            initial_mix = Mixture(formula, density, name=self.name)

        if initial_mix:
            self.density = initial_mix.density
            for iso in initial_mix.isotopes:
                if iso.concentration:
                    self.isotopes[iso.isotope_code] = iso.concentration

    def __add__(self, other):
        if isinstance(other, Mixture):
            # Convert Mixture to Material (factor 1.0) if needed
            other = other * 1.0

        if isinstance(other, Material):
            new_name = self.name

            if not new_name and other.name:
                new_name = other.name

            new_mat = Material(
                name=new_name,
                density=self.density
                + other.density,  # Because we are using partial densities
                concentration_threshold=min(
                    self.concentration_threshold, other.concentration_threshold
                ),
            )

            new_mat.isotopes = self.isotopes.copy()
            for code, conc in other.isotopes.items():
                new_mat.isotopes[code] = new_mat.isotopes.get(code, 0.0) + conc

            return new_mat
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            factor = float(other)
            new_mat = Material(
                name=self.name,
                density=self.density * factor,
                concentration_threshold=self.concentration_threshold,
            )
            for code, conc in self.isotopes.items():
                new_mat.isotopes[code] = conc * factor
            return new_mat
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        """
        Returns a string representation of the material in PHITS format.
        """
        if self.density is None:
            self.density = 0.0

        material_string = [f"$ {self.name};\t{self.density:.3f} g/cm3"]

        # Filter and sort
        valid_isotopes = []
        for code, conc in self.isotopes.items():
            if conc >= self.concentration_threshold:
                valid_isotopes.append((code, conc))

        valid_isotopes.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)

        for code, conc in valid_isotopes:
            material_string.append(f"{code}\t{conc:.6E}")

        return "\n".join(material_string)


if __name__ == "__main__":
    """
    Example of creating a Shielding material from two mixtures
    """
    # Option 1: simple material definition from formula
    water = Material("Water", density=1.0, formula="H2O")
    print(water, "\n")

    # Option 2: material definition from Mixtures
    polyethylene = Mixture("CH2", density=0.94, name="Polyethylene")
    boric_acid = Mixture("B4C", density=2.52, name="Boric Acid")

    shielding = polyethylene * 0.9 + boric_acid * 0.1

    shielding.name = "Borated_Poly_10vol"
    shielding.concentration_threshold = 1e-4  # Filter low concentrations
    print(shielding, "\n")

    # Using radioactive isotopes

    heavy_water = 0.7 * Material(
        "Heavy Water", density=1.1, formula="D2O"
    ) + 0.3 * Material("Water", density=1.0, formula="H2O")
    print(heavy_water)
