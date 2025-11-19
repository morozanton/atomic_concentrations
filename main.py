from materials import Material
import re


def parse_mixture(mixture):
    """Parse a chemical mixture string into a dictionary of compounds and their fractions."""
    fractions = {}

    for part in mixture.split("+"):
        match = re.search(r"(\d+.?\d*)%(.+)", part.strip())
        if not match:
            match = re.search(r"(\d+\.\d+)(.*)", part.strip())
        if match:
            fraction = float(match.group(1))
            formula = match.group(2)
            fractions[formula] = fraction
        else:
            fractions[part.strip()] = 1.0
    return fractions


def run_sequence():
    """Run the sequence to input material data and create a Material object."""

    print(f"\nMaterial")
    formula = input(
        "Chemical composition (e.g. 'H2O', '90% SiO2 + 10% B2O3...'):\n"
    ).strip()
    name = input(f"Material name (leave blank to use '{formula}'): ").strip()
    density = input(f"Density (g/cc):\n").strip()
    density = float(density) if density else 0

    if formula and density:
        return f"m1 " + str(Material(compound_fractions=parse_mixture(formula), density=density, name=name))
    return ""


if __name__ == "__main__":
    # EXAMPLE:
    material = Material(
        compound_fractions=parse_mixture("DT"),
        density=1,
        name="dt",
    )
    print(material)
    # Output:
    # $ dt;	1 g/cm3
    # 1002	1.196783E-01
    # 1003	1.196783E-01
