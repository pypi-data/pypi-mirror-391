import unittest
from src.pyono.softsim.profile import Profile, ProfileTLVTag


class TestEncoder(unittest.TestCase):

    def test_swap_nibbles(self):
        self.assertEqual(Profile._Profile__swap_nibbles("1234"), "2143")
        self.assertEqual(Profile._Profile__swap_nibbles("1"), "1")
        self.assertEqual(
            Profile._Profile__swap_nibbles("1234567890abcdef"), "2143658709badcfe"
        )

    def test_encode_imsi(self):
        self.assertEqual(
            Profile._Profile__encode_imsi("234602102350049"),
            "082943061220530094",
        )
        self.assertEqual(
            Profile._Profile__encode_imsi("234602102349958"),
            "082943061220439985",
        )

    def test_encode_iccid(self):

        self.assertEqual(
            Profile._Profile__swap_nibbles("89457300000013500452"),
            "98543700000031054025",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_ICCID, "89457300000013500452"
            ),
            "021498543700000031054025",
        )

    def test_encode_tlv(self):
        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_IMSI, "234602102350049"
            ),
            "0112082943061220530094",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_ICCID, "89457300000013500452"
            ),
            "021498543700000031054025",
        )

        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_OPC, "00000000000000000000000000000000"
            ),
            "032000000000000000000000000000000000",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_K, "000102030405060708090A0B0C0D0E0A"
            ),
            "0420000102030405060708090A0B0C0D0E0A",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_KIC, "000102030405060708090A0B0C0D0E0B"
            ),
            "0520000102030405060708090A0B0C0D0E0B",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_KID, "000102030405060708090A0B0C0D0E0C"
            ),
            "0620000102030405060708090A0B0C0D0E0C",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(
                ProfileTLVTag.TLV_SMSP, "000102030405060708090A0B0C0D0E0D"
            ),
            "0720000102030405060708090A0B0C0D0E0D",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(ProfileTLVTag.TLV_PIN, "1234"),
            "080831323334",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(ProfileTLVTag.TLV_ADM, "12345678"),
            "0A103132333435363738",
        )
        self.assertEqual(
            Profile._Profile__encode_tlv_field(ProfileTLVTag.TLV_PUK, "5678"),
            "0B0835363738",
        )

    def test_encode_profile(self):
        self.assertEqual(
            Profile.encode(
                {
                    "iccid": "89000123456789012341",
                    "imsi": "001010123456063",
                    "opc": "00000000000000000000000000000000",
                    "k": "000102030405060708090A0B0C0D0E0F",
                    "kic": "000102030405060708090A0B0C0D0E0F",
                    "kid": "000102030405060708090A0B0C0D0E0F",
                }
            ),
            "01120809101010325406360214980010325476981032140320000000000000000000000000000000000420000102030405060708090A0B0C0D0E0F0520000102030405060708090A0B0C0D0E0F0620000102030405060708090A0B0C0D0E0F",
        )

    def test_convert_profile(self):
        self.assertEqual(
            Profile.convert(
                "89000123456789012341",
                {
                    "iccid": "89000123456789012341",
                    "imsi": "001010123456063",
                    "opc": "00000000000000000000000000000000",
                    "k": "000102030405060708090A0B0C0D0E0F",
                    "kic": "000102030405060708090A0B0C0D0E0F",
                    "kid": "000102030405060708090A0B0C0D0E0F",
                },
            ),
            {
                "iccid": "89000123456789012341",
                "imsi": "001010123456063",
                "opc": "00000000000000000000000000000000",
                "k": "000102030405060708090A0B0C0D0E0F",
                "kic": "000102030405060708090A0B0C0D0E0F",
                "kid": "000102030405060708090A0B0C0D0E0F",
            },
        )
        self.assertEqual(
            Profile.convert(
                "89000123456789012341",
                {
                    "imsi": "001010123456063",
                    "opc": "00000000000000000000000000000000",
                    "k": "000102030405060708090A0B0C0D0E0F",
                    "kic": "000102030405060708090A0B0C0D0E0F",
                    "kid": "000102030405060708090A0B0C0D0E0F",
                },
            ),
            {
                "iccid": "89000123456789012341",
                "imsi": "001010123456063",
                "opc": "00000000000000000000000000000000",
                "k": "000102030405060708090A0B0C0D0E0F",
                "kic": "000102030405060708090A0B0C0D0E0F",
                "kid": "000102030405060708090A0B0C0D0E0F",
            },
        )

    def test_convert_profile_errors(self):
        # Missing ICCID
        with self.assertRaises(ValueError):
            Profile.convert(
                None,
                {
                    "imsi": "001010123456063",
                    "opc": "00000000000000000000000000000000",
                    "k": "000102030405060708090A0B0C0D0E0F",
                    "kic": "000102030405060708090A0B0C0D0E0F",
                    "kid": "000102030405060708090A0B0C0D0E0F",
                },
            )

        # Unmatched ICCID
        with self.assertRaises(ValueError):
            Profile.convert(
                "89000123456789012341",
                {
                    "iccid": "00000000000000000",
                    "imsi": "001010123456063",
                    "opc": "00000000000000000000000000000000",
                    "k": "000102030405060708090A0B0C0D0E0F",
                    "kic": "000102030405060708090A0B0C0D0E0F",
                    "kid": "000102030405060708090A0B0C0D0E0F",
                },
            ),


if __name__ == "__main__":
    unittest.main()
