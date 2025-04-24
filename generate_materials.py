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
        print()

        self.calculate(self.formula, self.density)

    @staticmethod
    def parse_formula(formula: str):
        matches = re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", formula)
        return {m[0]: float(m[1]) if m[1] else 1 for m in matches}

    @staticmethod
    def get_isotope_code(atomic_number, mass_number) -> str:
        mass_formatted = f"{int(mass_number):03}"
        return str(int(atomic_number)) + mass_formatted

    def calculate(self, formula, density) -> None:
        elements = self.parse_formula(formula)

        compound_mass = 0
        purity_factor = 1
        for el, num in elements.items():
            if num < 1:
                purity_factor -= num
                continue
            mass = self.data[self.data["element"] == el]["element_atomic_weight"].dropna().iloc[0]
            compound_mass += mass * num
        compound_mass /= purity_factor

        output = [f"m1\t\t$ {formula}; {density} g/cc\n"]

        factor = self.AVOGADRO * density
        for el, formula_units in elements.items():

            isotopes = self.data[self.data["element"] == el]
            if formula_units < 1:
                formula_units = 1

            for index, row in isotopes.iterrows():
                if pd.notna(row["isotopic_composition"]):
                    atomic_concentration = (factor * row["isotopic_composition"] *
                                            formula_units / compound_mass)

                    atomic_concentration = f"{atomic_concentration:.6E}"

                    isotope_code = self.get_isotope_code(atomic_number=row["atomic_number"],
                                                         mass_number=row["mass_number"])
                    output.append(f"{isotope_code}\t{atomic_concentration}\n")
        output.sort(key=lambda x: int(x[1:].split()[0]))
        print("".join(output))


if __name__ == "__main__":
    convertor = ConcentrationConvertor()
