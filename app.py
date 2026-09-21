import streamlit as st
import matplotlib.pyplot as plt
from math import pi
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler
from qiskit_aer import AerSimulator
from qiskit.visualization import (
    plot_bloch_multivector, plot_state_qsphere, plot_histogram
)

# Set up page configurations
st.set_page_config(page_title="Quantum Circuit Designer", layout="wide")

# ==================== HELPERS & SIMULATIONS ====================
def simulate_ideal(circuit, shots=1024, seed=7):
    """
    Inspects the pure state and samples the circuit using StatevectorSampler.
    """
    non_measured_qc = circuit.remove_final_measurements(inplace=False)
    # 1. Inspect the pure state before measurement.
    state = Statevector.from_instruction(non_measured_qc)

    # 2. Sample a measured copy; keep the original unitary circuit intact.
    measured = circuit.copy()
    
    # Only add measure_all if no classical bits or registers already exist
    if measured.num_clbits == 0:
        measured.measure_all()
        
    sampler = StatevectorSampler(seed=seed)
    pub_result = sampler.run([measured], shots=shots).result()[0]
    
    # Retrieve the bitstring data safely from classical register names
    # measure_all creates a register named 'meas'
    if 'meas' in pub_result.data:
        counts = pub_result.data.meas.get_counts()
    else:
        # Fallback for manually added registers
        counts = pub_result.data.c.get_counts() if 'c' in pub_result.data else {}
        
    return state, counts

# ==================== UI CORE IMPLEMENTATION ====================
st.title("⚛️ Interactive Quantum Circuit Designer & Analyzer")

# Sidebar for circuit configuration
st.sidebar.header("Circuit Parameters")
num_qubits = st.sidebar.slider("Number of Qubits", 1, 5, 2)
circuit_type = st.sidebar.selectbox("Preset Circuit", ["Bell State", "GHZ State", "Custom"])

# Initialize Circuit based on presets
if circuit_type == "Custom":
    # Custom configuration can either use explicit classical bits or automatic measuring
    qc = QuantumCircuit(num_qubits)
else:
    qc = QuantumCircuit(num_qubits, num_qubits)

# Apply Presets or Custom Configurations
if circuit_type == "Bell State" and num_qubits >= 2:
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(range(2), range(2))
elif circuit_type == "GHZ State" and num_qubits >= 3:
    qc.h(0)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure(range(num_qubits), range(num_qubits))
elif circuit_type == "Custom":
    st.sidebar.info("Configure custom gates below:")
    gate = st.sidebar.selectbox("Add Gate", ["H", "X", "CX", "Measure"])
    target = st.sidebar.slider("Target Qubit", 0, num_qubits - 1, 0)
    
    if gate == "H":
        qc.h(target)
    elif gate == "X":
        qc.x(target)
    elif gate == "CX":
        if num_qubits > 1:
            # Control qubit defaults to 0 unless the target is 0, then defaults to 1
            control = 0 if target != 0 else 1
            qc.cx(control, target)
        else:
            st.sidebar.warning("CX gate requires at least 2 qubits.")
    elif gate == "Measure":
        # Add a classical bit to hold custom measurement if not already generated
        if qc.num_clbits == 0:
            qc.add_register(QuantumCircuit(num_qubits, num_qubits).cregs[0])
        qc.measure(target, target)
else:
    st.sidebar.warning(f"{circuit_type} requires more qubits than currently selected.")

# Display Circuit Diagram
st.subheader("Circuit Diagram")
fig_circuit, ax = plt.subplots()
qc.draw(output='mpl', ax=ax)
st.pyplot(fig_circuit)

# Execution Section
st.subheader("Execution & Noisy Simulation Comparison")
backend_choice = st.selectbox("Select Backend", ["Ideal Simulator", "Noisy Aer Simulator", "IBM Quantum Hardware (Token Required)"])

if st.button("Run Simulation"):
    # Create a temporary copy to protect the drawing UI state from unwanted measurements
    run_circuit = qc.copy()
    
    # Fallback checking: ensure the circuit contains measurement mappings
    if run_circuit.num_clbits == 0:
        run_circuit.measure_all()
        
    if backend_choice == "Ideal Simulator":
        # Process through our standalone StatevectorSampler utility function
        state, counts = simulate_ideal(qc)
        
        # Display the pure state vector data matrices for mathematical analysis
        st.write("### Pure State Vector Matrix Output")
        st.code(state.data)
    else:
        # Standard Aer Local Execution
        simulator = AerSimulator()
        job = simulator.run(run_circuit, shots=1024)
        result = job.result()
        counts = result.get_counts()
    
    # Display the final execution histogram plots
    st.write("### Result Plots")
    fig_hist, ax_hist = plt.subplots()
    plot_histogram(counts, ax=ax_hist)
    st.pyplot(fig_hist)
    st.success("Execution completed successfully!")
