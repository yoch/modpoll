"""Register and coil payload decoding (replaces removed pymodbus.payload).

Derived from pymodbus 3.9.2 BinaryPayloadDecoder.
"""

from __future__ import annotations

from array import array
from struct import pack, unpack

from pymodbus.pdu.utils import pack_bitstring, unpack_bitstring


class Endian:
    BIG = ">"
    LITTLE = "<"


class RegisterDecoder:
    """Decode Modbus register/coil payloads with configurable byte and word order."""

    def __init__(self, payload: bytes, byteorder=Endian.LITTLE, wordorder=Endian.BIG):
        self._payload = payload
        self._pointer = 0
        self._byteorder = byteorder
        self._wordorder = wordorder

    @classmethod
    def from_registers(
        cls,
        registers: list[int],
        byteorder=Endian.LITTLE,
        wordorder=Endian.BIG,
    ) -> RegisterDecoder:
        payload = pack(f"!{len(registers)}H", *registers)
        return cls(payload, byteorder, wordorder)

    @classmethod
    def from_coils(
        cls,
        coils: list[bool],
        byteorder=Endian.LITTLE,
    ) -> RegisterDecoder:
        # Unused by modpoll FC1/FC2 polling (direct result.bits slicing). Kept for API parity.
        payload = b""
        if padding := len(coils) % 8:
            coils = [False] * padding + coils
        for chunk in (coils[i : i + 8] for i in range(0, len(coils), 8)):
            payload += pack_bitstring(chunk[::-1])
        return cls(payload, byteorder)

    def _unpack_words(self, handle: bytes) -> bytes:
        if Endian.LITTLE in {self._byteorder, self._wordorder}:
            handle_array = array("H", handle)
            if self._byteorder == Endian.LITTLE:
                handle_array.byteswap()
            if self._wordorder == Endian.LITTLE:
                handle_array.reverse()
            handle = handle_array.tobytes()
        return handle

    def decode_16bit_uint(self) -> int:
        self._pointer += 2
        handle = self._payload[self._pointer - 2 : self._pointer]
        return unpack(self._byteorder + "H", handle)[0]

    def decode_16bit_int(self) -> int:
        self._pointer += 2
        handle = self._payload[self._pointer - 2 : self._pointer]
        return unpack(self._byteorder + "h", handle)[0]

    def decode_32bit_uint(self) -> int:
        self._pointer += 4
        handle = self._unpack_words(self._payload[self._pointer - 4 : self._pointer])
        return unpack("!I", handle)[0]

    def decode_32bit_int(self) -> int:
        self._pointer += 4
        handle = self._unpack_words(self._payload[self._pointer - 4 : self._pointer])
        return unpack("!i", handle)[0]

    def decode_64bit_uint(self) -> int:
        self._pointer += 8
        handle = self._unpack_words(self._payload[self._pointer - 8 : self._pointer])
        return unpack("!Q", handle)[0]

    def decode_64bit_int(self) -> int:
        self._pointer += 8
        handle = self._unpack_words(self._payload[self._pointer - 8 : self._pointer])
        return unpack("!q", handle)[0]

    def decode_16bit_float(self) -> float:
        self._pointer += 2
        handle = self._unpack_words(self._payload[self._pointer - 2 : self._pointer])
        return unpack("!e", handle)[0]

    def decode_32bit_float(self) -> float:
        self._pointer += 4
        handle = self._unpack_words(self._payload[self._pointer - 4 : self._pointer])
        return unpack("!f", handle)[0]

    def decode_64bit_float(self) -> float:
        self._pointer += 8
        handle = self._unpack_words(self._payload[self._pointer - 8 : self._pointer])
        return unpack("!d", handle)[0]

    def decode_bits(self, package_len: int = 1) -> list[bool]:
        self._pointer += package_len
        handle = self._payload[self._pointer - 1 : self._pointer]
        return unpack_bitstring(handle)

    def decode_string(self, size: int = 1) -> bytes:
        self._pointer += size
        return self._payload[self._pointer - size : self._pointer]

    def skip_bytes(self, nbytes: int) -> None:
        self._pointer += nbytes
