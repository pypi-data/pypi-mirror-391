from rdkit import Chem
from rdkit.Chem import rdChemReactions, AllChem
import pandas as pd
from typing import List

def canonicalize_smiles(smiles: str) -> str:
    return Chem.MolToSmiles(Chem.MolFromSmiles(smiles))

def are_isomorphic(mol1: Chem.rdchem.Mol,
                   mol2: Chem.rdchem.Mol,
                   consider_stereo: bool = False) -> bool:
    """
    Check if two molecules are isomorphic, i.e. their bond and atom arrangements are identical

    Parameters
    ----------
    mol1 : Chem.rdchem.Mol
        RDKit mol object of first molecule generated from its SMILES or SMARTS representation.
        If SMARTS were used in creating mol object, these need not be atom mapped.

    mol2 : Chem.rdchem.Mol
        RDKit mol object of second molecule generated from its SMILES or SMARTS representation.
        If SMARTS were used in creating mol object, these need not be atom mapped.

    consider_stereo: bool
        Whether to consider stereochemistry or not when comparing two molecules.

    Returns
    -------
    is_isomorphic : bool
        True if both molecules are isomorphic, False otherwise.
    """

    if consider_stereo:
        is_isomorphic = mol1.HasSubstructMatch(mol2, useChirality = True) and mol2.HasSubstructMatch(mol1, useChirality = True)
    else:
        is_isomorphic = mol1.HasSubstructMatch(mol2) and mol2.HasSubstructMatch(mol1)

    return is_isomorphic

def is_cofactor(mol: Chem.rdchem.Mol,
                cofactors_list: list,
                consider_stereo: bool = False) -> bool:
    """
    Checks if a given query molecule is equivalent to a cofactor.
    A list of predetermined cofactors needs to be passed into this function.

    Parameters
    ----------
    mol : Chem.rdchem.Mol
        RDKit mol object of query molecule generated from its SMILES or SMARTS representation.
        If SMARTS were used in creating mol object, these need not be atom mapped.
    cofactors_list : list
        List of SMILES strings representing cofactors.
    consider_stereo: bool
        Whether to consider stereochemistry or not when comparing two molecules.

    Returns
    -------
    bool
        True if the input query mol is isomorphic to any cofactor in the list, False otherwise.
    """
    for cofactor in cofactors_list:
        if are_isomorphic(mol1 = mol,
                          mol2 = Chem.MolFromSmiles(cofactor),
                          consider_stereo = consider_stereo):
            return True

    return False

def remove_stereo(mol: Chem.rdchem.Mol) -> Chem.rdchem.Mol:
    """
    Remove stereochemistry from a molecule.

    Parameters
    ----------
    mol : Chem.rdchem.Mol
        RDKit mol object of query molecule generated from its SMILES or SMARTS representation with stereochemistry.

    Returns
    -------
    mol : Chem.rdchem.Mol
        RDKit mol object of input molecule without stereochemistry.
    """
    Chem.RemoveStereochemistry(mol)
    return mol

def remove_stereo_frm_rxn(reaction_SMARTS: str) -> str:
    """
    Remove stereochemistry from a reaction SMARTS.

    Parameters
    ----------
    reaction_SMARTS : str
        Fully atom-mapped SMARTS string for a given input reaction with potentially chiral species.

    Returns
    -------
    no_stereo_reaction_SMARTS : str
        Fully atom-mapped SMARTS string but stereochemistry information is remove for any participating chiral species.
    """
    reaction = rdChemReactions.ReactionFromSmarts(reaction_SMARTS)
    if reaction is None:
        raise ValueError("Invalid reaction SMARTS string!")

    # process reactants, products, and agents
    reactants = [remove_stereo(mol) for mol in reaction.GetReactants()]
    products = [remove_stereo(mol) for mol in reaction.GetProducts()]
    agents = [remove_stereo(mol) for mol in reaction.GetAgents()]

    # reconstruct the reaction SMARTS
    reactant_smarts = '.'.join([Chem.MolToSmiles(mol) for mol in reactants])
    product_smarts = '.'.join([Chem.MolToSmiles(mol) for mol in products])
    agent_smarts = '.'.join([Chem.MolToSmiles(mol) for mol in agents])

    # Combine into a single reaction SMARTS string
    if agent_smarts:
        no_stereo_reaction_SMARTS = f"{reactant_smarts}.{agent_smarts}>>{product_smarts}"
    else:
        no_stereo_reaction_SMARTS = f"{reactant_smarts}>>{product_smarts}"

    return no_stereo_reaction_SMARTS

