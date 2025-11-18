from .client import Client, Network, IDFactory, c_pf
import csv
from itertools import count
from .settings import settings


_h: dict[str, [str]] = dict(settings.from_csv.header_names)
"""header names"""


class IpAddress:
    __value: list[int]

    def __init__(self, value: str = "127.0.0.1"):
        self.__value = list()
        for el1 in value.split("."):
            if el1.isdigit():
                el = int(el1)
                if 0 <= el <= 255:
                    self.__value.append(el)
                else:
                    raise ValueError(F"Wrong digit in value: {el}, must be 0..255")
            else:
                raise ValueError(F"Value is not digit: {el1}")
        if len(self.__value) != 4:
            raise ValueError(F"Length of Ip address {value} must be 4, got {len(self.__value)}")

    @classmethod
    def is_valid(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False

    def __str__(self):
        return ".".join(map(str, self.__value))


def get_client_from_csv(
        file_name: str,
        id_factory: IDFactory,
        universal: bool = False
) -> list[Client]:
    """file in utf-8 format"""
    da: str
    with open(file_name, "r", encoding="utf-8-sig") as csv_file:
        dialect = csv.Sniffer().sniff(csv_file.readline(1024))
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect=dialect)
        first_row: list[str] = next(reader)
        if any(map(IpAddress.is_valid, first_row)):  # search ip_address in first row
            raise ValueError("Table header not found")
        # header is exist search column by name
        field_names: list[str] = []
        for index, cell in enumerate(first_row):
            for column in _h:
                if any(map(cell.lower().startswith, _h[column])):
                    field_names.append(_h[column][0])
                    break
            else:
                field_names.append(F"unknown{index}")
        if all(map(lambda name: name in field_names, ("ip",))):
            csv_file.seek(0)
            reader = csv.DictReader(csv_file, fieldnames=field_names, dialect=dialect)
            next(reader)  # skeep header
            res: list[Client] = []
            for i in reader:
                if IpAddress.is_valid(i["ip"]):
                    res.append(c := Client(
                        media=Network(
                            host=i.get("ip") or "127.0.0.1",
                            port=i.get("port") or "8888",
                            to_recv=float(i.get("timeout") or 120.0)
                        ),
                        SAP=int(i.get("sap") or 0x30),
                        secret=bytes(i.get("secret", "0000000000000000"), "utf-8"),
                        m_id=int(i.get("m_id") or 2),
                        id_=id_factory.create(),
                        universal=universal
                    ))
                    if (
                        (da := i.get("da"))
                        and da.isdigit()
                    ):
                        c.com_profile.parameters.device_address = int(da)
                    if name := i.get("name"):
                        c.name = name
            return res
        raise ValueError("not find at least one client")
