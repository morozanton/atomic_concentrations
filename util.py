import re


def count_unique_atoms(material: str):
    atoms = re.findall(r"([A-Z][a-z]?)(\d*)", material)
    unique = {}
    for a in atoms:
        if a[0] in unique:
            unique[a[0]] += int(a[1]) if a[1] else 1
        else:
            unique[a[0]] = int(a[1]) if a[1] else 1
    return "".join([f"{k}{v}" for k, v in unique.items()])


if __name__ == "__main__":
    # EXAMPLE:
    print(count_unique_atoms("HO-C2H4-NH2"))  # output: H7O1C2N1
    print(count_unique_atoms("KAl3Si3O10F2"))  # output: K1Al3Si3O10F2