def reset_atom_map(SMARTS: str,
                   starting_atom_num: int = 1) -> str:
    """
    Reset the numbering of an extracted reaction template.
    Resetting atom maps of extracted templates can help duplicate duplicates.

    Parameters
    ----------
    SMARTS: str
        Fully-atom mapped SMARTS string of an input molecule, complete with stereochemistry

    starting_atom_num: int
        Starting atom number for the new atom mapping
    """

    # convert the input molecule's SMARTS to an RDKit mol object
    mol = Chem.MolFromSmarts(SMARTS)
    if not mol:
        raise ValueError("Invalid SMARTS string!")

    # map the existing atom indices to new atom map numbers starting from 1
    new_atom_map = {atom.GetIdx(): starting_atom_num + i for i, atom in enumerate(mol.GetAtoms())}

    # update the existing atom map numbers in the current molecule
    for atom in mol.GetAtoms():
        if atom.HasProp('molAtomMapNumber'):
            atom.SetProp('molAtomMapNumber', str(new_atom_map[atom.GetIdx()]))

    # convert the RDKit mol object back to SMARTS once new atom map numbers have been set
    SMARTS_with_new_atom_mapping = Chem.MolToSmarts(mol)
    return SMARTS_with_new_atom_mapping

def get_cofactor_CoF_code(query_SMILES: str,
                          cofactors_df: pd.DataFrame) -> str:

    num_rows = cofactors_df.shape[0]

    for i in range(num_rows):
        if are_isomorphic(mol1 = Chem.MolFromSmiles(query_SMILES),
                          mol2 = Chem.MolFromSmiles(cofactors_df.iloc[i,:]["SMILES"]),
                          consider_stereo = False):

            CoF_code = cofactors_df.iloc[i,:]["#ID"]

            return CoF_code

def are_rxn_descriptors_equal(rxn_descriptor_01: List[str],
                              rxn_descriptor_02: List[str]) -> bool:

    return sorted(rxn_descriptor_01) == sorted(rxn_descriptor_02)


def neutralize_atoms(smiles: str) -> str:
    """
    http://www.rdkit.org/docs/Cookbook.html#neutralizing-charged-molecules
    """
    mol = Chem.MolFromSmiles(smiles)
    pattern = Chem.MolFromSmarts("[+1!h0!$([*]~[-1,-2,-3,-4]),-1!$([*]~[+1,+2,+3,+4])]")
    at_matches = mol.GetSubstructMatches(pattern)
    at_matches_list = [y[0] for y in at_matches]
    if len(at_matches_list) > 0:
        for at_idx in at_matches_list:
            atom = mol.GetAtomWithIdx(at_idx)
            chg = atom.GetFormalCharge()
            hcount = atom.GetTotalNumHs()
            atom.SetFormalCharge(0)
            atom.SetNumExplicitHs(hcount - chg)
            atom.UpdatePropertyCache()

    return Chem.MolToSmiles(mol)

def does_template_fit(rxn_str: str,
                      rxn_template: str) -> bool:

    rxn = AllChem.ReactionFromSmarts(rxn_template)

    # extract reactants and products from the input reaction string and remove any hydrogens present
    reactants_list = rxn_str.split(">>")[0].split(".") # index 0 for reactants on LHS
    products_list = rxn_str.split(">>")[1].split(".") # index 1 for products on RHS

    reactant_templates = rxn_template.split(">>")[0].split(".")
    product_templates = rxn_template.split(">>")[1].split(".")

    if '[H+]' in reactants_list:
        reactants_list.remove('[H+]')

    if '[H+]' in products_list:
        products_list.remove('[H+]')

    ### first, we check if the reactant patterns within the template match the reactants present in the input reaction
    # note here that the order in which reactants appear in a template must match their order in the input reaction
    num_reactant_template_matches = 0
    for i in range(0, len(reactants_list)):
        reactant_smiles = reactants_list[i]
        reactant_mol = Chem.MolFromSmiles(reactant_smiles)
        reactant_template_smarts = reactant_templates[i]
        reactant_template_mol = Chem.MolFromSmarts(reactant_template_smarts)
        if reactant_mol.HasSubstructMatch(reactant_template_mol):
            num_reactant_template_matches += 1

    # the number of reactant templates must exactly match the number of reactants present
    if num_reactant_template_matches == len(reactants_list):
        pass
    else:
        # if number of reactant templates does not exactly match number of reactants present, then template does not fit
        return False

    ### second, run the chemical reaction prescribed by the input reaction template
    # initialize an empty tuple to store mol objects of reactants
    reactant_mols = []

    for reactant_smiles in reactants_list:
        reactant_mols.append(Chem.MolFromSmiles(reactant_smiles))

    # convert the list into a tuple to use RDKit's rxn.RunReactants method
    reactants_tuple = tuple(reactant_mols)

    ### lastly, check if the products generated from running the chemical reaction match the template
    rxn_outcomes = rxn.RunReactants(reactants_tuple)

    # initialize a counter for the number of successful reaction outcomes since multiple pairs of products can form
    # for a template to successfully fit, at least one reaction outcome must be successful
    for rxn_outcome in rxn_outcomes:

        # within each reaction outcome, initialize a counter to count the number of successful products
        num_product_template_matches = 0
        for product_formed in rxn_outcome:
            for product_smiles in products_list:
                if are_isomorphic(mol1 = Chem.MolFromSmiles(product_smiles),
                                  mol2 = product_formed,
                                  consider_stereo = False):

                    num_product_template_matches += 1

        if num_product_template_matches == len(products_list):
            return True
        else:
            pass