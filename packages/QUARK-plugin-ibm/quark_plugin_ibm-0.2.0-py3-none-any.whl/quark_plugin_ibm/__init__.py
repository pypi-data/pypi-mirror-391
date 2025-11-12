from quark.plugin_manager import factory

from quark_plugin_ibm.circuit_to_estimator import CircuitToEstimator
from quark_plugin_ibm.circuit_to_sampler import CircuitToSampler

def register() -> None:
    """
    Register the IBM Quantum modules in the Quark factory.
    """
    factory.register("circuit_to_estimator", CircuitToEstimator)
    factory.register("circuit_to_sampler", CircuitToSampler)
