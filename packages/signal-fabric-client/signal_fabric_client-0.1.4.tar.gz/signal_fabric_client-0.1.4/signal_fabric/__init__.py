"""
Signal Fabric Client Library
gRPC client for interacting with Signal Fabric server
"""

from .grpc_client import GrpcClient, SignalOutcome

__version__ = "0.1.4"

__all__ = ['GrpcClient', 'SignalOutcome', '__version__']
