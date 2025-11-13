"""Test module for dotbot protocol."""

import dataclasses
from dataclasses import dataclass
from enum import IntEnum

import pytest

from dotbot_utils.protocol import (
    PAYLOAD_PARSERS,
    Frame,
    Header,
    Packet,
    Payload,
    PayloadFieldMetadata,
    PayloadRawData,
    ProtocolPayloadParserException,
    register_parser,
)


@dataclass
class PayloadWithBytesTest(Payload):
    metadata: list[PayloadFieldMetadata] = dataclasses.field(
        default_factory=lambda: [
            PayloadFieldMetadata(name="count", disp="len."),
            PayloadFieldMetadata(name="data", type_=bytes, length=0),
        ]
    )
    count: int = 0
    data: bytes = b""


@dataclass
class PayloadWithBytesFixedLengthTest(Payload):
    metadata: list[PayloadFieldMetadata] = dataclasses.field(
        default_factory=lambda: [
            PayloadFieldMetadata(name="data", type_=bytes, length=8),
        ]
    )
    data: bytes = b""


@dataclass
class PayloadWithInt(Payload):
    """Dataclass that holds a 1 byte int."""

    metadata: list[PayloadFieldMetadata] = dataclasses.field(
        default_factory=lambda: [
            PayloadFieldMetadata(name="value", disp="val."),
        ]
    )

    value: int = 0


@dataclass
class PayloadWithLongInt(Payload):
    """Dataclass that holds a 4-bytes int."""

    metadata: list[PayloadFieldMetadata] = dataclasses.field(
        default_factory=lambda: [
            PayloadFieldMetadata(name="value", disp="val.", length=4),
        ]
    )

    value: int = 0


@dataclass
class PayloadWithList(Payload):
    """Dataclass that holds a list."""

    metadata: list[PayloadFieldMetadata] = dataclasses.field(
        default_factory=lambda: [
            PayloadFieldMetadata(name="count", disp="len."),
            PayloadFieldMetadata(name="values", type_=list, length=0),
        ]
    )

    count: int = 0
    values: list[PayloadWithLongInt] = dataclasses.field(default_factory=lambda: [])


register_parser(0x81, PayloadWithBytesTest)
register_parser(0x82, PayloadWithBytesFixedLengthTest)


class PayloadType(IntEnum):
    RAW_DATA = 0x83
    WITH_INT = 0x84
    WITH_LONG_INT = 0x85
    WITH_LIST = 0x86


register_parser(PayloadType.RAW_DATA, PayloadRawData)
register_parser(PayloadType.WITH_INT, PayloadWithInt)
register_parser(PayloadType.WITH_LONG_INT, PayloadWithLongInt)
register_parser(PayloadType.WITH_LIST, PayloadWithList)


@pytest.mark.parametrize(
    "bytes_,expected",
    [
        pytest.param(
            b"\x04\x02\x11\x11\x11\x11\x11\x22\x22\x11\x12\x12\x12\x12\x12\x12\x12\x12",
            Header(
                version=4,
                type_=2,
                destination=0x1122221111111111,
                source=0x1212121212121212,
            ),
            id="DefaultHeader",
        ),
    ],
)
def test_parse_header(bytes_, expected):
    assert Header().from_bytes(bytes_) == expected


