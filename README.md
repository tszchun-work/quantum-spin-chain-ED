# Exact Diagonalization of Quantum Spin Systems
This repository contains a set of codes that I coded with the assistance of AI for learning quantum spin systems, particularly the 1D spin system (a.k.a. spin chains).
We write the Hamiltonian of spin chains as sparse matrix with csr format, and carry out exact diagonalize with Lanzcos algorithm using SciPy. Since we only need small L to
observe the core physical properties of the ground state, we did not push it further with say, symmetry constraints. One can diagonalize the Ising chain, Heisenberg chain and
AKLT chain up to around L = 14 rather easily with these codes.
