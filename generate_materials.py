import re

import pandas as pd


class Material:
    """
    Represents a material with a chemical formula, density, and an optional name.
    """

    def __init__(self, formula: str, density: float, name: str | None = None):
        """
        Initializes a Material instance.

        Args:
            formula (str): The chemical formula of the material.
            density (float): The density of the material in g/cc.
            name (str, optional): The name of the material. Defaults to None.
        """
        self.name = name if name else formula
        self.formula = formula
        self.density = density

    def __str__(self):
        """
        Returns a string representation of the material.
        """
        return f"$ {self.name};\t{self.density} g/cm3"


class ConcentrationConvertor:
    """
    A class to calculate atomic concentrations of isotopes in a material based on its chemical composition and density.
    """

    def __init__(self):
        """
        Initializes the ConcentrationConvertor by loading isotopic data from the NIST table,
        prompting the user for input and performing the initial calculation.

        Attributes:
            AVOGADRO (float): Avogadro's number in units of 1/(mol * g/cc).
            data (pd.DataFrame): DataFrame containing isotopic data from the NIST table.
            formula (str): Chemical formula of the material.
            density (float): Density of the material in g/cc.
            material_name (str): Name of the material, either user-provided or derived from the formula.
        """

        self.AVOGADRO = 0.602
        self.data = pd.read_csv("data/nist_isotopic_compositions.csv")
        self.data[
            ["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]] = self.data[
            ["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]].apply(pd.to_numeric)

        self.materials = []
        self.init_materials()
        self.use_natural_concentrations = input(
            "Use natural isotopic compositions (y/n)?"
            "\nif not, only the primary isotopes will be considered.\n---> ").strip().lower() == "y"

    def init_materials(self):
        """
        Prompts the user to input multiple materials, including their formulas, names, and densities,
        and initializes them as Material objects, which are then added to the `self.materials` list.
        """
        n_mat = int(input("Number of materials: "))

        for i in range(1, n_mat + 1):
            print(f"\nMaterial {i}\n")
            formula = input("Chemical composition (e.g. 'H2O', 'C2H4 B0.2'):\n---> ").strip()
            name = input(f"Material {i} name (leave blank to use chemical formula): ").strip()
            density = [float(d) for d in input(f"Material {i} densities (g/cc);\ne.g. '2.3 2.5 2.8': ").strip().split()]
            for d in density:
                self.materials.append(Material(formula=formula, density=d, name=name))
        print()

    @staticmethod
    def parse_formula(formula: str):
        """
         Parses a material definition into its constituent elements and their quantities.

         Args:
             formula (str): The chemical formula as a string (e.g., 'H2O', 'C2H4 B0.2').

         Returns:
             list[dict[str, float]]: A list of dictionaries where each dictionary represents
             a component of the material, consisting of separate chemical elements and their quantities.
             If no quantity is specified for an element, it defaults to 1.

         Example:
             Input: 'C2H4 B0.2'
             Output: [{'C': 2.0, 'H': 4.0}, {'B': 0.2}]
         """

        components = formula.split()
        composition = []

        for c in components:
            matches = re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", c)
            composition.append({m[0]: float(m[1]) if m[1] else 1 for m in matches})

        return composition

    @staticmethod
    def get_isotope_code(atomic_number, mass_number) -> str:
        """
        Generates a unique isotope code based on the atomic number and mass number.

        Args:
            atomic_number (int): The atomic number of the element.
            mass_number (int): The mass number of the isotope.

        Returns:
            str: A string representing the isotope code, formatted as a concatenation
            of the atomic number and the mass number, where the mass number is zero-padded
            to three digits.

        Example:
            Input: atomic_number=1, mass_number=2
            Output: '1002'

            Input: atomic_number=82, mass_number=207
            Output: '82207'
        """

        mass_formatted = f"{int(mass_number):03}"
        return str(int(atomic_number)) + mass_formatted

    def calculate(self, threshold: float = 1e-6) -> None:
        """
        Calculates the atomic concentrations of isotopes in a material based on its element composition and density.

        For each material in self.materials, performs the following steps:
        1. Parses the material formula into its constituent elements and their quantities.
        2. Computes the molecular mass of each material component.
        3.
            (self.use_natural_concentrations == True):
                Calculates the atomic concentration of each naturally occurring isotope using the
                material density and isotopic composition.

            (self.use_natural_concentrations == False):
                Uses only the primary isotope of each element.

        4. Generates a formatted output containing isotope codes and their atomic concentrations.

        Args:
            threshold (float): minimum concentration threshold for isotopes to be included in the output.

        Returns:
            None: The results are printed to the console.

        Output Format:
            - First line: material name and density.
            - Subsequent lines: isotope codes and their atomic concentrations in decimal notation.

        Example:
            Input: formula='H2O', density=1.0
            Output:
                m1        $ H2O; 1.0 g/cc
                1001      6.674E-02
                1002      3.326E-02
                ...

            Input: formula="Fe0.988 C0.001 Mn0.0045 Si0.0025 S0.0002 P0.0002", density=7.87
            Output:
                m1		$ Steel 10; 7.87 g/cc
                6012	3.902425E-04
                6013	4.220756E-06
                14028	3.889341E-04
                14029	1.975816E-05
                ...
        """

        def get_concentration(factor: float, abundance: float, units: float, atomic_number, mass_number) -> str | None:
            """
            Calculates the atomic concentration of an isotope and formats it as a string.

            Args:
                factor (float): A common factor derived from the material's density and molecular mass.
                abundance (float): The isotopic abundance (fractional value between 0 and 1).
                units (float): The number of formula units of the element in the material.
                atomic_number (int): The atomic number of the element.
                mass_number (int): The mass number of the isotope.

            Returns:
                str | None: A formatted string containing the isotope code and its concentration,
                or None if the concentration is below the specified threshold.
            """
            concentration = f"{(factor * abundance * units):.6E}"
            if float(concentration) < threshold:
                return None

            isotope_code = self.get_isotope_code(atomic_number=atomic_number, mass_number=mass_number)
            return f"{isotope_code}\t{concentration}\n"

        result = []

        for i, mat in enumerate(self.materials, start=1):
            output = [f"m{i}\t\t{mat}\n"]
            components = self.parse_formula(mat.formula)

            for c in components:
                component_mass = 0

                for el, num in c.items():
                    weights = self.data[self.data["element"] == el]["element_atomic_weight"].dropna()
                    if not weights.empty:
                        weight = weights.iloc[0]
                    else:  # For radioactive isotopes, element_atomic_weight is zero
                        weight = self.data[self.data["element"] == el]["isotope_atomic_mass"].dropna().iloc[0]

                    component_mass += weight * (num if num > 1 else 1)

                common_factor = self.AVOGADRO * mat.density / component_mass

                for el, formula_units in c.items():
                    isotopes = self.data[self.data["element"] == el]

                    if not isotopes["isotopic_composition"].notna().any():
                        print(f"Warning: No abundance data for '{el}'. Using 100% isotope concentration...")
                        isotope = isotopes.iloc[0]
                        atomic_concentration = get_concentration(factor=common_factor,
                                                                 abundance=1.0,
                                                                 units=formula_units,
                                                                 atomic_number=isotope["atomic_number"],
                                                                 mass_number=isotope["mass_number"])
                        output.append(atomic_concentration)

                    else:
                        if not self.use_natural_concentrations:
                            primary_isotope = isotopes.loc[isotopes["isotopic_composition"].idxmax()]
                            atomic_concentration = get_concentration(factor=common_factor,
                                                                     abundance=1.0,
                                                                     units=formula_units,
                                                                     atomic_number=primary_isotope["atomic_number"],
                                                                     mass_number=primary_isotope["mass_number"])
                            output.append(atomic_concentration)

                        else:
                            for index, row in isotopes.iterrows():
                                if pd.notna(row["isotopic_composition"]):
                                    atomic_concentration = get_concentration(common_factor, row["isotopic_composition"],
                                                                             formula_units,
                                                                             atomic_number=row["atomic_number"],
                                                                             mass_number=row["mass_number"])
                                    output.append(atomic_concentration)
            output = [output[0]] + sorted(output[1:], key=lambda x: int(x.split("\t")[0]))
            result.append("".join(output))

        print()
        print("\n".join(result))


if __name__ == "__main__":
    convertor = ConcentrationConvertor()
    convertor.calculate()
