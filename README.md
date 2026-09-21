# Quantum Circuit Designer & Hardware Comparison Tool

An interactive web application built with Streamlit and Qiskit to design quantum circuits, execute them via noisy simulators or real IBM Quantum hardware, and automatically generate comparison plots and editable reports.

## Features
- **Interactive Circuit Designer:** Construct custom multi-qubit quantum circuits visually.
- **Hardware vs. Simulation:** Compare ideal statevector results, noisy simulation results (using IBM Aer noise models), and real backend execution.
- **Automated Testing:** Run built-in unit tests to validate circuit logic and measurement stability.
- **Reporting & Demo:** Export structured experiment reports and follow the presentation script for demonstration.

## Quick Start
1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt