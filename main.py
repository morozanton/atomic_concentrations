from materials import Material
import re


def parse_mixture(mixture):
    fractions = {}

    for part in mixture.split('+'):
        match = re.search(r"(\d+.?\d*)%(.+)", part.strip())
        if match:
            fraction = float(match.group(1))
            formula = match.group(2)
            fractions[formula] = fraction
        else:
            fractions[part] = 1.0

    return fractions


def run_sequence():
    materials = []
    n_materials = int(input("Number of materials: "))

    for i in range(1, n_materials + 1):
        print(f"\nMaterial {i}")

        formula = input("Chemical composition (e.g. 'H2O', '90% SiO2 + 10% B2O3...'):\n").strip()
        name = input(f"Material name (leave blank to use {formula}): ").strip()
        density = float(input(f"Material {i} density (g/cc):\n").strip())

        materials.append(
            f"m{i} " + str(Material(compound_fractions=parse_mixture(formula), density=density, name=name)))

    for m in materials:
        print("\n" + m)


if __name__ == "__main__":
    run_sequence()
