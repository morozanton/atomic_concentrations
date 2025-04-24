import re

import pandas as pd


class ConcentrationConvertor:
    AVOGADRO = 0.602

    def __init__(self):
        self.data = pd.read_csv("data/nist_isotopic_compositions.csv")
        self.data[
            ["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]] = self.data[
            ["element_atomic_weight", "isotope_atomic_mass", "isotopic_composition"]].apply(pd.to_numeric)

        self.formula = input("Chemical composition (e.g. 'H2O', 'C2H4 B0.2'):\n---> ").strip()
        self.density = float(input("Density (g/cc): ").strip())
        name = input("Material name (leave blank to use chemical formula): ").strip()

        self.material_name = name if name else self.formula
        print()

        self.calculate(self.formula, self.density)

    @staticmethod
    def parse_formula(formula: str):
        components = formula.split()
        composition = []

        for c in components:
            matches = re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", c)
            composition.append({m[0]: float(m[1]) if m[1] else 1 for m in matches})

        return composition

    @staticmethod
    def get_isotope_code(atomic_number, mass_number) -> str:
        mass_formatted = f"{int(mass_number):03}"
        return str(int(atomic_number)) + mass_formatted

    def calculate(self, formula: str, density: float) -> None:
        output = [f"m1\t\t$ {self.material_name}; {density} g/cc\n"]

        components = self.parse_formula(formula)
        for c in components:
            component_mass = sum(self.data[self.data["element"] == el]["element_atomic_weight"].dropna().iloc[0] * (
                num if num > 1 else 1)
                                 for el, num in c.items())

            common_factor = self.AVOGADRO * density / component_mass

            for el, formula_units in c.items():
                isotopes = self.data[self.data["element"] == el]

                for index, row in isotopes.iterrows():
                    if pd.notna(row["isotopic_composition"]):
                        atomic_concentration = f"{(common_factor * row["isotopic_composition"] * formula_units):.6E}"
                        isotope_code = self.get_isotope_code(atomic_number=row["atomic_number"],
                                                             mass_number=row["mass_number"])
                        output.append(f"{isotope_code}\t{atomic_concentration}\n")

        output.sort(key=lambda x: int(x[1:].split()[0]))
        print("".join(output))


if __name__ == "__main__":
    convertor = ConcentrationConvertor()
