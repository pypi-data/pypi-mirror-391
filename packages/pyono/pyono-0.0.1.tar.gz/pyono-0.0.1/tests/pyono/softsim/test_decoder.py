import unittest
from src.pyono.softsim.profile import Profile


class TestDecoder(unittest.TestCase):

    def test_decode_profile(self):
        self.assertEqual(
            Profile.decode(
                "01120809101010325406360214980010325476981032140320000000000000000000000000000000000420000102030405060708090A0B0C0D0E0F0520000102030405060708090A0B0C0D0E0F0620000102030405060708090A0B0C0D0E0F080831323334"
            ),
            {
                "iccid": "89000123456789012341",
                "imsi": "001010123456063",
                "opc": "00000000000000000000000000000000",
                "k": "000102030405060708090A0B0C0D0E0F",
                "kic": "000102030405060708090A0B0C0D0E0F",
                "kid": "000102030405060708090A0B0C0D0E0F",
                "pin": "1234",
            },
        )
