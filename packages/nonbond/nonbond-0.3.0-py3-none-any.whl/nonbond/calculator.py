import numpy as np
from ase.calculators.calculator import Calculator, all_changes
from ase.units import mol, kcal, eV

import torch
from vesin.torch import NeighborList

from .lj import LJCalculator
from .coul import CoulombCalculator


class Nonbond(Calculator):
    """
    ASE Calculator for Lennard-Jones + Coulomb interactions

    The total potential energy is:
    E_total = E_LJ + E_coulomb

    Where:
    E_LJ = sum_i<j 4*epsilon_ij * [(sigma_ij/r_ij)^12 - (sigma_ij/r_ij)^6]
    E_coulomb = sum_i<j k * q_i * q_j / r_ij

    Mixing rules (Lorentz-Berthelot):
    epsilon_ij = sqrt(epsilon_i * epsilon_j)
    sigma_ij = (sigma_i + sigma_j) / 2

    Parameters:
    -----------
    sigma : dict
        LJ sigma parameters by atom type (Å)
        Format: {'H': 2.51, 'O': 3.12}

    epsilon : dict  
        LJ epsilon parameters by atom type (kcal/mol)
        Format: {'H': 0.044, 'O': 0.126}

    cutoff : float, optional
        Cutoff distance for both LJ and Coulomb interactions (Å)
        Default: 3 * max(sigma) or 10.0 Å

    coul_method : str, optional
        Method for Coulomb interaction calculation ('direct', 'ewald', 'pme', 'p3m')
        Default: None

    accuracy : float, optional
        Accuracy for Long-Range Coulomb Interaction
        Default: 1e-5

    device : str, optional
        Device for calculations ('cpu' or 'cuda')
        Default: 'cpu'
    """

    implemented_properties = [
        "energy",
        "energies",
    ]

    def __init__(
        self,
        epsilon: dict,
        sigma: dict,
        cutoff: float = 10.0,
        coul_method: str = None,
        accuracy: float = 1e-5,
        device: str = 'cpu',
    ):

        kwargs = {
            'epsilon': epsilon,
            'sigma': sigma,
            'cutoff': cutoff,
            'coul_method': coul_method,
            'accuracy': accuracy,
            'device': device,
            'dtype': torch.float64,
        }
        Calculator.__init__(self, **kwargs)

        # Initialize neighbor lists
        self._neighbor_indices, self._neighbor_distances = None, None

        # Cache for parameters
        self._atom_types = None
        self._sigmas = None
        self._epsilons = None
        self._charges = None
        self._atoms = None
        self._positions = None
        self._cell = None

    def calculate(self,
                  atoms=None,
                  properties=None,
                  system_changes=all_changes):
        """Calculate energy"""

        if properties is None:
            properties = self.implemented_properties

        Calculator.calculate(self, atoms, properties, system_changes)
        
        self._atoms = atoms
        self._update_parameters()
        self._update_neighbor_list()
        
        if self._neighbor_indices.numel() == 0:
            energy, energies = 0.0, np.zeros(len(self._atoms))
        else:
            energy, energies = self._calculate_energy()
            if isinstance(energy, torch.Tensor):
                energy = energy.item()
            if isinstance(energies, torch.Tensor):
                energies = energies.detach().cpu().numpy()    
        self.results['energy'] = energy
        self.results['energies'] = energies

    # 构建邻接列表
    def _update_neighbor_list(self):
        nl = NeighborList(cutoff=self.parameters.cutoff, full_list=False)
        self._neighbor_indices, self._neighbor_distances = nl.compute(
            points=self._positions,
            box=self._cell,
            periodic=True,
            quantities="Pd")
        
        if self._neighbor_indices.numel() == 0:
            return 

        # if cutoff exceeds half box length, remove duplicate periodic pairs
        box_lengths = self._cell.diagonal()
        if torch.any(self.parameters.cutoff > 0.5 * box_lengths):
            combined = torch.cat([self._neighbor_indices, self._neighbor_distances.reshape(-1, 1)], dim=1).detach().numpy()
            sort_idx = np.lexsort((combined[:, 2], combined[:, 1], combined[:, 0]))
            combined = combined[sort_idx]
            
            diff = np.diff(combined[:, :2], axis=0)
            is_unique = np.any(diff != 0, axis=1)
            keep_mask = np.concatenate(([True], is_unique)) 

            filtered = combined[keep_mask]

            self._neighbor_indices = torch.as_tensor(filtered[:, :2], dtype=torch.long, device=self.parameters.device)
            self._neighbor_distances = torch.as_tensor(filtered[:, 2], dtype=self.parameters.dtype, device=self.parameters.device)
        
        
    def _calculate_energy(self):

        energy = 0.0
        energy_lj = 0.0
        energy_coulomb = 0.0
        
        # Calculate LJ interactions (always calculated)
        lj_calc = LJCalculator(cutoff=self.parameters.cutoff,
                               device=self.parameters.device,
                               dtype=self.parameters.dtype)
        energy_lj, energies_lj = lj_calc.get_lj_energy(self._neighbor_indices,
                                                       self._neighbor_distances,
                                                       self._epsilons, 
                                                       self._sigmas)
        
        # Calculate Coulomb interactions (if charges are provided)
        if self.parameters.coul_method is not None and torch.all(self._charges != 0.0):
            coulomb_calc = CoulombCalculator(
                method=self.parameters.coul_method,
                cutoff=self.parameters.cutoff,
                accuracy=self.parameters.accuracy,
                device=self.parameters.device,
                dtype=self.parameters.dtype)
            energy_coulomb, energies_coulomb = coulomb_calc.get_coul_energy(
                self._neighbor_indices, self._neighbor_distances, self._positions, self._cell, self._charges)
        else:
            energy_coulomb = 0.0
            energies_coulomb = torch.zeros_like(energies_lj)
        energies_lj = energies_lj.reshape(-1)
        energies_coulomb = energies_coulomb.reshape(-1)
        

        energy = energy_lj + energy_coulomb
        energies = energies_lj + energies_coulomb
        
        return energy, energies

    def _update_parameters(self):
        """Update cached parameters for current system"""

        # atom types
        try:
            self._atom_types = self._atoms.get_array('type')
        except KeyError:
            self._atom_types = self._atoms.get_chemical_symbols()

        # Convert energy units from kcal/mol to eV
        convert_factor = kcal / mol / eV
        atom_types = self._atom_types
        self._sigmas = np.array(
            [self.parameters.sigma[atom_type] for atom_type in atom_types])
        self._epsilons = np.array([
            self.parameters.epsilon[atom_type] * convert_factor
            for atom_type in atom_types
        ])

        dtype = self.parameters.dtype
        device = self.parameters.device
        self._positions = torch.tensor(self._atoms.positions,
                                      dtype=dtype,
                                      device=device,
                                      requires_grad=True)
        self._cell = torch.tensor(self._atoms.cell.array,
                                 dtype=dtype,
                                 device=device)
        self._charges = torch.tensor(
            self._atoms.get_initial_charges(), dtype=dtype, device=device).unsqueeze(1)
