from dataclasses import dataclass
from typing import override, Literal

from quark.core import Core, Data, Result
from quark.interface_types import Circuit, Other

from qiskit.quantum_info import SparsePauliOp

from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator
import qiskit.qasm3
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

@dataclass
class CircuitToEstimator(Core):
    """
    In this module, a quantum circuit is executed on an IBM Quantum backend using the Estimator primitive.
    """

    backend_name: str = None
    token: str = "" # Add your IBM token here
    channel: Literal["local", "ibm_cloud", "ibm_quantum_platform"] = "local"
    min_num_qubits: int = 2
    observables: list[float] = None
    options: dict = None
    shots: int = 10

    @override
    def preprocess(self, data: Circuit) -> Result:

        qasm_string = data.as_qasm_string()
        circuit = qiskit.qasm3.loads(qasm_string)

        service = QiskitRuntimeService(channel=self.channel, token=self.token)

        # Selects least busy backend filtered by name and min_num_qubits
        if self.backend_name is None:
            backend = service.least_busy(min_num_qubits=self.min_num_qubits)
        else:
            backend = service.backend(self.backend_name)
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        transpiled_circuit = pm.run(circuit)
        if self.observables is None:
            hamiltonian = SparsePauliOp.from_list([("II", 1), ("IZ", 2), ("XI", 3)])
            observables = hamiltonian.apply_layout(transpiled_circuit.layout)
        else:
            observables = self.observables
        if self.options is None:
            self.options = {"default_shots": self.shots}
        estimator = Estimator(backend, options=self.options)

        # Execute the circuit using the Estimator primitive
        job = estimator.run([(transpiled_circuit, observables)])
        self.result = job.result()
        return Data(Other(self.result))

    @override
    def postprocess(self, data: Other) -> Result:
        result_dict = {"expectation_values": self.result[0].data.evs.tolist(), "counts": self.shots, "raw_results": self.result}
        return Data(Other(result_dict))
