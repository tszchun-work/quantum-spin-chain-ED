# Spin Chain Exact Diagonalization: TFIM, AFH, and AKLT Models

A collection of computational notebooks written in python designed for exact diagonalization (ED) studies of one-dimensional quantum spin chains. This repository focuses on numerical analysis of ground state properties, phase transitions, order parameters, and topological features across three benchmark quantum spin systems:

1. **Transverse Field Ising Model (TFIM)** – Quantum phase transitions and symmetry breaking.

2. **Antiferromagnetic Heisenberg (AFH) Model**

3. **Affleck-Kennedy-Lieb-Tasaki (AKLT) Model** – Symmetry-Protected Topological (SPT) phases and valence-bond solid (VBS) ground states.

## 📌 Features

* **Full Exact Diagonalization (ED):** Construct and diagonalize sparse Hamiltonian matrices for small-to-medium chain sizes ($N \leq 14$).

* **Ground State Analysis:**

  * Energy density and finite-size scaling.

  * Energy gap $\Delta E = E_1 - E_0$ and quantum critical behavior.

  * Two-point spin-spin correlation functions $\langle S_i^z S_j^z \rangle$ and $\langle S_i^+ S_j^- \rangle$.

* **Topological Order Parameters:**

  * String order parameter $O_{\text{string}}^\alpha(i, j)$ for identifying Haldane/SPT order.

  * Degeneracy structure of the entanglement spectrum.
 
  * Effective S=1/2 edge spin

## 🔬 Models Overview

### 1. Transverse Field Ising Model (TFIM)

$$
H_{\text{TFIM}} = -J \sum_{i=1}^{N} \sigma_i^z \sigma_{i+1}^z - h \sum_{i=1}^{N} \sigma_i^x - g \sum_{i=1}^{N} \sigma_i^z
$$

* **Spin:** $S = 1/2$

* **Physics:** Demonstrates a quantum phase transition at $h/J = 1$ separating a ferromagnetic phase ($\mathbb{Z}_2$ symmetry broken) from a paramagnetic phase.

### 2. Antiferromagnetic Heisenberg (AFH) Model

$$
H_{\text{AFH}} = J \sum_{i=1}^{N} \vec{S}_i \cdot \vec{S}_{i+1} \quad (J > 0)
$$

* **Spin:** $S = 1/2$ and $S = 1$

* **Physics:**

  * $S=1/2$: Critical gapless state governed by $SU(2)_1$ Wess-Zumino-Witten CFT.

  * $S=1$: Gapped Haldane phase (likely) featuring topological edge states under open boundary conditions (OBC).

### 3. AKLT Model

$$
H_{\text{AKLT}} = \sum_{i=1}^{N} \left[ \frac{1}{3} + \frac{1}{2} \vec{S}_i \cdot \vec{S}_{i+1} + \frac{1}{6} (\vec{S}_i \cdot \vec{S}_{i+1})^2 \right]
$$

* **Spin:** $S = 1$

* **Physics:** An exactly solvable point in the Haldane phase whose ground state is a Valence-Bond Solid (VBS). Displays non-zero string order parameter and fourfold ground state degeneracy under OBC.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
