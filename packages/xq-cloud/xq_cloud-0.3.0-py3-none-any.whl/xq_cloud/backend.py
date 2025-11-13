from __future__ import annotations

from typing import Union

import qiskit.qasm2
from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2 as Backend
from qiskit.providers import JobV1 as Job
from qiskit.providers import Options
from qiskit.providers.jobstatus import JobStatus
from qiskit.result import Result
from qiskit.result.models import ExperimentResultData
from qiskit.result.result import ExperimentResult
from qiskit.transpiler import Target
from typing_extensions import override
from xq_pulse.pulse.program import PulseProgram
from xq_pulse.pulse.serialization import create_converter

from xq_cloud.client import XQCloudApiError, XQCloudClient


class XQCloudJob(Job):
    _backend: XQCloudBackend
    _job_id: str
    shots: int
    readout: str

    def __init__(self, backend: XQCloudBackend, job_id: str, shots: int = -1, readout: str = "population"):
        super().__init__(backend, job_id)
        self.shots = shots
        self.readout = readout

    @override
    def result(self, timeout_seconds: float = 300.0):
        """Get the result of the job execution.

        Args:
            timeout_seconds: Maximum time to wait for the job to complete (default: 300.0).
                If the timeout is exceeded, a TimeoutError or XQCloudApiError will be raised.

        Returns:
            Result object containing the job results.

        Raises:
            TimeoutError: If the job does not complete within the timeout period.
            XQCloudApiError: If the API returns an error or the result data is not available.
        """
        success = False
        expectation_values: dict[str, float] | None = None
        photoluminescence: list[float] | list[list[float]] | None = None
        shots_used = self.shots
        try:
            result_data = self._backend._client.wait_for_result(
                int(self._job_id),
                poll_interval_seconds=0.5,
                timeout_seconds=timeout_seconds,
                readout=self.readout,
            )
            # Get the actual shots used from the API response
            result_status = self._backend._client.get_result(int(self._job_id))
            if result_status.shots is not None:
                shots_used = result_status.shots

            # Process result based on readout mode
            if self.readout == "pl":
                photoluminescence = result_data.get("photoluminescence")
                # Validate that photoluminescence data is present and not None
                if photoluminescence is None:
                    success = False
                else:
                    success = True
            else:
                expectation_values = result_data
                # Validate that expectation values are present (non-empty dict)
                if not expectation_values or not isinstance(expectation_values, dict):
                    success = False
                else:
                    success = True
        except (TimeoutError, XQCloudApiError):
            # Re-raise timeout and API errors instead of silently catching them
            raise

        # Build ExperimentResultData based on readout mode
        if self.readout == "pl":
            data = ExperimentResultData(photoluminescence=photoluminescence)
        else:
            data = ExperimentResultData(expectation_values=expectation_values)

        return Result(
            backend_name=self._backend.name,
            backend_version=self._backend.backend_version,
            job_id=self._job_id,
            success=success,
            results=[
                ExperimentResult(
                    shots=shots_used,
                    success=success,
                    data=data,
                    status=JobStatus.DONE if success else JobStatus.ERROR,
                )
            ],
        )

    @override
    def submit(self):
        """This is a no-op as the job is submitted on creation."""
        return

    def cancel(self):
        """Attempt to cancel the job."""
        # TODO: Implement job cancellation in the API
        raise NotImplementedError

    @override
    def status(self) -> JobStatus:
        result = self._backend._client.get_result(int(self._job_id))
        if result.status == 'running':
            status = JobStatus.RUNNING
        elif result.status == 'completed':
            status = JobStatus.DONE
        else:
            status = JobStatus.ERROR
        return status