@pytest.mark.parametrize(
    "bytes_,header,payload_type,payload",
    [
        pytest.param(
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x81"  # payload type
            b"\x08"  # count
            b"abcdefgh",  # data
            Header(),
            0x81,
            PayloadWithBytesTest(count=8, data=b"abcdefgh"),
            id="PayloadWithBytesTest",
        ),
        pytest.param(
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x82"  # payload type
            b"abcdefgh",  # data
            Header(),
            0x82,
            PayloadWithBytesFixedLengthTest(data=b"abcdefgh"),
            id="PayloadWithBytesFixedLengthTest",
        ),
        pytest.param(
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x83"  # Raw data type
            b"\x08"  # count
            b"abcdefgh",  # data
            Header(),
            0x83,
            PayloadRawData(count=8, data=b"abcdefgh"),
            id="PayloadRawDataTest",
        ),
        pytest.param(
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x84"  # payload type
            b"\x08",  # value
            Header(),
            0x84,
            PayloadWithInt(value=8),
            id="PayloadWithInt",
        ),
        pytest.param(
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x85"  # payload type
            b"\x08\x00\x00\x00",  # value
            Header(),
            0x85,
            PayloadWithLongInt(value=8),
            id="PayloadWithLongInt",
        ),
        pytest.param(
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x86"  # payload type
            b"\x02"  # count
            b"\x0a\x00\x00\x00\x0b\x00\x00\x00",  # list of ints
            Header(),
            0x86,
            PayloadWithList(
                count=2,
                values=[PayloadWithLongInt(value=10), PayloadWithLongInt(value=11)],
            ),
            id="PayloadWithList",
        ),
    ],
)
def test_frame_parser(bytes_, header, payload_type, payload):
    frame = Frame.from_bytes(bytes_)
    assert frame.header == header
    assert frame.packet.payload_type == payload_type
    assert frame.packet.payload == payload


@pytest.mark.parametrize(
    "frame,expected",
    [
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(
                    PayloadWithBytesTest(count=8, data=b"abcdefgh")
                ),
            ),
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x81"  # payload type
            b"\x08"  # count
            b"abcdefgh",  # data
            id="PayloadWithBytesTest",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(
                    PayloadWithBytesFixedLengthTest(data=b"abcdefgh")
                ),
            ),
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x82"  # payload type
            b"abcdefgh",  # data
            id="PayloadWithBytesFixedLengthTest",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(PayloadRawData(count=8, data=b"abcdefgh")),
            ),
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x83"  # Raw data type
            b"\x08"  # count
            b"abcdefgh",  # data
            id="PayloadRawDataTest",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(PayloadWithInt(value=8)),
            ),
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x84"  # payload type
            b"\x08",  # value
            id="PayloadWithInt",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(PayloadWithLongInt(value=8)),
            ),
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x85"  # payload type
            b"\x08\x00\x00\x00",  # value
            id="PayloadWithLongInt",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(
                    PayloadWithList(
                        count=2,
                        values=[
                            PayloadWithLongInt(value=10),
                            PayloadWithLongInt(value=11),
                        ],
                    )
                ),
            ),
            b"\x01\x10\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00"  # header
            b"\x86"  # payload type
            b"\x02"  # count
            b"\x0a\x00\x00\x00\x0b\x00\x00\x00",  # list of ints
            id="PayloadWithList",
        ),
    ],
)
def test_payload_to_bytes(frame, expected):
    result = frame.to_bytes()
    assert result == expected, f"{result} != {expected}"


@pytest.mark.parametrize(
    "frame,string",
    [
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(
                    PayloadWithBytesTest(count=8, data=b"abcdefgh")
                ),
            ),
            (
                "                 +------+------+--------------------+--------------------+------+\n"
                " CUSTOM_DATA     | ver. | type | dst                | src                | type |\n"
                " (28 Bytes)      | 0x01 | 0x10 | 0xffffffffffffffff | 0x0000000000000000 | 0x81 |\n"
                "                 +------+------+--------------------+--------------------+------+\n"
                "                 +------+--------------------+\n"
                "                 | len. | data               |\n"
                "                 | 0x08 | 0x6162636465666768 |\n"
                "                 +------+--------------------+\n"
                "\n"
            ),
            id="PayloadWithBytesTest",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(
                    PayloadWithBytesFixedLengthTest(data=b"abcdefgh")
                ),
            ),
            (
                "                 +------+------+--------------------+--------------------+------+\n"
                " CUSTOM_DATA     | ver. | type | dst                | src                | type |\n"
                " (27 Bytes)      | 0x01 | 0x10 | 0xffffffffffffffff | 0x0000000000000000 | 0x82 |\n"
                "                 +------+------+--------------------+--------------------+------+\n"
                "                 +--------------------+\n"
                "                 | data               |\n"
                "                 | 0x6162636465666768 |\n"
                "                 +--------------------+\n"
                "\n"
            ),
            id="PayloadWithBytesFixedLengthTest",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(PayloadRawData(count=8, data=b"abcdefgh")),
            ),
            (
                "                 +------+------+--------------------+--------------------+------+\n"
                " RAW_DATA        | ver. | type | dst                | src                | type |\n"
                " (28 Bytes)      | 0x01 | 0x10 | 0xffffffffffffffff | 0x0000000000000000 | 0x83 |\n"
                "                 +------+------+--------------------+--------------------+------+\n"
                "                 +------+--------------------+\n"
                "                 | len. | data               |\n"
                "                 | 0x08 | 0x6162636465666768 |\n"
                "                 +------+--------------------+\n"
                "\n"
            ),
            id="PayloadRawDataTest",
        ),
        pytest.param(
            Frame(
                header=Header(),
                packet=Packet.from_payload(PayloadWithInt(value=8)),
            ),
            (
                "                 +------+------+--------------------+--------------------+------+------+\n"
                " WITH_INT        | ver. | type | dst                | src                | type | val. |\n"
                " (20 Bytes)      | 0x01 | 0x10 | 0xffffffffffffffff | 0x0000000000000000 | 0x84 | 0x08 |\n"
                "                 +------+------+--------------------+--------------------+------+------+\n"
                "\n"
            ),
            id="PayloadWithInt",
        ),
    ],
)
def test_payload_frame_repr(frame, string, capsys):
    print(frame)
    out, _ = capsys.readouterr()
    assert out == string


