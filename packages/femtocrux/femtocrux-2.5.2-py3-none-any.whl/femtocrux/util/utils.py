""" Utils for client-server communication. """
import json
import numpy as np
import torch
from typing import Any
import sys
import termios

import femtocrux.grpc.compiler_service_pb2 as cs_pb2


def field_or_none(message: Any, field_name: str) -> Any:
    """Convert empty message fields to None."""
    return getattr(message, field_name) if message.HasField(field_name) else None


def get_channel_options(max_message_mb: int = 32):
    # Set the maximum message size
    megabyte_size = 2**20
    max_message_size = max_message_mb * megabyte_size
    return [
        ("grpc.max_send_message_length", max_message_size),
        ("grpc.max_receive_message_length", max_message_size),
    ]


def serialize_numpy_array(arr: np.ndarray) -> cs_pb2.ndarray:
    """Serializes a NumPy array into a NumpyArrayProto message."""
    return cs_pb2.ndarray(
        data=arr.tobytes(), shape=list(arr.shape), dtype=str(arr.dtype)
    )


def serialize_sim_inputs_message(
    data_dict: dict, input_period: float
) -> cs_pb2.simulation_data:
    """Serializes a dictionary where values are NumPy arrays."""
    message = cs_pb2.simulation_data()
    for key, array in data_dict.items():
        if isinstance(array, torch.Tensor):
            array_to_serialize = array.numpy()
        elif isinstance(array, np.ndarray):
            array_to_serialize = array
        else:
            raise (Exception("Input array was not of type torch.Tensor or np.ndarray"))

        if not np.issubdtype(array_to_serialize.dtype, np.integer):
            raise (
                Exception(
                    "Input data is not an integer type. Please quantize your"
                    "data to int16 or lower."
                )
            )

        if len(array_to_serialize.shape) > 2:
            raise (
                Exception(
                    "Expected 2 dimensions for input and got shape: "
                    "{array_to_serialize.shape} Your input array has too many "
                    "dimensions. When in inference mode, please remove any batch "
                    "dimensions."
                )
            )

        message.inputs[key].CopyFrom(serialize_numpy_array(array_to_serialize))
    message.input_period = input_period
    return message


def serialize_simulation_output(data_dict: dict, report) -> cs_pb2.simulation_output:
    """Serializes a dictionary where values are NumPy arrays."""
    message = cs_pb2.simulation_output()
    for key, array in data_dict.items():
        message.outputs[key].CopyFrom(serialize_numpy_array(array))
    message.report = json.dumps(report)
    message.status.CopyFrom(cs_pb2.status(success=True))

    return message


def deserialize_numpy_array(proto: cs_pb2.ndarray) -> np.ndarray:
    """Deserializes a NumpyArrayProto message back into a NumPy array."""
    return np.frombuffer(proto.data, dtype=np.dtype(proto.dtype)).reshape(proto.shape)


def deserialize_simulation_data(proto: cs_pb2.simulation_data) -> dict:
    """Deserializes a LargerMessage back into a dictionary of NumPy arrays."""
    return {key: deserialize_numpy_array(value) for key, value in proto.items()}


def deserialize_simulation_output(proto: cs_pb2.simulation_output) -> dict:
    """Deserializes a LargerMessage back into a dictionary of NumPy arrays."""
    return {key: deserialize_numpy_array(value) for key, value in proto.items()}


def read_secret_raw(prompt="Secret: "):
    """Read a secret from stdin without echoing or overflowing buffer"""
    fd = sys.stdin.fileno()
    sys.stdout.write(prompt)
    sys.stdout.flush()
    old = termios.tcgetattr(fd)
    try:
        new = termios.tcgetattr(fd)
        new[3] &= ~(termios.ECHO | termios.ICANON)  # no echo, raw-ish
        termios.tcsetattr(fd, termios.TCSADRAIN, new)
        chunks = []
        while True:
            ch = sys.stdin.buffer.read(1)
            if ch in (b"\n", b"\r"):
                break
            chunks.append(ch)
        sys.stdout.write("\n")
        sys.stdout.flush()
        return b"".join(chunks).decode("utf-8", "replace")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