class XQCloudBackend(Backend):
    """Qiskit Backend describing the XQ Cloud target."""

    def __init__(
        self,
        client: XQCloudClient,
        *,
        target: Target,
        name: str = "xq-cloud-xq1",
        description: str = "XQ Cloud backend for XQ1 target",
        backend_version: str = "0.0.0",
        supports_pulse_level: bool = False,
    ) -> None:
        super().__init__(
            provider=None,
            name=name,
            description=description,
            backend_version=backend_version,
        )
        self._client = client
        self._target = target
        self._options = self._default_options()
        self.supports_pulse_level = supports_pulse_level
        if supports_pulse_level:
            self._converter = create_converter()
        else:
            self._converter = None

    @property
    def target(self) -> Target:  # type: ignore[override]
        return self._target

    @property
    def options(self) -> Options:  # type: ignore[override]
        return self._options

    @property
    def max_circuits(self) -> int | None:  # type: ignore[override]
        return 1

    @override
    def run(
        self,
        run_input: Union[QuantumCircuit, PulseProgram] | list[Union[QuantumCircuit, PulseProgram]],
        **options,
    ) -> XQCloudJob:  # type: ignore[override]
        if isinstance(run_input, list):
            # Unwrap single circuit if needed
            assert len(run_input) == 1, f"Only single-circuit jobs are supported by the {self.name} backend"
            program = run_input[0]
        else:
            program = run_input

        # Validate PulseProgram support
        if isinstance(program, PulseProgram):
            if not self.supports_pulse_level:
                raise ValueError(
                    f"Backend {self.name} does not support PulseProgram. "
                    "Use a backend with supports_pulse_level=True or submit a QuantumCircuit."
                )
        else:
            # Validate the circuit is compatible with this backend's target before submission
            self.assert_compatible(program, self.target)

        # Extract shots and readout from options if provided
        shots = options.get("shots", None)
        readout = options.get("readout", "population")

        # Validate readout mode
        if readout not in ("population", "pl"):
            raise ValueError(f'Invalid readout mode "{readout}". Must be "population" or "pl".')

        # Serialize program based on type
        if isinstance(program, PulseProgram):
            assert self._converter is not None, "Converter should be initialized when supports_pulse_level=True"
            program_dict = self._converter.unstructure(program)
            job_id = self._client.queue_program(program_dict, backend=self.name, shots=shots, readout=readout)
        else:
            serialized_circuit = qiskit.qasm2.dumps(program)
            job_id = self._client.queue_circuit(serialized_circuit, backend=self.name, shots=shots, readout=readout)

        return XQCloudJob(
            backend=self,
            job_id=str(job_id),
            shots=shots if shots is not None else -1,
            readout=readout,
        )

    @classmethod
    def _default_options(cls) -> Options:  # type: ignore[override]
        """Default backend options."""
        return Options()

    def __repr__(self) -> str:
        return f"XQCloudBackend(name={self.name}, description={self.description})"

    @staticmethod
    def assert_compatible(circuit: QuantumCircuit, target: Target) -> None:
        """Raise ValueError if ``circuit`` is not compatible with ``target``.

        Checks:
        - Circuit qubit count does not exceed target qubits.
        - All instructions are in the target's operation set (barrier is ignored).
        - Each instruction is applied to a qubit tuple allowed by the target.
        """
        # Basic qubit count check
        if circuit.num_qubits > int(target.num_qubits):
            raise ValueError(f"Circuit uses {circuit.num_qubits} qubits, but target supports only {target.num_qubits}.")

        allowed_ops = set(target.operation_names)
        errors: list[str] = []

        for inst in circuit.data:
            op = inst.operation

            # Skip barriers
            if op.name == "barrier":
                continue

            # Disallow measurements for this backend
            if op.name == "measure":
                errors.append("Unsupported operation 'measure' — remove measurements before submission")
                continue

            name = op.name
            if name not in allowed_ops:
                errors.append(f"Unsupported operation '{name}'. Supported: {sorted(allowed_ops)}")
                continue

            # Validate the specific qubit tuple is allowed by the target
            qargs = tuple(circuit.find_bit(qb).index for qb in inst.qubits)
            try:
                qarg_map = target[name]
            except Exception:
                errors.append(f"Target mapping for operation '{name}' is unavailable")
                continue

            if qargs not in qarg_map:
                allowed_qargs = sorted(map(tuple, qarg_map.keys()))
                errors.append(
                    f"Operation '{name}' on qubits {qargs} is not allowed for target; "
                    f"allowed qubit tuples: {allowed_qargs}"
                )

        if errors:
            hint = "Transpile the circuit for this target first."
            raise ValueError("; ".join(errors) + ". " + hint)
