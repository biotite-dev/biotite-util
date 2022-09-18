import argparse
import json
import biotite.structure.io.pdbx as pdbx
from os.path import join


def create_files(components_pdbx_file_path, json_path):
    pdbx_file = pdbx.PDBxFile()
    pdbx_file.read(components_pdbx_file_path)
    components = pdbx_file.get_block_names()
    data_dict = {}
    for i, component in enumerate(components):
        print(f"{((i+1) / len(components) * 100):4.1f} %", end="\r")
        try:
            cif_dict = pdbx_file.get_category("chem_comp", block=component)
        except ValueError:
            # The 'chem_comp' category may contain unparsable names
            # with wrong quote escaping
            # In this case the PDBx file parser raises an Exception
            cif_dict = None
        if cif_dict is None:
            # No or erroneous info for this compound
            data_dict[component] = None
        else:
            try:
                data = str(cif_dict['type'])
            except ValueError:
                # Unparsable data, e.g. '?' as float
                data = None
            data_dict[component] = data
    
    # Create a set of all types in the database
    types = set(data_dict.values())

    # Create ist of all types for the relevant categories
    peptide_types = []
    carbohydrate_types = []
    nucleotide_types = []
    remainder_types = []

    for current_type in types:
        t = current_type.lower()
        if ('like' in t):
            remainder_types.append(current_type)
        elif ('peptide' in t) or ('amino' in t):
            peptide_types.append(current_type)
        elif ('rna' in t) or ('dna' in t):
            nucleotide_types.append(current_type)
        elif ('saccharide' in t):
            carbohydrate_types.append(current_type)
        else:
            remainder_types.append(current_type)

    # Print out the type values
    print()
    print('Ignoring the following types:')
    print(sorted(remainder_types))
    print()
    for l, t in zip(
        ('nucleotide', 'carbohydrate', 'peptide'), 
        (nucleotide_types, carbohydrate_types, peptide_types)
    ):
        print(f'Using the following types for group {l}:')
        print(sorted(t))
        print()

    # Create the relevant comprehensive lists
    comprehensive_nucleotide_list = []
    comprehensive_carbohydrate_list = []
    comprehensive_amino_acid_list = []

    for r, t in data_dict.items():
        
        if t in nucleotide_types:
            comprehensive_nucleotide_list.append(r)
        elif t in carbohydrate_types:
            comprehensive_carbohydrate_list.append(r)
        elif t in peptide_types:
            comprehensive_amino_acid_list.append(r)

    # Write the lists to json
    with open(join(json_path, 'nucleotides.json'), "w") as f:
        json.dump(comprehensive_nucleotide_list, f, indent=1)
    with open(join(json_path, 'carbohydrates.json'), "w") as f:
        json.dump(comprehensive_carbohydrate_list, f, indent=1)
    with open(join(json_path, 'amino_acids.json'), "w") as f:
        json.dump(comprehensive_amino_acid_list, f, indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create json files with all monomer residue ids that"
                    "belong to peptides, carbohydrates, and nucleotides. "
                    "The information is based on the '_chem_comp.type "
                    "property in a 'components.cif' file."
    )
    parser.add_argument(
        "infile",
        help="The path to the 'components.cif' file to be read."
    )
    parser.add_argument(
        "outfolder",
        help="The path to the folder, where the output Json files should "
             "be placed."
    )
    args = parser.parse_args()

    create_files(args.infile, args.outfolder)
