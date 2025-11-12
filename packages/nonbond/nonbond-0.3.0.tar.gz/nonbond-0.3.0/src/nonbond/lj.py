
import torch


class LJCalculator:
    def __init__(self, 
                 cutoff: float,
                 device: str,
                 dtype: torch.dtype
                 ):
        self._cutoff = cutoff
        self._device = device
        self._dtype = dtype

    def get_lj_energy(self, neighbor_indices, neighbor_distances, epsilon, sigma):

        if neighbor_indices.numel() == 0:
            return 0.0
        
        sigma_t = torch.as_tensor(sigma, device=self._device, dtype=self._dtype)
        eps_t = torch.as_tensor(epsilon, device=self._device, dtype=self._dtype)

        i_idx = neighbor_indices[:, 0].to(device=self._device)
        j_idx = neighbor_indices[:, 1].to(device=self._device)
        r = neighbor_distances.to(device=self._device, dtype=self._dtype)
        
        sigma_ij = 0.5 * (sigma_t[i_idx] + sigma_t[j_idx])           
        epsilon_ij = torch.sqrt(eps_t[i_idx] * eps_t[j_idx])         

        # (sigma/r)^n 
        inv_r = sigma_ij / r          # (sigma_ij / r)
        inv_r2 = inv_r * inv_r
        inv_r6 = inv_r2 * inv_r2 * inv_r2
        inv_r12 = inv_r6 * inv_r6
        
        pair_energy = 4.0 * epsilon_ij * (inv_r12 - inv_r6)  # (n_pairs,)

        # === 计算 per-atom energy ===
        n_atoms = sigma_t.shape[0]
        energies = torch.zeros(n_atoms, device=self._device, dtype=self._dtype)
        energies.index_add_(0, i_idx, 0.5 * pair_energy)
        energies.index_add_(0, j_idx, 0.5 * pair_energy)

        energy = energies.sum().item()

        return energy, energies
