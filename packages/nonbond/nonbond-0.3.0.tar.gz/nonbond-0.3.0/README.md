# Nonbond

**Nonbond** is an [ASE (Atomic Simulation Environment)](https://ase-lib.org/) calculator designed for computing **non-bonded interactions**, including the 12-6 Lennard–Jones (LJ) and Coulomb potentials.  
It currently outputs only the **total potential energy** and **per-atom energies**.  
(*Note: Force and stress calculations are not yet implemented.*)

# Requirements
  
- ASE
- torch-pme
- vesin-torch 

# Installation

Install via **pip**:

```bash
conda create -n nonbond python=3.13
conda activate nonbond
pip install nonbond
```

# Example

```python
from ase import Atoms
from nonbond import Nonbond
import numpy as np

# Define Lennard-Jones parameters for SPC/E water
# Unit: kcal/mol
epsilon = {
    'Ow': 0.15535,
    'Hw': 0.0,
}

# Unit: Å
sigma = {
    'Ow': 3.16600,
    'Hw': 1.0,
}

# Calculator
calc = Nonbond(
    epsilon=epsilon,
    sigma=sigma,
    cutoff=14.0,  # Unit: Å, cutoff radius for LJ and Coulomb interactions
    coul_method='ewald',  # Options: 'direct', 'ewald', 'pme', 'p3m'
    accuracy=1e-5,  # Accuracy for long-range Coulomb interactions
    device='cpu', # Options: 'cuda'
)

# SPC/E water molecule
atoms = Atoms(
    'OH2',
    positions=[
        [0.00000, -0.06461, 0.00000],
        [0.81649,  0.51275, 0.00000],
        [-0.81649, 0.51275, 0.00000]
    ],
    cell=[40.0, 40.0, 40.0],
    pbc=True
)

# Assign atom types and charges
atoms.set_array('type', np.array(['Ow', 'Hw', 'Hw']))
atoms.set_initial_charges([-0.8476, 0.4238, 0.4238])

# Attach calculator and compute energy
atoms.calc = calc
energy = atoms.get_potential_energy()
print(f"Potential energy: {energy:.6f} eV")
```
---







