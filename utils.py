def decode(message: bytes) -> str:
    return message.decode("utf-8").rstrip("\n")


def encode(message: str) -> bytes:
    return bytes(message + "\n", "utf-8")
