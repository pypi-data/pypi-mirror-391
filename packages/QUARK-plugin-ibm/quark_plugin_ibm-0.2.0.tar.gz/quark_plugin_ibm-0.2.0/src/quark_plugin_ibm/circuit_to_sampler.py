from dataclasses import dataclass
from typing import override, Literal

from quark.core import Core, Data, Result
from quark.interface_types import Circuit, Other, SampleDistribution

from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import qiskit.qasm3
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

@dataclass
class CircuitToSampler(Core):
    """
    In this module, a quantum circuit is executed on an IBM Quantum backend using the Sampler primitive.
    """

    backend_name: str = None
    token: str = "" # Add your IBM token here
    channel: Literal["local", "ibm_cloud", "ibm_quantum_platform"] = "local"
    min_num_qubits: int = 2
    parameter_values: list[float] = None
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
        sampler = Sampler(backend)

        # Execute the circuit using the Sampler primitive
        if self.parameter_values is None:
            job = sampler.run([transpiled_circuit], shots=self.shots)
        else:
            job = sampler.run([(transpiled_circuit, self.parameter_values)], shots=self.shots)
        self.result = job.result()
        return Data(Other(self.result))

    @override
    def postprocess(self, data: Other) -> Result:
        result_as_list = []
        result_as_dict = self.result[0].data.c.get_counts()
        for qubit_string in result_as_dict:
            result_as_list.append((qubit_string, result_as_dict[qubit_string]))
        return Data(SampleDistribution.from_list(result_as_list, self.shots))
