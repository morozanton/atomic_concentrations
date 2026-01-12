from materials import Mixture, Material

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
