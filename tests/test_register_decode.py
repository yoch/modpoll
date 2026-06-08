from modpoll.modbus_task import Device, Poller, Reference


class FakeResult:
    def __init__(self, *, bits=None, registers=None):
        self.bits = bits
        self.registers = registers

    def isError(self):
        return False


def test_poller_decodes_le_be_bit_and_float16():
    device = Device("dev", 1)
    poller = Poller(device, 3, 40000, 2, "LE_BE")
    ref_msb = Reference(device, "bit15", "40000:15", "bool", "r", None, None)
    ref_float = Reference(device, "current", "40001", "float16", "r", None, None)
    poller.add_readable_reference(ref_msb)
    poller.add_readable_reference(ref_float)

    class FakeMaster:
        def read_holding_registers(self, *args, **kwargs):
            return FakeResult(registers=[0x8001, 0x4228])

    assert poller.poll(FakeMaster()) is True
    assert ref_msb.val is False
    assert ref_float.val == 0.03326416015625
