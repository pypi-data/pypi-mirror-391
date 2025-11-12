import json
import unittest
import os
from src.pyono.softsim.crypto import Crypto


class TestDecrypt(unittest.TestCase):

    RESOURCES_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "resources"
    )

    def test_create_from_file(self):
        crypto = Crypto.from_rsa_private_file(os.path.join(self.RESOURCES_PATH, "key"))
        self.assertEqual(
            crypto.privkey.n,
            117164719821873799281413604275721006246581623599799326048782984980141803110043106748076522433329919600879182506556280916390441808035568679685773499533506637461213853153058039563768154429970631365281119660068777130945804492133049137853895703389805800379577685220134557780147771594294017366586254175399816936341,
        )
        self.assertTrue(crypto.privkey.can_encrypt())

    def test_create_from_invalid_files(self):
        # Invalid path
        with self.assertRaises(FileNotFoundError):
            Crypto.from_rsa_private_file(
                os.path.join(self.RESOURCES_PATH, "key.notexist")
            )
        # No file
        with self.assertRaises(ValueError):
            Crypto.from_rsa_private_file(None)
        # Invalid file type
        with self.assertRaises(ValueError):
            Crypto.from_rsa_private_file(
                os.path.join(self.RESOURCES_PATH, "key.notkey")
            )
        # Invalid key
        with self.assertRaises(ValueError):
            Crypto.from_rsa_private_file(
                os.path.join(self.RESOURCES_PATH, "key.invalid")
            )

    def test_create_from_key(self):
        crypto = Crypto.from_rsa_private_key(
            """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCm2R0JxqyPfZSGOWUd9vT2fGLOn5IGl1PfuwC4NuH4h0Ozoe71
8iisX1TBoR9RgqxUYfepiW9tjhjqOK3PDfwhWkMHxXPdM+naHV4ZiiNITU6H30St
mh0+GrMuUXWHHqygg+yzcUch2JtCc9rQLCXESOOwpMO1Ui8WXH3gBWM7lQIDAQAB
AoGAQZLg67+ugDKN1fbmu9EcU2dteeGTBY4iA7M+RCglxYR74jSJcxX6UEyjRfpq
EaH20q8yI+qE5ZzMQ/mErfTEGz4Zf4gpoZxv/GKzJ8MULmxO2X+E7Bm0DwjpITeL
bDV7l9597eAWgJJ1inRJ0rpT3F6IGN+5Mj7t3s4IhnX9NkECQQD60xkYA5VF8gbi
uJ1lnygKbL9fFP/Lh4JVZUH2MY2KAcTYGjJvxSVt2DFJFCX/mxif/yvRN4kUqR2c
IAkK91+FAkEAqkpvnDPiNnKVgr+zFVb6VsRs2WAEK8qr43AcwMG3W5lw/ptJ9A51
Of1uFDi5niYo9Rc2wcadXYQV/jlRnGlA0QJBAIQdnSIhAQeOrEHPrFhStOyIy2Rx
0yqJfgUtCMl84GjI9b4+TkLBPS3Wql8r1bgFIbtk1NemwPW4/ne2CA1Wr2ECQAPZ
zxBPNAxbJvpf72LKJrsTkgqQW0fKO3zXKi9JsiXGIIIBbPix4wC+tGCMr9Xdswtn
zPswzJoyxHSNQ0UwNCECQEeLTz8jDz1gHmDZYUT1Pk05FwyK2P7KhciuO5fmD9Gb
Kthw+VViUazIaTshRIqgZeL4x20slSuESZuTFllZCoA=
-----END RSA PRIVATE KEY-----"""
        )
        self.assertEqual(
            crypto.privkey.n,
            117164719821873799281413604275721006246581623599799326048782984980141803110043106748076522433329919600879182506556280916390441808035568679685773499533506637461213853153058039563768154429970631365281119660068777130945804492133049137853895703389805800379577685220134557780147771594294017366586254175399816936341,
        )
        self.assertTrue(crypto.privkey.can_encrypt())

    def test_create_from_invalid_key(self):
        # Invalid key
        with self.assertRaises(ValueError):
            Crypto.from_rsa_private_key(None)
        # Invalid key
        with self.assertRaises(ValueError):
            Crypto.from_rsa_private_key("Invalid key")

    def test_decrypt(self):
        crypto = Crypto.from_rsa_private_file(os.path.join(self.RESOURCES_PATH, "key"))
        self.assertEqual(
            crypto._decrypt(
                "001",
                "cEFafGQ8OipYXKYL1nHLedFYBUwYPrHaJLWW6s/RgjK5waliUN2pcnfzZTwgsVeUClrWYYM5p9dfct7U1qUavWFn91lxKNErTLUZ5X8AMIpjDm8GFQGBG7srVhtaigAjaSsLK4XENQWzz/NEfEmmd9IiQCW0cud+xi7WLJvDOoo=",
            ),
            {
                "iccid": "001",
                "opc": "abcdef",
                "k": "1234567890",
                "ki": "12345678901234567890123456789012",
            },
        )
        self.assertEqual(
            crypto._decrypt(
                "002",
                "DsfnByOMFfh7+OGZ3AofnRUfrvwvWI6uEWjv7F0Em217GqQe0fkxPsDlR1Z8+kdwG+Di2O/b5nZcV7WROkCzJzmYUhy5ItXRtvAXBcEZQe00cFo17jksQLB7HbVmpqIfgkDdqkxIStSXRJI2KrEviPM4pTp4hvoAhmhKr0P/fec=",
            ),
            {
                "iccid": "002",
                "opc": "helloworld",
                "k": "1234567890",
                "ki": "12345678901234567890123456789012",
            },
        )

    def test_next(self):
        crypto = Crypto.from_rsa_private_file(os.path.join(self.RESOURCES_PATH, "key"))
        results = []

        with open(os.path.join(self.RESOURCES_PATH, "profiles.json"), "r") as fd:
            profiles = json.load(fd)

        while profiles is not None:
            result, profiles = crypto.next(profiles)
            results.append(result)

        self.assertEqual(
            results,
            [
                {
                    "opc": "abcdef",
                    "ki": "12345678901234567890123456789012",
                    "k": "1234567890",
                    "iccid": "001",
                },
                {
                    "opc": "helloworld",
                    "ki": "12345678901234567890123456789012",
                    "k": "1234567890",
                    "iccid": "002",
                },
            ],
        )
