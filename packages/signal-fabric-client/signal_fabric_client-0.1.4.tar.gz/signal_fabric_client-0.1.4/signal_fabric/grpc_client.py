"""
gRPC Client for Signal Fabric
Provides a clean interface for connecting to Signal Fabric server
"""

import json
import grpc
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Import generated protobuf code from package
from generated.signal_processor_pb2_grpc import SignalProcessorStub
from generated.signal_processor_pb2 import SignalRequest, SignalResponse


@dataclass
class SignalOutcome:
    """
    Represents the outcome of a signal computation
    Mirrors the server's Outcome/DetailedOutcome structure
    """
    result: str
    computation: str
    computed_at: float
    errors: List[str] = None
    details: Dict[str, str] = None

    def __post_init__(self):
        """Initialize empty collections if None"""
        if self.errors is None:
            self.errors = []
        if self.details is None:
            self.details = {}

    def has_errors(self) -> bool:
        """Check if outcome contains errors"""
        return len(self.errors) > 0

    def is_detailed(self) -> bool:
        """Check if this is a detailed outcome (has errors or details)"""
        return len(self.errors) > 0 or len(self.details) > 0


class GrpcClient:
    """
    gRPC client for Signal Fabric server

    Usage:
        from signal_fabric import GrpcClient

        # Connect to server
        client = GrpcClient(host='localhost', port=50051)

        # Process a signal
        outcome = client.process_signal(
            target='BTC',
            signal_name='trend',
            signal_op='analyze',
            handler_request={'period': 14}
        )

        # Check result
        if outcome.has_errors():
            print(f"Errors: {outcome.errors}")
        else:
            print(f"Result: {outcome.result}")
    """

    def __init__(self, host: str = 'localhost', port: int = 50051, timeout: int = 30,
                 ca_cert_path: str = None):
        """
        Initialize gRPC client with TLS/SSL

        Args:
            host: Server hostname or IP address
            port: Server port number
            timeout: Request timeout in seconds
            ca_cert_path: Path to CA certificate for server verification (optional, uses system CAs if not provided)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.ca_cert_path = ca_cert_path
        self.server_address = f'{host}:{port}'
        self._channel = None
        self._stub = None

    def connect(self):
        """
        Establish secure TLS connection to the server
        Creates gRPC channel and stub with TLS encryption
        """
        # Always use TLS - secure channel only
        if self.ca_cert_path:
            # Use custom CA certificate
            with open(self.ca_cert_path, 'rb') as f:
                ca_cert = f.read()
            credentials = grpc.ssl_channel_credentials(root_certificates=ca_cert)
        else:
            # Use system CA certificates
            credentials = grpc.ssl_channel_credentials()

        self._channel = grpc.secure_channel(self.server_address, credentials)
        self._stub = SignalProcessorStub(self._channel)

    def disconnect(self):
        """
        Close the connection to the server
        """
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._stub is not None

    def _ensure_connected(self):
        """Ensure client is connected, connect if not"""
        if not self.is_connected():
            self.connect()

    def process_signal(
        self,
        target: str,
        signal_name: str,
        signal_op: str,
        handler_request: Optional[Dict[str, Any]] = None
    ) -> SignalOutcome:
        """
        Process a signal request

        Args:
            target: Target for signal computation (e.g., 'BTC', 'ETH')
            signal_name: Signal handler name or profile name (e.g., 'hello', 'happy_hello')
            signal_op: Signal operation to perform (e.g., 'greet', 'analyze')
            handler_request: Optional request data as dictionary

        Returns:
            SignalOutcome containing the result

        Raises:
            grpc.RpcError: If the RPC call fails
        """
        self._ensure_connected()

        # Convert handler_request dict to JSON string if provided
        handler_request_json = None
        if handler_request is not None:
            handler_request_json = json.dumps(handler_request)

        # Build gRPC request
        request = SignalRequest(
            target=target,
            signal_name=signal_name,
            signal_op=signal_op,
            handler_request=handler_request_json
        )

        # Make RPC call
        try:
            response: SignalResponse = self._stub.ProcessSignal(
                request,
                timeout=self.timeout
            )

            # Convert response to SignalOutcome
            return SignalOutcome(
                result=response.result,
                computation=response.computation,
                computed_at=response.computed_at,
                errors=list(response.errors) if response.errors else [],
                details=dict(response.details) if response.details else {}
            )

        except grpc.RpcError as e:
            # Wrap gRPC errors in SignalOutcome for consistent error handling
            return SignalOutcome(
                result="UNKNOWN",
                computation="gRPC Error",
                computed_at=0.0,
                errors=[f"gRPC error: {e.code()}: {e.details()}"],
                details={"grpc_code": str(e.code())}
            )

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False
