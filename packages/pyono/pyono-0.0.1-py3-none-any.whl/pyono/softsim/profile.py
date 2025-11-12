from enum import Enum


class ProfileTLVTag(Enum):
    TLV_IMSI = 1
    TLV_ICCID = 2
    TLV_OPC = 3
    TLV_K = 4
    TLV_KIC = 5
    TLV_KID = 6
    TLV_SMSP = 7
    TLV_PIN = 8
    TLV_ADM = 10
    TLV_PUK = 11
    TLV_END = 0xFF


class Profile(object):

    TLV_KEYS = {
        ProfileTLVTag.TLV_IMSI.name: "imsi",
        ProfileTLVTag.TLV_ICCID.name: "iccid",
        ProfileTLVTag.TLV_OPC.name: "opc",
        ProfileTLVTag.TLV_K.name: "k",
        ProfileTLVTag.TLV_KIC.name: "kic",
        ProfileTLVTag.TLV_KID.name: "kid",
        ProfileTLVTag.TLV_SMSP.name: "smsp",
        ProfileTLVTag.TLV_PIN.name: "pin",
        ProfileTLVTag.TLV_ADM.name: "adm",
        ProfileTLVTag.TLV_PUK.name: "puk",
        ProfileTLVTag.TLV_END.name: None,
    }

    # Common helpers
    @staticmethod
    def __swap_nibbles(s: str) -> str:
        """
        Swap hexstring nibbles to simulate endianess byteswap

        Args:
            s (str): Hexadecimal string to swap

        Returns:
            str: Swapped hexadecimal string
        """
        data = list(s)
        for i in range(0, len(s) - 1, 2):
            data[i], data[i + 1] = data[i + 1], data[i]
        return "".join(data)

    # Encoders
    @staticmethod
    def __encode_tlv(tag: int, value: str) -> str:
        return f"{tag:02x}{len(value):02x}{value}"

    @staticmethod
    def __encode_imsi(imsi: str) -> str:
        l = (len(imsi) + 1) // 2  # Half round up
        oe = len(imsi) & 1
        header = f"{(oe << 3) | 1:x}" + imsi.ljust(15, "f")
        swapped = __class__.__swap_nibbles(header)
        return f"{l:02x}{swapped}"

    @staticmethod
    def __encode_tlv_field(tag: ProfileTLVTag, data: str) -> str:

        # Specfic tags preprocessing
        if tag == ProfileTLVTag.TLV_IMSI:
            data = __class__.__encode_imsi(data)
        elif tag == ProfileTLVTag.TLV_ICCID:
            data = __class__.__swap_nibbles(data)
        elif tag in [
            ProfileTLVTag.TLV_PIN,
            ProfileTLVTag.TLV_PUK,
            ProfileTLVTag.TLV_ADM,
        ]:
            data = data.encode().hex()

        return __class__.__encode_tlv(tag.value, data).upper()

    # Decoders
    @staticmethod
    def __decode_tlv_tag(data: bytes) -> tuple[ProfileTLVTag, int]:
        tag = data[0]
        i = 1

        # Handle multi-byte tag (if bits 5-1 of first byte are all 1)
        if (tag & 0x1F) == 0x1F:
            tag_bytes = [tag]
            while data[i] & 0x80:  # continuation bit
                tag_bytes.append(data[i])
                i = i + 1
            tag_bytes.append(data[i])
            i = i + 1
            tag = bytes(tag_bytes).hex().upper()
        else:
            tag = f"{tag:02X}"

        return ProfileTLVTag(int(tag, base=16)), i

    @staticmethod
    def __decode_tlv_length(data: bytes) -> tuple[str, int]:

        length = data[0]
        i = 1

        if length & 0x80:  # multi-byte length
            num_len_bytes = length & 0x7F
            length = int.from_bytes(data[i : i + num_len_bytes], "big")
            i += num_len_bytes

        return length, i

    @staticmethod
    def __decode_tlv_field(tag: ProfileTLVTag, data: bytes) -> tuple[bytes, dict]:

        if tag == ProfileTLVTag.TLV_IMSI:
            value = __class__.__swap_nibbles(data.hex().upper())
            value = value[3:]

        elif tag == ProfileTLVTag.TLV_ICCID:
            value = __class__.__swap_nibbles(data.hex().upper())

        elif tag in [
            ProfileTLVTag.TLV_PIN,
            ProfileTLVTag.TLV_PUK,
            ProfileTLVTag.TLV_ADM,
        ]:
            value = data.decode().upper()

        else:
            value = data.hex().upper()

        return {__class__.TLV_KEYS[tag.name]: value}, len(data)

    @staticmethod
    def encode(decoded: dict) -> str:
        """
        Encode JSON-like profile to softSIM-compatible TLV string

        Args:
            profile (dict): JSON-like profile

        Returns:
            str: TLV encoded softSIM profile
        """
        encoded = ""

        # Parse profile by TLV tag order instead of profile keys to ensure consistent TLV frame order
        for tag in ProfileTLVTag:
            if __class__.TLV_KEYS[tag.name] in decoded:
                encoded = encoded + __class__.__encode_tlv_field(
                    tag, decoded[__class__.TLV_KEYS[tag.name]]
                )

        return encoded

    @staticmethod
    def decode(encoded: str) -> dict:
        """
        Decode TLV softSIM profile

        Args:
            profile (str): Encoded TLV softSIM profile

        Returns:
            dict: JSON-like decoded profile
        """
        decoded = dict()
        tlv_data = bytes.fromhex(encoded)

        while len(tlv_data):

            # Decode TLV fields and pop them once processed
            tag, off = __class__.__decode_tlv_tag(tlv_data)
            tlv_data = tlv_data[off:]

            length, off = __class__.__decode_tlv_length(tlv_data)
            tlv_data = tlv_data[off:]

            # Use half length as hexstr uses two char by encoded byte
            value, off = __class__.__decode_tlv_field(tag, tlv_data[: (length // 2)])
            tlv_data = tlv_data[off:]

            decoded.update(value)

        return decoded

    def convert(iccid: str, profile: dict) -> dict:
        """
        Convert softSIM decrypted profile into TLV encodable one

        Args:
            iccid (str): Encoded TLV softSIM profile
            decoded (dict): Encoded TLV softSIM profile

        Returns:
            dict: JSON-like, TLV-encodable profile
        """
        if not "iccid" in profile:
            if iccid is None:
                raise ValueError("ICCID not provided, nor present in input profile")
            profile.update({"iccid": iccid})

        if iccid is not None and iccid != profile["iccid"]:
            raise ValueError("Unmatched ICCIDs")

        return profile
