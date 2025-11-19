import pandas as pd
import re


class Isotope:
    def __init__(self, atomic_number: int, mass_number: int, atomic_mass: float, abundance: float = 1.0):
        self.atomic_number = atomic_number
        self.mass_number = mass_number
        self.isotope_code = str(int(self.atomic_number)) + f"{int(self.mass_number):03}"
        self.atomic_mass = atomic_mass
        self.abundance = abundance
        self.concentration = None


class Element:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.nist_data = pd.read_csv("data/nist_isotopic_compositions.csv")
        self.nist_data[["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]] = self.nist_data[
            ["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]].apply(pd.to_numeric)
        self.isotopes = []
        self.radioactive = False


class StableElement(Element):
    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.retrieve_natural_composition()
        self.radioactive = False

    def retrieve_natural_composition(self):
        isotopes = self.nist_data[self.nist_data["element"] == self.symbol]

        for i in range(len(isotopes)):
            row = isotopes.iloc[i]
            if pd.notna(row["isotopic_composition"]):
                isotope = Isotope(atomic_number=row["atomic_number"],
                                  mass_number=row["mass_number"],
                                  atomic_mass=row["isotope_atomic_mass"],
                                  abundance=row["isotopic_composition"])
                self.isotopes.append(isotope)


class RadioactiveElement(Element):
    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.mass_number = self.parse_mass_number()

        self.radioactive = True
        self.retrieve_isotope_data()

    def parse_mass_number(self):
        if self.symbol == "D":
            return 2
        elif self.symbol == "T":
            return 3
        elif match := re.search(r"\d+", self.symbol):
            self.symbol = re.sub(r"\d+", "", self.symbol)
            return int(match.group(0))
        else:
            raise ValueError("Radioactive element must include mass number (e.g., C14, 14C, C-14...)")

    def retrieve_isotope_data(self):
        isotope_data = self.nist_data[
            (self.nist_data["element"] == self.symbol) & (self.nist_data["mass_number"] == self.mass_number)
            ]
        row = isotope_data.iloc[0]
        isotope = Isotope(
            atomic_number=row["atomic_number"],
            mass_number=row["mass_number"],
            atomic_mass=row["isotope_atomic_mass"],
            abundance=1.0)
        self.isotopes.append(isotope)


class ChemicalCompound:
    def __init__(self, formula: str, density: float, name: str | None = None):
        self.name = name if name else formula
        self.formula = formula
        self.density = density
        self.AVOGADRO = 0.602

        self.element_amounts = re.findall(r"([A-Z][a-z]?)(\d*)", self.formula)
        self.isotopes = []
        self.compound_molar_mass = self.calculate_molar_mass()
        self.update_isotope_concentrations()

    def calculate_molar_mass(self):
        mass = 0
        for el in self.element_amounts:
            if el[0] in ["D", "T"] or re.search(r"\d+", el[0]):
                element = RadioactiveElement(el[0])
            else:
                element = StableElement(el[0])
            formula_units = int(el[1]) if el[1] else 1
            for iso in element.isotopes:
                mass += iso.atomic_mass * formula_units * iso.abundance
        return mass

    def update_isotope_concentrations(self):
        for el in self.element_amounts:
            if el[0] in ["D", "T"] or re.search(r"\d+", el[0]):
                element = RadioactiveElement(el[0])
            else:
                element = StableElement(el[0])
            formula_units = int(el[1]) if el[1] else 1

            for isotope in element.isotopes:
                isotope.concentration = ((self.AVOGADRO * self.density * isotope.abundance * formula_units)
                                         / self.compound_molar_mass)
                self.isotopes.append(isotope)


class Material:
    def __init__(self, compound_fractions: dict, density: float, name: str | None = None):
        self.compound_fractions = compound_fractions
        self.parse_fractions()
        self.isotopes = {}

        self.density = density
        self.name = name if name else self.compose_material_name()
        self.compounds = [ChemicalCompound(formula=compound, density=density) for compound in
                          self.compound_fractions.keys()]
        self.recalculate_atomic_concentrations()

    def compose_material_name(self):
        if len(self.compound_fractions) == 1:
            print(list(self.compound_fractions.keys())[0])
            return list(self.compound_fractions.keys())[0]
        else:
            return " + ".join(
                [f"{fraction}{compound}" for compound, fraction in self.compound_fractions.items()])

    def parse_fractions(self):
        for compound, fraction in self.compound_fractions.items():
            if float(fraction) > 1.0:
                self.compound_fractions[compound] = fraction / 100

    def recalculate_atomic_concentrations(self):
        for compound in self.compounds:
            for isotope in compound.isotopes:
                updated_concentration = isotope.concentration * self.compound_fractions[compound.formula]
                if isotope in self.isotopes:
                    self.isotopes[isotope.isotope_code] += updated_concentration
                else:
                    self.isotopes[isotope.isotope_code] = updated_concentration

    def __str__(self):
        material_string = [f"$ {self.name};\t{self.density} g/cm3"]
        isotopes = sorted([(iso, concent) for iso, concent in self.isotopes.items()], key=lambda x: int(x[0]))
        for iso in isotopes:
            material_string.append(f"{iso[0]}\t{iso[1]:.6E}")
        return "\n".join(material_string)


if __name__ == "__main__":
    ...
