# Atomic Concentrations

Calculates atomic concentrations from chemical formula or material description.

## Description

This code uses
a [NIST table of Atomic Weights and Isotopic Compositions](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl)
of naturally occurring isotopes to create material descriptions for later use in MonteCarlo codes.

## Output format

```
material_Id   $ material_name; density=value
isotope_code_1  atomic_concentration_1
isotope_code_2  atomic_concentration_2
...
```

Where:

- Part after the `$` symbol is a Fortran comment
- `isotope_code` consists of the atomic number and mass number (e.g. 1H -> *1001*, 16O -> *8016*)
- `atomic_concentration` is in units of 1 x 10<sup>24</sup> atoms/cc

## Use cases

### 1. Chemical formulas

Elements or compounds (e.g. *O2, Pb, C10H8O4*)

**Input:**

```bash
Chemical composition(e.g. 'H2O', 'C2H4 B0.2'):
---> "H2O"
Density (g / cc): "0.998"
Material name(leave blank to use chemical formula):
```

**Output:**

```bash
m1	$ H2O; 0.998 g/cc
1001	6.669056E-02
1002	7.670297E-06
8016	3.326808E-02
8017	1.267266E-05
8018	6.836569E-05
```

### 2. Element compositions

E.g. steel grades, concrete mixes.

**Input:**

```bash
Chemical composition(e.g. 'H2O', 'C2H4 B0.2'):
---> "Fe0.988 C0.001 Mn0.0045 Si0.0025 S0.0002 P0.0002"
Density (g / cc): "7.87"
Material name(leave blank to use chemical formula): "Steel 10 (AISI 1010)"
```

**Output:**

```bash
m1	$ Steel 10 (AISI 1010); 7.87 g/cc
6012	3.902425E-04
6013	4.220756E-06
14028	3.889341E-04
14029	1.975816E-05
14030	1.303996E-05
15031	3.059196E-05
25055	3.880704E-04
16032	2.806816E-05
16033	2.216141E-07
16034	1.255813E-06
16036	2.954855E-09
26054	4.899236E-03
26056	7.690753E-02
26057	1.776130E-03
26058	2.363703E-04
```

### 3. Mixed input

Chemical compounds with additives/impurities (e.g. '*H2O Mg0.002*')

**Input:**

```bash
Chemical composition(e.g. 'H2O', 'C2H4 B0.2'):
---> "C2H4 B0.2"
Density (g / cc): "0.99"
Material name(leave blank to use chemical formula): "Borated polyethylene 20%"
```

**Output:**

```bash
m1	$ Borated polyethylene 20%; 0.99 g/cc
1001	8.496907E-02
1002	9.772567E-06
5010	2.193555E-03
5011	8.829333E-03
6012	4.203479E-02
6013	4.546368E-04
```

## Classes

### `ConcentrationConvertor`

A class to calculate atomic concentrations of isotopes in a material based on its chemical composition and density.

#### Attributes

- **`AVOGADRO` (float):** Avogadro's number in units of 1/(mol * g/cc).
- **`data` (pd.DataFrame):** DataFrame containing isotopic data from the NIST table.
- **`formula` (str):** Chemical formula of the material.
- **`density` (float):** Density of the material in g/cc.
- **`material_name` (str):** Name of the material, either user-provided or derived from the formula.

---

## Methods

### `__init__()`

Initializes the `ConcentrationConvertor` by loading isotopic data, prompting the user for input, and performing the
initial calculation.

#### Attributes:

- **`AVOGADRO` (float):** Avogadro's number in units of 1/(mol * g/cc).
- **`data` (pd.DataFrame):** DataFrame containing isotopic data from the NIST table.
- **`formula` (str):** Chemical formula of the material.
- **`density` (float):** Density of the material in g/cc.
- **`material_name` (str):** Name of the material, either user-provided or derived from the formula.

---

### `parse_formula(formula: str)`

Parses a material definition into its constituent elements and their quantities.

#### Args:

- **`formula` (str):** The chemical formula as a string (e.g., *'H2O', 'C2H4 B0.2'*).

#### Returns:

- **`list[dict[str, float]]`:** A list of dictionaries where each dictionary represents a component of the material,
  consisting of separate chemical elements and their quantities.

#### Example:

- **Input:** `'C2H4 B0.2'`
- **Output:** `[{'C': 2.0, 'H': 4.0}, {'B': 0.2}]`

---

### `get_isotope_code(atomic_number, mass_number) -> str`

Generates a unique isotope code based on the atomic number and mass number.

#### Args:

- **`atomic_number` (int):** The atomic number of the element.
- **`mass_number` (int):** The mass number of the isotope.

#### Returns:

- **`str`:** A string representing the isotope code, formatted as a concatenation of the atomic number and the mass
  number.

#### Example:

- **Input:** `atomic_number=1, mass_number=2`
- **Output:** `'1002'`

---

### `calculate(formula: str, density: float, threshold: float = 1e-6) -> None`

Calculates the atomic concentrations of isotopes in a material based on its element composition and density.

#### Args:

- **`formula` (str):** The formula of the material (e.g., 'Al2O3', 'C2H4 B0.2').
- **`density` (float):** The density of the material in g/cc.
- **`threshold` (float):** Minimum concentration threshold for isotopes to be included in the output.

#### Returns:

- **`None`:** The results are printed to the console.

#### Output Format:

- **First line:** Material name and density.
- **Subsequent lines:** Isotope codes and their atomic concentrations in decimal notation.

#### Example:

- **Input:** `formula='H2O', density=1.0`
- **Output:**
  ```
  m1        $ H2O; 1.0 g/cc
  1001      6.674E-02
  1002      3.326E-02
  ```
- **Input:** `formula="Fe0.988 C0.001 Mn0.0045 Si0.0025 S0.0002 P0.0002", density=7.87`
- **Output:**
  ```
   m1	$ Steel 10; 7.87 g/cc
   6012	3.902425E-04
   6013	4.220756E-06
   14028	3.889341E-04
   14029	1.975816E-05
   ...
  ```

---

## Static Methods

### `load_isotopic_data(file_path: str) -> pd.DataFrame`

Loads isotopic composition data from a CSV file into a pandas DataFrame.

#### Args:

- **`file_path` (str):** The path to the CSV file containing isotopic data.

#### Returns:

- **`pd.DataFrame`:** A DataFrame containing the isotopic composition data.

#### Raises:

- **`FileNotFoundError`:** If the specified file does not exist.
- **`pd.errors.EmptyDataError`:** If the file is empty.
- **`pd.errors.ParserError`:** If the file cannot be parsed as a CSV.

#### Example:

- **Input:** `file_path='data/isotopes.csv'`
- **Output:** A DataFrame with columns such as 'Element', 'AtomicNumber', 'MassNumber', etc.
