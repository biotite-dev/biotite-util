import argparse
import msgpack
import biotite.structure as struc
import biotite.structure.io.pdbx as pdbx


BOND_ORDERS = {
    ("SING", "N") : struc.BondType.SINGLE,
    ("DOUB", "N") : struc.BondType.DOUBLE,
    ("TRIP", "N") : struc.BondType.TRIPLE,
    ("QUAD", "N") : struc.BondType.QUADRUPLE,
    ("SING", "Y") : struc.BondType.AROMATIC_SINGLE,
    ("DOUB", "Y") : struc.BondType.AROMATIC_DOUBLE,
    ("TRIP", "Y") : struc.BondType.AROMATIC_TRIPLE,
}


def create_bond_dict(components_pdbx_file_path, msgpack_file_path):
    pdbx_file = pdbx.PDBxFile()
    pdbx_file.read(components_pdbx_file_path)
    components = pdbx_file.get_block_names()
    bond_dict = {}
    for i, component in enumerate(components):
        print(f"{component:3}   {int(i/len(components)*100):>3d}%", end="\r")
        cif_bonds = pdbx_file.get_category(
            "chem_comp_bond", block=component, expect_looped=True
        )
        if cif_bonds is None:
            # No bond info for this compound
            continue
        else:
            group_bonds = {}
            for atom1, atom2, order, aromatic_flag in zip(
                cif_bonds["atom_id_1"], cif_bonds["atom_id_2"],
                cif_bonds["value_order"], cif_bonds["pdbx_aromatic_flag"]
            ):
                bond_type = BOND_ORDERS[order, aromatic_flag]
                group_bonds[(atom1, atom2)] = bond_type
        bond_dict[component] = group_bonds
    with open(msgpack_file_path, "wb") as msgpack_file:
        msgpack.dump(bond_dict, msgpack_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a dataset, that contains the information which "
                    "atoms are connected in a given residue. "
                    "The information is based on a 'components.cif' file."
    )
    parser.add_argument(
        "infile",
        help="The path to the 'components.cif' file to be read."
    )
    parser.add_argument(
        "outfile",
        help="The path to the file, where the output MessagePack file should "
             "be placed."
    )
    args = parser.parse_args()

    create_bond_dict(args.infile, args.outfile)