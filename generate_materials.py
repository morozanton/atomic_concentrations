import re

import pandas as pd


class ConcentrationConvertor:
    """
    A class to calculate atomic concentrations of isotopes in a material based on its chemical composition and density.
    """

    def __init__(self):
        """
        Initializes the ConcentrationConvertor by loading isotopic data from the NIST table,
        prompting the user for input, and performing the initial calculation.

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

        self.formula = input("Chemical composition (e.g. 'H2O', 'C2H4 B0.2'):\n---> ").strip()
        self.density = float(input("Density (g/cc): ").strip())
        name = input("Material name (leave blank to use chemical formula): ").strip()

        self.material_name = name if name else self.formula
        print()

        self.calculate(self.formula, self.density)

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

    def calculate(self, formula: str, density: float) -> None:
        """
        Calculates the atomic concentrations of isotopes in a material based on its element composition and density.

        Performs the following steps:
        1. Parses the material formula into its constituent elements and their quantities.
        2. Computes the molecular mass of each material component.
        3. Calculates the atomic concentration of each isotope using the material density and isotopic composition.
        4. Generates a formatted output containing isotope codes and their atomic concentrations.

        Args:
            formula (str): The formula of the material (e.g., 'Al2O3', 'C2H4 B0.2').
            density (float): The density of the material in g/cc.

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
