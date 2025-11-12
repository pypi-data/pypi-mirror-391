from torchpme.tuning import tune_ewald, tune_pme, tune_p3m
import torchpme
import torch
from torchpme.prefactors import eV_A

class CoulombCalculator:
    """
    Coulomb Calculator
    """
    
    def __init__(self, 
                 method: str,
                 cutoff: float,
                 accuracy: float,
                 device: str,
                 dtype: torch.dtype,
                 ):

        self._method = method.lower()
        self._cutoff = cutoff
        self._accuracy = accuracy
        self._device = device
        self._dtype = dtype

        # 验证方法
        valid_methods = ['direct', 'ewald', 'pme', 'p3m']
        if self._method not in valid_methods:
            raise ValueError(f"Unsupported method: {self._method}. Valid methods: {valid_methods}")

        # 通用参数
        self._neighbor_indices, self._neighbor_distances = None, None
        self._positions = None
        self._cell = None
        self._charges = None
        
        #结果
        self._energy = None
        self._energies = None
        # self.forces = None
    
    def get_coul_energy(self, 
                        neighbor_indices: torch.Tensor, 
                        neighbor_distances: torch.Tensor,
                        positions: torch.Tensor,
                        cell: torch.Tensor,
                        charges: torch.Tensor,
                        ) -> float:
    
        self._positions = positions
        self._cell = cell
        self._charges = charges

        self._neighbor_indices, self._neighbor_distances = neighbor_indices, neighbor_distances
        
        if self._method == 'direct':
            self._direct_coulomb()
        else:
            self._long_range_coulomb()
  
        return self._energy, self._energies
    
    def _optimize_params(self):
        if self._method == 'ewald':
            return tune_ewald(
                charges=self._charges,
                cell=self._cell,
                positions=self._positions,
                cutoff=self._cutoff,
                accuracy=self._accuracy,
                neighbor_indices=self._neighbor_indices,
                neighbor_distances=self._neighbor_distances,
            )
        elif self.method == 'pme':
            return tune_pme(
                charges=self._charges,
                cell=self._cell,
                positions=self._positions,
                cutoff=self._cutoff,
                accuracy=self._accuracy,
                neighbor_indices=self._neighbor_indices,
                neighbor_distances=self._neighbor_distances,
            )
        elif self.method == 'p3m':
            return tune_p3m(
                charges=self._charges,
                cell=self._cell,
                positions=self._positions,
                cutoff=self._cutoff,
                accuracy=self._accuracy,
                neighbor_indices=self._neighbor_indices,
                neighbor_distances=self._neighbor_distances,
            )
 
    def _long_range_coulomb(self) -> float:
        """长程库伦相互作用计算"""
        smearing, params, _ = self._optimize_params()
        prefactor = eV_A
        if self._method == 'ewald':
            base_calc = torchpme.EwaldCalculator(
                potential=torchpme.CoulombPotential(smearing),
                **params,
                prefactor=prefactor
            )
        elif self._method == 'pme':
            base_calc = torchpme.PMECalculator(
                potential=torchpme.CoulombPotential(smearing),
                **params,
                prefactor=prefactor
            )
        elif self._method == 'p3m':
            base_calc = torchpme.P3MCalculator(
                potential=torchpme.CoulombPotential(smearing),
                **params,
                prefactor=prefactor
            )

        calculator = base_calc
        calculator.to(device=self._device, dtype=self._dtype)
        potentials = calculator.forward(
            self._charges, self._cell, self._positions, self._neighbor_indices, self._neighbor_distances
        )
        energies = self._charges * potentials
        energy = torch.sum(energies)
        # energy.backward()
        # forces = -self._positions.grad
        
        
        self._energy = energy.item()
        self._energies = energies
        # self.forces = forces
    
    def _direct_coulomb(self):
        COULOMB_CONSTANT = 14.399644853  # eV·Å/e²
        qi = self._charges[self._neighbor_indices[:, 0]].flatten()
        qj = self._charges[self._neighbor_indices[:, 1]].flatten()
        rij = self._neighbor_distances.flatten()
        # 避免除零
        mask = rij > 1e-12
        if not torch.all(mask):
            qi = qi[mask]; qj = qj[mask]; rij = rij[mask]
        pair_energy = (COULOMB_CONSTANT * qi * qj / rij)
        
        # === 计算 per-atom energy ===
        n_atoms = self._charges.shape[0]
        energies = torch.zeros(n_atoms, device=self._device, dtype=self._dtype)
        i_idx = self._neighbor_indices[:, 0][mask]
        j_idx = self._neighbor_indices[:, 1][mask]
        energies.index_add_(0, i_idx, 0.5 * pair_energy)
        energies.index_add_(0, j_idx, 0.5 * pair_energy)

        # 系统总能量（所有 pair 的总和）
        energy = pair_energy.sum().item()
        
        self._energy = energy
        self._energies = energies
