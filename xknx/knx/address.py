from enum import Enum

class CouldNotParseAddress(Exception):
    def __init__(self, address=None):
        super(CouldNotParseAddress, self).__init__("Could not parse address")
        self.address = address

    def __str__(self):
        return "<CouldNotParseAddress address='{0}'>".format(self.address)

class AddressType(Enum):
    PHYSICAL = 1
    GROUP = 2

class AddressFormat(Enum):
    LEVEL2 = 1
    LEVEL3 = 2
    FREE = 3

class Address:

    def __init__(self, address=0, address_type=None):
        self.raw = None
        self.address_format = None
        self._set(address, address_type)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Address):
            raise TypeError()
        return self.raw == other.raw

    def __str__(self):
        return "<Address str={0}>".format(self.str())

    def _set(self, address, address_type):

        self.address_type = \
            address_type if address_type is not None \
            else self._detect_address_type(address)

        if address is None:
            self.raw = 0
            self.address_format = AddressFormat.LEVEL3

        elif isinstance(address, Address):
            self.raw = address.raw
            self.address_format = address.address_format

        elif isinstance(address, str):
            if self.address_type == AddressType.PHYSICAL:
                self._set_str_physical(address)
            else:
                self._set_str_group(address)

        elif isinstance(address, int):
            self._set_int(address)

        elif isinstance(address, tuple):
            self._set_tuple(address)

        else:
            raise TypeError()


    def to_knx(self):
        return (self.raw >> 8) & 255, self.raw & 255



    ##################################################
    def _set_str_physical(self, address):
        parts = address.split(".")
        if any(not part.isdigit() for part in parts):
            raise CouldNotParseAddress(address)
        if len(parts) != 3:
            raise CouldNotParseAddress(address)
        main = int(parts[0])
        middle = int(parts[1])
        sub = int(parts[2])
        if main > 15:
            raise CouldNotParseAddress(address)
        if middle > 15:
            raise CouldNotParseAddress(address)
        if sub > 255:
            raise CouldNotParseAddress(address)
        self.raw = (main<<12) +  (middle<<8) + sub
        self.address_format = AddressFormat.LEVEL3


    def _set_str_group(self, address):
        parts = address.split("/")

        if any(not part.isdigit() for part in parts):
            raise CouldNotParseAddress(address)
        if len(parts) == 1:
            self._set_int(int(parts[0]))
        elif len(parts) == 2:
            self._set_str_group_level2(parts)
        elif len(parts) == 3:
            self._set_str_group_level3(parts)
        else:
            raise CouldNotParseAddress(address)

    def _set_str_group_level2(self, parts):
        main = int(parts[0])
        sub = int(parts[1])
        if main > 31:
            raise CouldNotParseAddress(parts)
        if sub > 2047:
            raise CouldNotParseAddress(parts)
        self.raw = (main<<11) + sub
        self.address_format = AddressFormat.LEVEL2

    def _set_str_group_level3(self, parts):
        main = int(parts[0])
        middle = int(parts[1])
        sub = int(parts[2])
        if main > 31:
            raise CouldNotParseAddress(parts)
        if middle > 7:
            raise CouldNotParseAddress(parts)
        if sub > 255:
            raise CouldNotParseAddress(parts)
        self.raw = (main<<11) +  (middle<<8) + sub
        self.address_format = AddressFormat.LEVEL3

    def _set_tuple(self, address):
        if len(address) != 2 \
                or any(not isinstance(byte, int) for byte in address) \
                or any(byte < 0 for byte in address) \
                or any(byte > 255 for byte in address):
            raise CouldNotParseAddress(address)

        self._set_int(address[0] * 256 + address[1])

    def _set_int(self, raw):
        if not isinstance(raw, int):
            raise CouldNotParseAddress(raw)
        if raw > 65535:
            raise CouldNotParseAddress(raw)
        self.raw = raw
        self.address_format = AddressFormat.FREE

    def str(self):
        if self.address_type == AddressType.PHYSICAL:
            return self._str_physical()
        elif self.address_format == AddressFormat.FREE:
            return self._str_free()
        elif self.address_format == AddressFormat.LEVEL2:
            return self._str_level2()
        elif self.address_format == AddressFormat.LEVEL3:
            return self._str_level3()
        else:
            raise TypeError()

    def _str_free(self):
        return '{0}'.format((self.raw & 65535))

    def _str_level2(self):
        return '{0}/{1}'.format(
            ((self.raw >> 11) & 15),
            (self.raw & 4095))

    def _str_level3(self):
        return '{0}/{1}/{2}'.format(
            ((self.raw >> 11) & 31),
            ((self.raw >> 8) & 7),
            (self.raw & 255))

    def _str_physical(self):
        return '{0}.{1}.{2}'.format(
            ((self.raw >> 12) & 15),
            ((self.raw >> 8) & 15),
            (self.raw & 255))

    @staticmethod
    def _detect_address_type(address):
        # Physical addresses have either be specified explicitely or
        # in the correct notation. As default an address is a group address.
        if isinstance(address, str) and "." in address:
            return AddressType.PHYSICAL
        elif isinstance(address, Address):
            return address.address_type
        else:
            return AddressType.GROUP
