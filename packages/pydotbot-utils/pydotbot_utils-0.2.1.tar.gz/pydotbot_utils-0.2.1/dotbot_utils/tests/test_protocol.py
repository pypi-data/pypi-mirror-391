"""Test module for dotbot protocol."""

import dataclasses
from dataclasses import dataclass

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


register_parser(0x81, PayloadWithBytesTest)
register_parser(0x82, PayloadWithBytesFixedLengthTest)
register_parser(0x83, PayloadRawData)


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
    ],
)
def test_frame_parser(bytes_, header, payload_type, payload):
    frame = Frame.from_bytes(bytes_)
    assert frame.header == header
    assert frame.packet.payload_type == payload_type
    assert frame.packet.payload == payload


@pytest.mark.parametrize(
    "payload,expected",
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
    ],
)
def test_payload_to_bytes(payload, expected):
    result = payload.to_bytes()
    assert result == expected, f"{result} != {expected}"


# @pytest.mark.parametrize(
#     "frame,string",
#     [
#         pytest.param(
#             Frame(
#                 header=Header(),
#                 packet=Packet.from_payload(
#                     PayloadWithBytesTest(count=8, data=b"abcdefgh")
#                 ),
#             ),
#             (
#                 "                 +------+------+--------------------+--------------------+------+\n"
#                 " CUSTOM_DATA     | ver. | type | dst                | src                | type |\n"
#                 " (28 Bytes)      | 0x01 | 0x10 | 0xffffffffffffffff | 0x0000000000000000 | 0x81 |\n"
#                 "                 +------+------+--------------------+--------------------+------+\n"
#                 "                 +------+--------------------+\n"
#                 "                 | len. | data               |\n"
#                 "                 | 0x08 | 0x6162636465666768 |\n"
#                 "                 +------+--------------------+\n"
#                 "\n"
#             ),
#             id="PayloadWithBytesTest",
#         ),
#         pytest.param(
#             Frame(
#                 header=Header(),
#                 packet=Packet.from_payload(
#                     PayloadWithBytesFixedLengthTest(data=b"abcdefgh")
#                 ),
#             ),
#             (
#                 "                 +------+------+--------------------+--------------------+------+\n"
#                 " CUSTOM_DATA     | ver. | type | dst                | src                | type |\n"
#                 " (27 Bytes)      | 0x01 | 0x10 | 0xffffffffffffffff | 0x0000000000000000 | 0x82 |\n"
#                 "                 +------+------+--------------------+--------------------+------+\n"
#                 "                 +--------------------+\n"
#                 "                 | data               |\n"
#                 "                 | 0x6162636465666768 |\n"
#                 "                 +--------------------+\n"
#                 "\n"
#             ),
#             id="PayloadWithBytesFixedLengthTest",
#         ),
#         pytest.param(
#             Frame(
#                 header=Header(),
#                 packet=Packet.from_payload(PayloadRawData(count=8, data=b"abcdefgh")),
#             ),
#             (
#                 "                 +------+------+--------------------+--------------------+------+\n"
#                 " RAW_DATA        | ver. | type | dst                | src                | type |\n"
#                 " (28 Bytes)      | 0x01 | 0x10 | 0xffffffffffffffff | 0x0000000000000000 | 0x10 |\n"
#                 "                 +------+------+--------------------+--------------------+------+\n"
#                 "                 +------+--------------------+\n"
#                 "                 | len. | data               |\n"
#                 "                 | 0x08 | 0x6162636465666768 |\n"
#                 "                 +------+--------------------+\n"
#                 "\n"
#             ),
#             id="PayloadRawDataTest",
#         ),
#     ],
# )
# def test_payload_frame_repr(frame, string, capsys):
#     print(frame)
#     out, _ = capsys.readouterr()
#     assert out == string


def test_parse_missing_metadata():
    @dataclass
    class PayloadMissingMetadata(Payload):
        field: int = 0

    with pytest.raises(ValueError) as excinfo:
        PayloadMissingMetadata().from_bytes(b"")
    assert str(excinfo.value) == "metadata must be defined first"


# @pytest.mark.parametrize(
#     "payload,bytes_",
#     [
#         pytest.param(
#             PayloadAdvertisement(application=ApplicationType.DotBot, calibrated=False),
#             b"",
#             id="PayloadAdvertisement",
#         ),
#         pytest.param(
#             PayloadDotBotData(direction=45, pos_x=1000, pos_y=1000, pos_z=2),
#             b"-\x00\x02" b"\xf1\xde\xbc\x9a\x78\x56\x34\x12\x01\x02",
#             id="PayloadDotBotData",
#         ),
#     ],
# )
# def test_from_bytes_empty(payload, bytes_):
#     with pytest.raises(ValueError) as excinfo:
#         payload.from_bytes(bytes_)
#     assert str(excinfo.value) == "Not enough bytes to parse"


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
