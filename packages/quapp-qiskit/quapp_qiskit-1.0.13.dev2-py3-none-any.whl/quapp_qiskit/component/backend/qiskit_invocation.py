"""
    QApp Platform Project qiskit_invocation.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  qiskit_invocation.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit import QuantumCircuit

from quapp_common.component.backend.invocation import Invocation
from quapp_common.data.async_task.circuit_export.backend_holder import BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import CircuitDataHolder
from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.model.provider.provider import Provider
from quapp_common.config.logging_config import logger
from quapp_common.config.thread_config import circuit_exporting_pool

from ...factory.qiskit_provider_factory import QiskitProviderFactory
from ...factory.qiskit_device_factory import QiskitDeviceFactory
from ...async_tasks.qiskit_circuit_export_task import QiskitCircuitExportTask


class QiskitInvocation(Invocation):

    def __init__(self, request_data: InvocationRequest):
        super().__init__(request_data)

    def _export_circuit(self, circuit):
        self.logger.debug('Exporting circuit to backend')

        circuit_export_task = QiskitCircuitExportTask(
            circuit_data_holder=CircuitDataHolder(circuit, self.circuit_export_url),
            backend_data_holder=BackendDataHolder(
                self.backend_information, self.authentication.user_token
            ),
        )

        circuit_exporting_pool.submit(circuit_export_task.do)

    def _create_provider(self):
        try:
            self.logger.debug(
                    f'Creating provider: provider_tag={getattr(self.backend_information, "provider_tag", None)}, sdk={getattr(self, "sdk", None)}')
            provider = QiskitProviderFactory.create_provider(
            provider_type=self.backend_information.provider_tag,
            sdk=self.sdk,
            authentication=self.backend_information.authentication,
        )
            self.logger.info(
                    f'Provider created successfully: {type(provider).__name__}')
            return provider
        except Exception as exception:
            self.logger.exception(f'Provider creation failed: {exception}')
            raise

    def _create_device(self, provider: Provider):
        self.logger.debug('Creating device')
        try:
            device_spec = getattr(self.backend_information, "device_name", None)
            self.logger.debug(
                    f'Creating device from provider={type(provider).__name__}, '
                    f'device_specification={device_spec}, sdk={getattr(self, "sdk", None)}', )
            device = QiskitDeviceFactory.create_device(
            provider=provider,
            device_specification=self.backend_information.device_name,
            authentication=self.backend_information.authentication,
            sdk=self.sdk,
        )
            self.logger.info(
                    f'Device created successfully: {type(device).__name__}')
            return device
        except Exception as exception:
            self.logger.exception(f"Device creation failed: {exception}")
            raise

    def _get_qubit_amount(self, circuit):
        self.logger.debug(
                f'Getting qubit amount for circuit type: {type(circuit).__name__}')
        if isinstance(circuit, QuantumCircuit):
            qubits = int(circuit.num_qubits)
            self.logger.debug(f'Qubit amount determined: {qubits}')
            return qubits

        self.logger.exception(
                f'Invalid circuit type for qubit amount: {type(circuit).__name__}')
        raise Exception("Invalid circuit type!")
