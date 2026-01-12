# Atomic Concentrations

A Python library for calculating atomic concentrations of isotopes for MonteCarlo radiation transport codes (MCNP, PHITS). It allows defining materials via chemical formulas and combining them intuitively using arithmetic operations.

## Features

*   **Chemical Formulas**: Define materials using standard chemical notation (e.g., `H2O`, `B4C`, `C2H4`).
*   **Natural Isotope Abundance**: Automatically retrieves natural isotopic compositions from NIST data.
*   **Intuitive Mixing**: Combine materials using standard arithmetic operators (`+`, `*`) to create complex mixtures (e.g., concrete, shielding).
*   **PHITS Output**: Generates formatted material cards for PHITS input files (also compatible with MCNP logic).

## Classes

### `Mixture`
Represents a specific chemical compound or element with a fixed stoichiometry.
*   **Input**: Formula string (e.g., "H2O") and density.
*   **Logic**: Calculates molar fractions and partial densities of elements.

### `Material`
Represents a homogeneous engineering material. It can be created from a single `Mixture` or by combining multiple materials/mixtures.
*   **Logic**: Stores specific isotopic concentrations and total density. Supports homogenization of multiple components.

## Usage Examples

### 1. Simple Material from Formula
You can create a material directly from a chemical formula string.

```python
from materials import Material

# Water with density 1.0 g/cm3
water = Material("Water", density=1.0, formula="H2O")
print(water)
```

**Output:**
```
$ Water;	1.000 g/cm3
1001	6.684797E-02
1002	7.688401E-06
8016	3.334660E-02
...
```

### 2. Complex Mixtures (Arithmetic)
You can define complex materials by mixing components by volume. The `+` operator adds components, and `*` scales their volume fraction (and partial density).

```python
from materials import Mixture, Material

# Define components
polyethylene = Mixture("CH2", density=0.94, name="Polyethylene")
boric_acid = Mixture("B4C", density=2.52, name="Boric Acid")

# Create Borated Polyethylene (90% Poly, 10% Boric Acid by volume)
# Logic: 0.9 * Poly + 0.1 * Boric = New Material
shielding = polyethylene * 0.9 + boric_acid * 0.1

shielding.name = "Borated_Poly_10vol"
shielding.concentration_threshold = 1e-4 # Optional: filter low-concentration isotopes

print(shielding)
```

**Output:**
```
$ Borated_Poly_10vol;	1.098 g/cm3
1001	7.263575E-02
5010	2.185836E-03
5011	8.798263E-03
...
```

### 3. Mixing Materials
You can mix existing `Material` objects with `Mixture` objects or other `Material` objects.

```python
# Heavy Water mixture
heavy_water = 0.7 * Material("D2O", density=1.1, formula="D2O") + \
              0.3 * Material("H2O", density=1.0, formula="H2O")
```

## Requirements
*   `pandas` (for reading NIST data)
*   `numpy` (optional, used internally if specific vectorization needed)

## Data Source
The library uses `data/nist_isotopic_compositions.csv` which contains NIST data for atomic weights and isotopic compositions.
