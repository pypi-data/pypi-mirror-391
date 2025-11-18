# RxnTools

RxnTools is a lightweight collection of RDKit-powered utilities for reaction-centric cheminformatics workflows. It grew out of template-extraction notebooks and now bundles reusable helpers for:

- parsing unmapped reaction strings, filtering cofactors, and building reaction descriptors
- tracing atom-mapped changes and extracting environment-specific SMARTS templates
- enumerating products from SMARTS templates (including optional stereochemical filters)
- visualising molecules or highlighting substructures inside Jupyter notebooks

Whether you are curating reaction datasets, prototyping retrosynthesis heuristics, or inspecting stereochemical templates, RxnTools provides the glue code built on top of RDKit so you do not have to rewrite it from scratch.

## Installation

### From PyPI (recommended)
```bash
pip install rxntools-kit
```

> **Note:** RxnTools targets Python 3.10. You must install an RDKit build that matches your platform; conda-forge is the most reliable source (`conda install -c conda-forge rdkit`).

### From source with Poetry
```bash
git clone https://github.com/<your-handle>/RxnTools.git
cd RxnTools
poetry env use /path/to/python3.10
poetry install
```

## Quickstart

```python
from rxntools.reaction import unmapped_reaction

# Provide a minimal cofactor list so helpers can filter them out
cofactors = ["O=C=O"]   # typically loaded from data/raw/cofactors.json

rxn = unmapped_reaction("CCO + O=C=O >> CC(=O)O + O")
substrates = rxn.get_substrates(cofactors_list=cofactors, consider_stereo=False)
products = rxn.get_products(cofactors_list=cofactors, consider_stereo=False)

print(substrates)  # ['CCO']
print(products)    # ['CC(=O)O', 'O']
```

Need to inspect transformed atoms? Switch to `rxntools.reaction.mapped_reaction`:

```python
from rxntools.reaction import mapped_reaction

rxn_smarts = "[CH3:1][CH2:2][OH:3].[C:4](=[O:5])=[O:6]>>[CH3:1][CH:2](=[O:5])[OH:3].[OH2:7]"
mr = mapped_reaction(rxn_smarts, include_stereo=True)
changed_atoms, broken_bonds, formed_bonds = mr.get_all_changed_atoms()
```

For template extraction, pass the mapped substrate SMARTS plus atom indices to `mapped_reaction.get_template_around_rxn_site`.

## Data Files

Two reference files ship with the source distribution and can be redistributed with your projects:

- `data/raw/all_cofactors.csv`
- `data/raw/cofactors.json`

Larger third-party datasets (e.g., `enzymemap*`) remain in the repository but are excluded from the published wheel to respect their original licenses. If you rely on them, keep a clone of the repository or source the datasets separately.

## Running Tests

```bash
poetry install --with dev  # ensure pytest and optional tooling are installed
poetry run pytest
```

## Contributing

Issues and pull requests are welcome. If you plan significant changes:

1. Fork the repository and create a topic branch.
2. Add or update tests that cover the new behaviour.
3. Run `poetry run pytest` before opening a PR.

## License

RxnTools is released under the [MIT License](LICENSE).