def test_parse_missing_metadata():
    @dataclass
    class PayloadMissingMetadata(Payload):
        field: int = 0

    with pytest.raises(ValueError) as excinfo:
        PayloadMissingMetadata().from_bytes(b"")
    assert str(excinfo.value) == "metadata must be defined first"


@dataclass
class PayloadTest(Payload):
    metadata: list[PayloadFieldMetadata] = dataclasses.field(
        default_factory=lambda: [PayloadFieldMetadata(name="field", type_=int)]
    )
    field: int = 0


@pytest.mark.parametrize(
    "payload_type,value_str",
    [
        (0x81, "0x81"),
        (0x82, "0x82"),
        (0x83, "0x83"),
    ],
)
def test_register_already_registered(payload_type, value_str):
    with pytest.raises(ValueError) as excinfo:
        register_parser(payload_type, PayloadTest)
    assert str(excinfo.value) == f"Payload type '{value_str}' already registered"


def test_register_parser():
    register_parser(0xFE, PayloadTest)
    assert PAYLOAD_PARSERS[0xFE] == PayloadTest


def test_parse_non_registered_payload():
    with pytest.raises(ProtocolPayloadParserException) as excinfo:
        Frame.from_bytes(
            b"\x04\x02\x88\x77\x66\x55\x44\x33\x22\x11\x21\x12\x22\x12\x22\x12\x22\x12\xfd\x01"
        )
    assert str(excinfo.value).startswith("Unsupported payload type")

    @dataclass
    class PayloadNotRegisteredTest(Payload):
        metadata: list[PayloadFieldMetadata] = dataclasses.field(
            default_factory=lambda: [PayloadFieldMetadata(name="field", type_=int)]
        )
        field: int = 0

    with pytest.raises(ValueError) as excinfo:
        Frame(header=Header(), packet=Packet.from_payload(PayloadNotRegisteredTest()))
    assert str(excinfo.value).startswith("Unsupported payload class")


@pytest.mark.parametrize(
    "payload,bytes_",
    [
        pytest.param(
            PayloadWithInt(value=42),
            b"",
            id="PayloadWithInt",
        ),
        pytest.param(
            PayloadWithList(
                count=2, values=[PayloadWithInt(value=10), PayloadWithInt(value=11)]
            ),
            b"\x02"  # count
            b"\x0a\x0b",  # list of ints,
            id="PayloadWithList",
        ),
    ],
)
def test_from_bytes_empty(payload, bytes_):
    with pytest.raises(ValueError) as excinfo:
        payload.from_bytes(bytes_)
    assert str(excinfo.value) == "Not enough bytes to parse"


def test_packet_with_none_payload():
    packet = Packet(payload_type=0x01)
    assert packet.to_bytes() == b"\x01"
