try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    buffer
except NameError:
    buffer = memoryview

import os
import array
import pytest
import hashlib

from .keys import VerifyingKey, SigningKey, MalformedPointError
from .der import (
    unpem,
    UnexpectedDER,
    encode_sequence,
    encode_oid,
    encode_bitstring,
)
from .util import (
    sigencode_string,
    sigencode_der,
    sigencode_strings,
    sigdecode_string,
    sigdecode_der,
    sigdecode_strings,
)
from .curves import NIST256p, Curve, BRAINPOOLP160r1, Ed25519, Ed448
from .ellipticcurve import Point, PointJacobi, CurveFp, INFINITY
from .ecdsa import generator_brainpoolp160r1


class TestVerifyingKeyFromString(unittest.TestCase):
    """
    Verify that ecdsa.keys.VerifyingKey.from_string() can be used with
    bytes-like objects
    """

    @classmethod
    def setUpClass(cls):
        cls.key_bytes = (
            b"\x04L\xa2\x95\xdb\xc7Z\xd7\x1f\x93\nz\xcf\x97\xcf"
            b"\xd7\xc2\xd9o\xfe8}X!\xae\xd4\xfah\xfa^\rpI\xba\xd1"
            b"Y\xfb\x92xa\xebo+\x9cG\xfav\xca"
        )
        cls.vk = VerifyingKey.from_string(cls.key_bytes)

    def test_bytes(self):
        self.assertIsNotNone(self.vk)
        self.assertIsInstance(self.vk, VerifyingKey)
        self.assertEqual(
            self.vk.pubkey.point.x(),
            105419898848891948935835657980914000059957975659675736097,
        )
        self.assertEqual(
            self.vk.pubkey.point.y(),
            4286866841217412202667522375431381222214611213481632495306,
        )

    def test_bytes_memoryview(self):
        vk = VerifyingKey.from_string(buffer(self.key_bytes))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytearray(self):
        vk = VerifyingKey.from_string(bytearray(self.key_bytes))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytesarray_memoryview(self):
        vk = VerifyingKey.from_string(buffer(bytearray(self.key_bytes)))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_array_array_of_bytes(self):
        arr = array.array("B", self.key_bytes)
        vk = VerifyingKey.from_string(arr)

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_array_array_of_bytes_memoryview(self):
        arr = array.array("B", self.key_bytes)
        vk = VerifyingKey.from_string(buffer(arr))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_array_array_of_ints(self):
        arr = array.array("I", self.key_bytes)
        vk = VerifyingKey.from_string(arr)

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_array_array_of_ints_memoryview(self):
        arr = array.array("I", self.key_bytes)
        vk = VerifyingKey.from_string(buffer(arr))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytes_uncompressed(self):
        vk = VerifyingKey.from_string(b"\x04" + self.key_bytes)

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytearray_uncompressed(self):
        vk = VerifyingKey.from_string(bytearray(b"\x04" + self.key_bytes))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytes_compressed(self):
        vk = VerifyingKey.from_string(b"\x02" + self.key_bytes[:24])

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytearray_compressed(self):
        vk = VerifyingKey.from_string(bytearray(b"\x02" + self.key_bytes[:24]))

        self.assertEqual(self.vk.to_string(), vk.to_string())


class TestVerifyingKeyFromDer(unittest.TestCase):
    """
    Verify that ecdsa.keys.VerifyingKey.from_der() can be used with
    bytes-like objects.
    """

    @classmethod
    def setUpClass(cls):
        prv_key_str = (
            "-----BEGIN EC PRIVATE KEY-----\n"
            "MF8CAQEEGF7IQgvW75JSqULpiQQ8op9WH6Uldw6xxaAKBggqhkjOPQMBAaE0AzIA\n"
            "BLiBd9CE7xf15FY5QIAoNg+fWbSk1yZOYtoGUdzkejWkxbRc9RWTQjqLVXucIJnz\n"
            "bA==\n"
            "-----END EC PRIVATE KEY-----\n"
        )
        key_str = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEuIF30ITvF/XkVjlAgCg2D59ZtKTX\n"
            "Jk5i2gZR3OR6NaTFtFz1FZNCOotVe5wgmfNs\n"
            "-----END PUBLIC KEY-----\n"
        )
        cls.key_pem = key_str

        cls.key_bytes = unpem(key_str)
        assert isinstance(cls.key_bytes, bytes)
        cls.vk = VerifyingKey.from_pem(key_str)
        cls.sk = SigningKey.from_pem(prv_key_str)

        key_str = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE4H3iRbG4TSrsSRb/gusPQB/4YcN8\n"
            "Poqzgjau4kfxBPyZimeRfuY/9g/wMmPuhGl4BUve51DsnKJFRr8psk0ieA==\n"
            "-----END PUBLIC KEY-----\n"
        )
        cls.vk2 = VerifyingKey.from_pem(key_str)

        cls.sk2 = SigningKey.generate(vk.curve)

    def test_load_key_with_explicit_parameters(self):
        pub_key_str = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MIIBSzCCAQMGByqGSM49AgEwgfcCAQEwLAYHKoZIzj0BAQIhAP////8AAAABAAAA\n"
            "AAAAAAAAAAAA////////////////MFsEIP////8AAAABAAAAAAAAAAAAAAAA////\n"
            "///////////8BCBaxjXYqjqT57PrvVV2mIa8ZR0GsMxTsPY7zjw+J9JgSwMVAMSd\n"
            "NgiG5wSTamZ44ROdJreBn36QBEEEaxfR8uEsQkf4vOblY6RA8ncDfYEt6zOg9KE5\n"
            "RdiYwpZP40Li/hp/m47n60p8D54WK84zV2sxXs7LtkBoN79R9QIhAP////8AAAAA\n"
            "//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABIr1UkgYs5jmbFc7it1/YI2X\n"
            "T//IlaEjMNZft1owjqpBYH2ErJHk4U5Pp4WvWq1xmHwIZlsH7Ig4KmefCfR6SmU=\n"
            "-----END PUBLIC KEY-----"
        )
        pk = VerifyingKey.from_pem(pub_key_str)

        pk_exp = VerifyingKey.from_string(
            b"\x04\x8a\xf5\x52\x48\x18\xb3\x98\xe6\x6c\x57\x3b\x8a\xdd\x7f"
            b"\x60\x8d\x97\x4f\xff\xc8\x95\xa1\x23\x30\xd6\x5f\xb7\x5a\x30"
            b"\x8e\xaa\x41\x60\x7d\x84\xac\x91\xe4\xe1\x4e\x4f\xa7\x85\xaf"
            b"\x5a\xad\x71\x98\x7c\x08\x66\x5b\x07\xec\x88\x38\x2a\x67\x9f"
            b"\x09\xf4\x7a\x4a\x65",
            curve=NIST256p,
        )
        self.assertEqual(pk, pk_exp)

    def test_load_key_with_explicit_with_explicit_disabled(self):
        pub_key_str = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MIIBSzCCAQMGByqGSM49AgEwgfcCAQEwLAYHKoZIzj0BAQIhAP////8AAAABAAAA\n"
            "AAAAAAAAAAAA////////////////MFsEIP////8AAAABAAAAAAAAAAAAAAAA////\n"
            "///////////8BCBaxjXYqjqT57PrvVV2mIa8ZR0GsMxTsPY7zjw+J9JgSwMVAMSd\n"
            "NgiG5wSTamZ44ROdJreBn36QBEEEaxfR8uEsQkf4vOblY6RA8ncDfYEt6zOg9KE5\n"
            "RdiYwpZP40Li/hp/m47n60p8D54WK84zV2sxXs7LtkBoN79R9QIhAP////8AAAAA\n"
            "//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABIr1UkgYs5jmbFc7it1/YI2X\n"
            "T//IlaEjMNZft1owjqpBYH2ErJHk4U5Pp4WvWq1xmHwIZlsH7Ig4KmefCfR6SmU=\n"
            "-----END PUBLIC KEY-----"
        )
        with self.assertRaises(UnexpectedDER):
            VerifyingKey.from_pem(
                pub_key_str, valid_curve_encodings=["named_curve"]
            )

    def test_load_key_with_disabled_format(self):
        with self.assertRaises(MalformedPointError) as e:
            VerifyingKey.from_der(self.key_bytes, valid_encodings=["raw"])

        self.assertIn("enabled (raw) encodings", str(e.exception))

    def test_custom_hashfunc(self):
        vk = VerifyingKey.from_der(self.key_bytes, hashlib.sha256)

        self.assertIs(vk.default_hashfunc, hashlib.sha256)

    def test_from_pem_with_custom_hashfunc(self):
        vk = VerifyingKey.from_pem(self.key_pem, hashlib.sha256)

        self.assertIs(vk.default_hashfunc, hashlib.sha256)

    def test_bytes(self):
        vk = VerifyingKey.from_der(self.key_bytes)

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytes_memoryview(self):
        vk = VerifyingKey.from_der(buffer(self.key_bytes))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytearray(self):
        vk = VerifyingKey.from_der(bytearray(self.key_bytes))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_bytesarray_memoryview(self):
        vk = VerifyingKey.from_der(buffer(bytearray(self.key_bytes)))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_array_array_of_bytes(self):
        arr = array.array("B", self.key_bytes)
        vk = VerifyingKey.from_der(arr)

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_array_array_of_bytes_memoryview(self):
        arr = array.array("B", self.key_bytes)
        vk = VerifyingKey.from_der(buffer(arr))

        self.assertEqual(self.vk.to_string(), vk.to_string())

    def test_equality_on_verifying_keys(self):
        self.assertEqual(self.vk, self.sk.get_verifying_key())

    def test_inequality_on_verifying_keys(self):
        self.assertNotEqual(self.vk, self.vk2)

    def test_inequality_on_verifying_keys_not_implemented(self):
        self.assertNotEqual(self.vk, None)

    def test_VerifyingKey_inequality_on_same_curve(self):
        self.assertNotEqual(self.vk, self.sk2.verifying_key)

    def test_SigningKey_inequality_on_same_curve(self):
        self.assertNotEqual(self.sk, self.sk2)

    def test_inequality_on_wrong_types(self):
        self.assertNotEqual(self.vk, self.sk)

    def test_from_public_point_old(self):
        pj = self.vk.pubkey.point
        point = Point(pj.curve(), pj.x(), pj.y())

        vk = VerifyingKey.from_public_point(point, self.vk.curve)

        self.assertEqual(vk, self.vk)

    def test_ed25519_VerifyingKey_repr__(self):
        sk = SigningKey.from_string(Ed25519.generator.to_bytes(), Ed25519)
        string = repr(sk.verifying_key)

        self.assertEqual(
            "VerifyingKey.from_string("
            "bytearray(b'K\\x0c\\xfbZH\\x8e\\x8c\\x8c\\x07\\xee\\xda\\xfb"
            "\\xe1\\x97\\xcd\\x90\\x18\\x02\\x15h]\\xfe\\xbe\\xcbB\\xba\\xe6r"
            "\\x10\\xae\\xf1P'), Ed25519, None)",
            string,
        )

    def test_edwards_from_public_point(self):
        point = Ed25519.generator
        with self.assertRaises(ValueError) as e:
            VerifyingKey.from_public_point(point, Ed25519)

        self.assertIn("incompatible with Edwards", str(e.exception))

    def test_edwards_precompute_no_side_effect(self):
        sk = SigningKey.from_string(Ed25519.generator.to_bytes(), Ed25519)
        vk = sk.verifying_key
        vk2 = VerifyingKey.from_string(vk.to_string(), Ed25519)
        vk.precompute()

        self.assertEqual(vk, vk2)

    def test_parse_malfomed_eddsa_der_pubkey(self):
        der_str = encode_sequence(
            encode_sequence(encode_oid(*Ed25519.oid)),
            encode_bitstring(bytes(Ed25519.generator.to_bytes()), 0),
            encode_bitstring(b"\x00", 0),
        )

        with self.assertRaises(UnexpectedDER) as e:
            VerifyingKey.from_der(der_str)

        self.assertIn("trailing junk after public key", str(e.exception))

    def test_edwards_from_public_key_recovery(self):
        with self.assertRaises(ValueError) as e:
            VerifyingKey.from_public_key_recovery(b"", b"", Ed25519)

        self.assertIn("unsupported for Edwards", str(e.exception))

    def test_edwards_from_public_key_recovery_with_digest(self):
        with self.assertRaises(ValueError) as e:
            VerifyingKey.from_public_key_recovery_with_digest(
                b"", b"", Ed25519
            )

        self.assertIn("unsupported for Edwards", str(e.exception))

    def test_load_ed25519_from_pem(self):
        vk_pem = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MCowBQYDK2VwAyEAIwBQ0NZkIiiO41WJfm5BV42u3kQm7lYnvIXmCy8qy2U=\n"
            "-----END PUBLIC KEY-----\n"
        )

        vk = VerifyingKey.from_pem(vk_pem)

        self.assertIsInstance(vk.curve, Curve)
        self.assertIs(vk.curve, Ed25519)

        vk_str = (
            b"\x23\x00\x50\xd0\xd6\x64\x22\x28\x8e\xe3\x55\x89\x7e\x6e\x41\x57"
            b"\x8d\xae\xde\x44\x26\xee\x56\x27\xbc\x85\xe6\x0b\x2f\x2a\xcb\x65"
        )

        vk_2 = VerifyingKey.from_string(vk_str, Ed25519)

        self.assertEqual(vk, vk_2)

    def test_export_ed255_to_pem(self):
        vk_str = (
            b"\x23\x00\x50\xd0\xd6\x64\x22\x28\x8e\xe3\x55\x89\x7e\x6e\x41\x57"
            b"\x8d\xae\xde\x44\x26\xee\x56\x27\xbc\x85\xe6\x0b\x2f\x2a\xcb\x65"
        )

        vk = VerifyingKey.from_string(vk_str, Ed25519)

        vk_pem = (
            b"-----BEGIN PUBLIC KEY-----\n"
            b"MCowBQYDK2VwAyEAIwBQ0NZkIiiO41WJfm5BV42u3kQm7lYnvIXmCy8qy2U=\n"
            b"-----END PUBLIC KEY-----\n"
        )

        self.assertEqual(vk_pem, vk.to_pem())

    def test_ed25519_export_import(self):
        sk = SigningKey.generate(Ed25519)
        vk = sk.verifying_key

        vk2 = VerifyingKey.from_pem(vk.to_pem())

        self.assertEqual(vk, vk2)

    def test_ed25519_sig_verify(self):
        vk_pem = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MCowBQYDK2VwAyEAIwBQ0NZkIiiO41WJfm5BV42u3kQm7lYnvIXmCy8qy2U=\n"
            "-----END PUBLIC KEY-----\n"
        )

        vk = VerifyingKey.from_pem(vk_pem)

        data = b"data\n"

        # signature created by OpenSSL 3.0.0 beta1
        sig = (
            b"\x64\x47\xab\x6a\x33\xcd\x79\x45\xad\x98\x11\x6c\xb9\xf2\x20\xeb"
            b"\x90\xd6\x50\xe3\xc7\x8f\x9f\x60\x10\xec\x75\xe0\x2f\x27\xd3\x96"
            b"\xda\xe8\x58\x7f\xe0\xfe\x46\x5c\x81\xef\x50\xec\x29\x9f\xae\xd5"
            b"\xad\x46\x3c\x91\x68\x83\x4d\xea\x8d\xa8\x19\x04\x04\x79\x03\x0b"
        )

        self.assertTrue(vk.verify(sig, data))

    def test_ed448_from_pem(self):
        pem_str = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MEMwBQYDK2VxAzoAeQtetSu7CMEzE+XWB10Bg47LCA0giNikOxHzdp+tZ/eK/En0\n"
            "dTdYD2ll94g58MhSnBiBQB9A1MMA\n"
            "-----END PUBLIC KEY-----\n"
        )

        vk = VerifyingKey.from_pem(pem_str)

        self.assertIsInstance(vk.curve, Curve)
        self.assertIs(vk.curve, Ed448)

        vk_str = (
            b"\x79\x0b\x5e\xb5\x2b\xbb\x08\xc1\x33\x13\xe5\xd6\x07\x5d\x01\x83"
            b"\x8e\xcb\x08\x0d\x20\x88\xd8\xa4\x3b\x11\xf3\x76\x9f\xad\x67\xf7"
            b"\x8a\xfc\x49\xf4\x75\x37\x58\x0f\x69\x65\xf7\x88\x39\xf0\xc8\x52"
            b"\x9c\x18\x81\x40\x1f\x40\xd4\xc3\x00"
        )

        vk2 = VerifyingKey.from_string(vk_str, Ed448)

        self.assertEqual(vk, vk2)

    def test_ed448_to_pem(self):
        vk_str = (
            b"\x79\x0b\x5e\xb5\x2b\xbb\x08\xc1\x33\x13\xe5\xd6\x07\x5d\x01\x83"
            b"\x8e\xcb\x08\x0d\x20\x88\xd8\xa4\x3b\x11\xf3\x76\x9f\xad\x67\xf7"
            b"\x8a\xfc\x49\xf4\x75\x37\x58\x0f\x69\x65\xf7\x88\x39\xf0\xc8\x52"
            b"\x9c\x18\x81\x40\x1f\x40\xd4\xc3\x00"
        )
        vk = VerifyingKey.from_string(vk_str, Ed448)

        vk_pem = (
            b"-----BEGIN PUBLIC KEY-----\n"
            b"MEMwBQYDK2VxAzoAeQtetSu7CMEzE+XWB10Bg47LCA0giNikOxHzdp+tZ/eK/En0\n"
            b"dTdYD2ll94g58MhSnBiBQB9A1MMA\n"
            b"-----END PUBLIC KEY-----\n"
        )

        self.assertEqual(vk_pem, vk.to_pem())

    def test_ed448_export_import(self):
        sk = SigningKey.generate(Ed448)
        vk = sk.verifying_key

        vk2 = VerifyingKey.from_pem(vk.to_pem())

        self.assertEqual(vk, vk2)

    def test_ed448_sig_verify(self):
        pem_str = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MEMwBQYDK2VxAzoAeQtetSu7CMEzE+XWB10Bg47LCA0giNikOxHzdp+tZ/eK/En0\n"
            "dTdYD2ll94g58MhSnBiBQB9A1MMA\n"
            "-----END PUBLIC KEY-----\n"
        )

        vk = VerifyingKey.from_pem(pem_str)

        data = b"data\n"

        # signature created by OpenSSL 3.0.0 beta1
        sig = (
            b"\x68\xed\x2c\x70\x35\x22\xca\x1c\x35\x03\xf3\xaa\x51\x33\x3d\x00"
            b"\xc0\xae\xb0\x54\xc5\xdc\x7f\x6f\x30\x57\xb4\x1d\xcb\xe9\xec\xfa"
            b"\xc8\x45\x3e\x51\xc1\xcb\x60\x02\x6a\xd0\x43\x11\x0b\x5f\x9b\xfa"
            b"\x32\x88\xb2\x38\x6b\xed\xac\x09\x00\x78\xb1\x7b\x5d\x7e\xf8\x16"
            b"\x31\xdd\x1b\x3f\x98\xa0\xce\x19\xe7\xd8\x1c\x9f\x30\xac\x2f\xd4"
            b"\x1e\x55\xbf\x21\x98\xf6\x4c\x8c\xbe\x81\xa5\x2d\x80\x4c\x62\x53"
            b"\x91\xd5\xee\x03\x30\xc6\x17\x66\x4b\x9e\x0c\x8d\x40\xd0\xad\xae"
            b"\x0a\x00"
        )

        self.assertTrue(vk.verify(sig, data))


class TestSigningKey(unittest.TestCase):
    """
    Verify that ecdsa.keys.SigningKey.from_der() can be used with
    bytes-like objects.
    """

    @classmethod
    def setUpClass(cls):
        prv_key_str = (
            "-----BEGIN EC PRIVATE KEY-----\n"
            "MF8CAQEEGF7IQgvW75JSqULpiQQ8op9WH6Uldw6xxaAKBggqhkjOPQMBAaE0AzIA\n"
            "BLiBd9CE7xf15FY5QIAoNg+fWbSk1yZOYtoGUdzkejWkxbRc9RWTQjqLVXucIJnz\n"
            "bA==\n"
            "-----END EC PRIVATE KEY-----\n"
        )
        cls.sk1 = SigningKey.from_pem(prv_key_str)

        prv_key_str = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MG8CAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQEEVTBTAgEBBBheyEIL1u+SUqlC6YkE\n"
            "PKKfVh+lJXcOscWhNAMyAAS4gXfQhO8X9eRWOUCAKDYPn1m0pNcmTmLaBlHc5Ho1\n"
            "pMW0XPUVk0I6i1V7nCCZ82w=\n"
            "-----END PRIVATE KEY-----\n"
        )
        cls.sk1_pkcs8 = SigningKey.from_pem(prv_key_str)

        prv_key_str = (
            "-----BEGIN EC PRIVATE KEY-----\n"
            "MHcCAQEEIKlL2EAm5NPPZuXwxRf4nXMk0A80y6UUbiQ17be/qFhRoAoGCCqGSM49\n"
            "AwEHoUQDQgAE4H3iRbG4TSrsSRb/gusPQB/4YcN8Poqzgjau4kfxBPyZimeRfuY/\n"
            "9g/wMmPuhGl4BUve51DsnKJFRr8psk0ieA==\n"
            "-----END EC PRIVATE KEY-----\n"
        )
        cls.sk2 = SigningKey.from_pem(prv_key_str)

    def test_decoding_explicit_curve_parameters(self):
        prv_key_str = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MIIBeQIBADCCAQMGByqGSM49AgEwgfcCAQEwLAYHKoZIzj0BAQIhAP////8AAAAB\n"
            "AAAAAAAAAAAAAAAA////////////////MFsEIP////8AAAABAAAAAAAAAAAAAAAA\n"
            "///////////////8BCBaxjXYqjqT57PrvVV2mIa8ZR0GsMxTsPY7zjw+J9JgSwMV\n"
            "AMSdNgiG5wSTamZ44ROdJreBn36QBEEEaxfR8uEsQkf4vOblY6RA8ncDfYEt6zOg\n"
            "9KE5RdiYwpZP40Li/hp/m47n60p8D54WK84zV2sxXs7LtkBoN79R9QIhAP////8A\n"
            "AAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBBG0wawIBAQQgIXtREfUmR16r\n"
            "ZbmvDGD2lAEFPZa2DLPyz0czSja58yChRANCAASK9VJIGLOY5mxXO4rdf2CNl0//\n"
            "yJWhIzDWX7daMI6qQWB9hKyR5OFOT6eFr1qtcZh8CGZbB+yIOCpnnwn0ekpl\n"
            "-----END PRIVATE KEY-----\n"
        )

        sk = SigningKey.from_pem(prv_key_str)

        sk2 = SigningKey.from_string(
            b"\x21\x7b\x51\x11\xf5\x26\x47\x5e\xab\x65\xb9\xaf\x0c\x60\xf6"
            b"\x94\x01\x05\x3d\x96\xb6\x0c\xb3\xf2\xcf\x47\x33\x4a\x36\xb9"
            b"\xf3\x20",
            curve=NIST256p,
        )

        self.assertEqual(sk, sk2)

    def test_decoding_explicit_curve_parameters_with_explicit_disabled(self):
        prv_key_str = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MIIBeQIBADCCAQMGByqGSM49AgEwgfcCAQEwLAYHKoZIzj0BAQIhAP////8AAAAB\n"
            "AAAAAAAAAAAAAAAA////////////////MFsEIP////8AAAABAAAAAAAAAAAAAAAA\n"
            "///////////////8BCBaxjXYqjqT57PrvVV2mIa8ZR0GsMxTsPY7zjw+J9JgSwMV\n"
            "AMSdNgiG5wSTamZ44ROdJreBn36QBEEEaxfR8uEsQkf4vOblY6RA8ncDfYEt6zOg\n"
            "9KE5RdiYwpZP40Li/hp/m47n60p8D54WK84zV2sxXs7LtkBoN79R9QIhAP////8A\n"
            "AAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBBG0wawIBAQQgIXtREfUmR16r\n"
            "ZbmvDGD2lAEFPZa2DLPyz0czSja58yChRANCAASK9VJIGLOY5mxXO4rdf2CNl0//\n"
            "yJWhIzDWX7daMI6qQWB9hKyR5OFOT6eFr1qtcZh8CGZbB+yIOCpnnwn0ekpl\n"
            "-----END PRIVATE KEY-----\n"
        )

        with self.assertRaises(UnexpectedDER):
            SigningKey.from_pem(
                prv_key_str, valid_curve_encodings=["named_curve"]
            )

    def test_equality_on_signing_keys(self):
        sk = SigningKey.from_secret_exponent(
            self.sk1.privkey.secret_multiplier, self.sk1.curve
        )
        self.assertEqual(self.sk1, sk)
        self.assertEqual(self.sk1_pkcs8, sk)

    def test_verify_with_empty_message(self):
        sig = self.sk1.sign(b"")

        self.assertTrue(sig)

        vk = self.sk1.verifying_key

        self.assertTrue(vk.verify(sig, b""))

    def test_verify_with_precompute(self):
        sig = self.sk1.sign(b"message")

        vk = self.sk1.verifying_key

        vk.precompute()

        self.assertTrue(vk.verify(sig, b"message"))

    def test_compare_verifying_key_with_precompute(self):
        vk1 = self.sk1.verifying_key
        vk1.precompute()

        vk2 = self.sk1_pkcs8.verifying_key

        self.assertEqual(vk1, vk2)

    def test_verify_with_lazy_precompute(self):
        sig = self.sk2.sign(b"other message")

        vk = self.sk2.verifying_key

        vk.precompute(lazy=True)

        self.assertTrue(vk.verify(sig, b"other message"))

    def test_inequality_on_signing_keys(self):
        self.assertNotEqual(self.sk1, self.sk2)

    def test_inequality_on_signing_keys_not_implemented(self):
        self.assertNotEqual(self.sk1, None)

    def test_ed25519_from_pem(self):
        pem_str = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MC4CAQAwBQYDK2VwBCIEIDS6x9FO1PG8T4xIPg8Zd0z8uL6sVGZFEZrX17gHC/XU\n"
            "-----END PRIVATE KEY-----\n"
        )

        sk = SigningKey.from_pem(pem_str)

        sk_str = SigningKey.from_string(
            b"\x34\xBA\xC7\xD1\x4E\xD4\xF1\xBC\x4F\x8C\x48\x3E\x0F\x19\x77\x4C"
            b"\xFC\xB8\xBE\xAC\x54\x66\x45\x11\x9A\xD7\xD7\xB8\x07\x0B\xF5\xD4",
            Ed25519,
        )

        self.assertEqual(sk, sk_str)

    def test_ed25519_to_pem(self):
        sk = SigningKey.from_string(
            b"\x34\xBA\xC7\xD1\x4E\xD4\xF1\xBC\x4F\x8C\x48\x3E\x0F\x19\x77\x4C"
            b"\xFC\xB8\xBE\xAC\x54\x66\x45\x11\x9A\xD7\xD7\xB8\x07\x0B\xF5\xD4",
            Ed25519,
        )

        pem_str = (
            b"-----BEGIN PRIVATE KEY-----\n"
            b"MC4CAQAwBQYDK2VwBCIEIDS6x9FO1PG8T4xIPg8Zd0z8uL6sVGZFEZrX17gHC/XU\n"
            b"-----END PRIVATE KEY-----\n"
        )

        self.assertEqual(sk.to_pem(format="pkcs8"), pem_str)

    def test_ed25519_to_and_from_pem(self):
        sk = SigningKey.generate(Ed25519)

        decoded = SigningKey.from_pem(sk.to_pem(format="pkcs8"))

        self.assertEqual(sk, decoded)

    def test_ed448_from_pem(self):
        pem_str = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MEcCAQAwBQYDK2VxBDsEOTyFuXqFLXgJlV8uDqcOw9nG4IqzLiZ/i5NfBDoHPzmP\n"
            "OP0JMYaLGlTzwovmvCDJ2zLaezu9NLz9aQ==\n"
            "-----END PRIVATE KEY-----\n"
        )
        sk = SigningKey.from_pem(pem_str)

        sk_str = SigningKey.from_string(
            b"\x3C\x85\xB9\x7A\x85\x2D\x78\x09\x95\x5F\x2E\x0E\xA7\x0E\xC3\xD9"
            b"\xC6\xE0\x8A\xB3\x2E\x26\x7F\x8B\x93\x5F\x04\x3A\x07\x3F\x39\x8F"
            b"\x38\xFD\x09\x31\x86\x8B\x1A\x54\xF3\xC2\x8B\xE6\xBC\x20\xC9\xDB"
            b"\x32\xDA\x7B\x3B\xBD\x34\xBC\xFD\x69",
            Ed448,
        )

        self.assertEqual(sk, sk_str)

    def test_ed448_to_pem(self):
        sk = SigningKey.from_string(
            b"\x3C\x85\xB9\x7A\x85\x2D\x78\x09\x95\x5F\x2E\x0E\xA7\x0E\xC3\xD9"
            b"\xC6\xE0\x8A\xB3\x2E\x26\x7F\x8B\x93\x5F\x04\x3A\x07\x3F\x39\x8F"
            b"\x38\xFD\x09\x31\x86\x8B\x1A\x54\xF3\xC2\x8B\xE6\xBC\x20\xC9\xDB"
            b"\x32\xDA\x7B\x3B\xBD\x34\xBC\xFD\x69",
            Ed448,
        )
        pem_str = (
            b"-----BEGIN PRIVATE KEY-----\n"
            b"MEcCAQAwBQYDK2VxBDsEOTyFuXqFLXgJlV8uDqcOw9nG4IqzLiZ/i5NfBDoHPzmP\n"
            b"OP0JMYaLGlTzwovmvCDJ2zLaezu9NLz9aQ==\n"
            b"-----END PRIVATE KEY-----\n"
        )

        self.assertEqual(sk.to_pem(format="pkcs8"), pem_str)

    def test_ed448_encode_decode(self):
        sk = SigningKey.generate(Ed448)

        decoded = SigningKey.from_pem(sk.to_pem(format="pkcs8"))

        self.assertEqual(decoded, sk)


class TestTrivialCurve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # To test what happens with r or s in signing happens to be zero we
        # need to find a scalar that creates one of the points on a curve that
        # has x coordinate equal to zero.
        # Even for secp112r2 curve that's non trivial so use this toy
        # curve, for which we can iterate over all points quickly
        curve = CurveFp(163, 84, 58)
        gen = PointJacobi(curve, 2, 87, 1, 167, generator=True)

        cls.toy_curve = Curve("toy_p8", curve, gen, (1, 2, 0))

        cls.sk = SigningKey.from_secret_exponent(
            140,
            cls.toy_curve,
            hashfunc=hashlib.sha1,
        )

    def test_generator_sanity(self):
        gen = self.toy_curve.generator

        self.assertEqual(gen * gen.order(), INFINITY)

    def test_public_key_sanity(self):
        self.assertEqual(self.sk.verifying_key.to_string(), b"\x98\x1e")

    def test_deterministic_sign(self):
        sig = self.sk.sign_deterministic(b"message")

        self.assertEqual(sig, b"-.")

        self.assertTrue(self.sk.verifying_key.verify(sig, b"message"))

    def test_deterministic_sign_random_message(self):
        msg = os.urandom(32)
        sig = self.sk.sign_deterministic(msg)
        self.assertEqual(len(sig), 2)
        self.assertTrue(self.sk.verifying_key.verify(sig, msg))

    def test_deterministic_sign_that_rises_R_zero_error(self):
        # the raised RSZeroError is caught and handled internally by
        # sign_deterministic methods
        msg = b"\x00\x4f"
        sig = self.sk.sign_deterministic(msg)
        self.assertEqual(sig, b"\x36\x9e")
        self.assertTrue(self.sk.verifying_key.verify(sig, msg))

    def test_deterministic_sign_that_rises_S_zero_error(self):
        msg = b"\x01\x6d"
        sig = self.sk.sign_deterministic(msg)
        self.assertEqual(sig, b"\x49\x6c")
        self.assertTrue(self.sk.verifying_key.verify(sig, msg))


# test VerifyingKey.verify()
prv_key_str = (
    "-----BEGIN EC PRIVATE KEY-----\n"
    "MF8CAQEEGF7IQgvW75JSqULpiQQ8op9WH6Uldw6xxaAKBggqhkjOPQMBAaE0AzIA\n"
    "BLiBd9CE7xf15FY5QIAoNg+fWbSk1yZOYtoGUdzkejWkxbRc9RWTQjqLVXucIJnz\n"
    "bA==\n"
    "-----END EC PRIVATE KEY-----\n"
)
key_bytes = unpem(prv_key_str)
assert isinstance(key_bytes, bytes)
sk = SigningKey.from_der(key_bytes)
vk = sk.verifying_key

data = (
    b"some string for signing"
    b"contents don't really matter"
    b"but do include also some crazy values: "
    b"\x00\x01\t\r\n\x00\x00\x00\xff\xf0"
)
assert len(data) % 4 == 0
sha1 = hashlib.sha1()
sha1.update(data)
data_hash = sha1.digest()
assert isinstance(data_hash, bytes)
sig_raw = sk.sign(data, sigencode=sigencode_string)
assert isinstance(sig_raw, bytes)
sig_der = sk.sign(data, sigencode=sigencode_der)
assert isinstance(sig_der, bytes)
sig_strings = sk.sign(data, sigencode=sigencode_strings)
assert isinstance(sig_strings[0], bytes)

verifiers = []
for modifier, fun in [
    ("bytes", lambda x: x),
    ("bytes memoryview", buffer),
    ("bytearray", bytearray),
    ("bytearray memoryview", lambda x: buffer(bytearray(x))),
    ("array.array of bytes", lambda x: array.array("B", x)),
    ("array.array of bytes memoryview", lambda x: buffer(array.array("B", x))),
    ("array.array of ints", lambda x: array.array("I", x)),
    ("array.array of ints memoryview", lambda x: buffer(array.array("I", x))),
]:
    if "ints" in modifier:
        conv = lambda x: x
    else:
        conv = fun
    for sig_format, signature, decoder, mod_apply in [
        ("raw", sig_raw, sigdecode_string, lambda x: conv(x)),
        ("der", sig_der, sigdecode_der, lambda x: conv(x)),
        (
            "strings",
            sig_strings,
            sigdecode_strings,
            lambda x: tuple(conv(i) for i in x),
        ),
    ]:
        for method_name, vrf_mthd, vrf_data in [
            ("verify", vk.verify, data),
            ("verify_digest", vk.verify_digest, data_hash),
        ]:
            verifiers.append(
                pytest.param(
                    signature,
                    decoder,
                    mod_apply,
                    fun,
                    vrf_mthd,
                    vrf_data,
                    id="{2}-{0}-{1}".format(modifier, sig_format, method_name),
                )
            )


@pytest.mark.parametrize(
    "signature,decoder,mod_apply,fun,vrf_mthd,vrf_data", verifiers
)
def test_VerifyingKey_verify(
    signature, decoder, mod_apply, fun, vrf_mthd, vrf_data
):
    sig = mod_apply(signature)

    assert vrf_mthd(sig, fun(vrf_data), sigdecode=decoder)


# test SigningKey.from_string()
prv_key_bytes = (
    b"^\xc8B\x0b\xd6\xef\x92R\xa9B\xe9\x89\x04<\xa2"
    b"\x9fV\x1f\xa5%w\x0e\xb1\xc5"
)
assert len(prv_key_bytes) == 24
converters = []
for modifier, convert in [
    ("bytes", lambda x: x),
    ("bytes memoryview", buffer),
    ("bytearray", bytearray),
    ("bytearray memoryview", lambda x: buffer(bytearray(x))),
    ("array.array of bytes", lambda x: array.array("B", x)),
    ("array.array of bytes memoryview", lambda x: buffer(array.array("B", x))),
    ("array.array of ints", lambda x: array.array("I", x)),
    ("array.array of ints memoryview", lambda x: buffer(array.array("I", x))),
]:
    converters.append(pytest.param(convert, id=modifier))


@pytest.mark.parametrize("convert", converters)
def test_SigningKey_from_string(convert):
    key = convert(prv_key_bytes)
    sk = SigningKey.from_string(key)

    assert sk.to_string() == prv_key_bytes


# test SigningKey.from_der()
prv_key_str = (
    "-----BEGIN EC PRIVATE KEY-----\n"
    "MF8CAQEEGF7IQgvW75JSqULpiQQ8op9WH6Uldw6xxaAKBggqhkjOPQMBAaE0AzIA\n"
    "BLiBd9CE7xf15FY5QIAoNg+fWbSk1yZOYtoGUdzkejWkxbRc9RWTQjqLVXucIJnz\n"
    "bA==\n"
    "-----END EC PRIVATE KEY-----\n"
)
key_bytes = unpem(prv_key_str)
assert isinstance(key_bytes, bytes)

# last two converters are for array.array of ints, those require input
# that's multiple of 4, which no curve we support produces
@pytest.mark.parametrize("convert", converters[:-2])
def test_SigningKey_from_der(convert):
    key = convert(key_bytes)
    sk = SigningKey.from_der(key)

    assert sk.to_string() == prv_key_bytes


# test SigningKey.sign_deterministic()
extra_entropy = b"\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11"


@pytest.mark.parametrize("convert", converters)
def test_SigningKey_sign_deterministic(convert):
    sig = sk.sign_deterministic(
        convert(data), extra_entropy=convert(extra_entropy)
    )

    vk.verify(sig, data)


# test SigningKey.sign_digest_deterministic()
@pytest.mark.parametrize("convert", converters)
def test_SigningKey_sign_digest_deterministic(convert):
    sig = sk.sign_digest_deterministic(
        convert(data_hash), extra_entropy=convert(extra_entropy)
    )

    vk.verify(sig, data)


@pytest.mark.parametrize("convert", converters)
def test_SigningKey_sign(convert):
    sig = sk.sign(convert(data))

    vk.verify(sig, data)


@pytest.mark.parametrize("convert", converters)
def test_SigningKey_sign_digest(convert):
    sig = sk.sign_digest(convert(data_hash))

    vk.verify(sig, data)


def test_SigningKey_with_unlikely_value():
    sk = SigningKey.from_secret_exponent(NIST256p.order - 1, curve=NIST256p)
    vk = sk.verifying_key
    sig = sk.sign(b"hello")
    assert vk.verify(sig, b"hello")


def test_SigningKey_with_custom_curve_old_point():
    generator = generator_brainpoolp160r1
    generator = Point(
        generator.curve(),
        generator.x(),
        generator.y(),
        generator.order(),
    )

    curve = Curve(
        "BRAINPOOLP160r1",
        generator.curve(),
        generator,
        (1, 3, 36, 3, 3, 2, 8, 1, 1, 1),
    )

    sk = SigningKey.from_secret_exponent(12, curve)

    sk2 = SigningKey.from_secret_exponent(12, BRAINPOOLP160r1)

    assert sk.privkey == sk2.privkey


def test_VerifyingKey_inequality_with_different_curves():
    sk1 = SigningKey.from_secret_exponent(2, BRAINPOOLP160r1)
    sk2 = SigningKey.from_secret_exponent(2, NIST256p)

    assert sk1.verifying_key != sk2.verifying_key


def test_VerifyingKey_inequality_with_different_secret_points():
    sk1 = SigningKey.from_secret_exponent(2, BRAINPOOLP160r1)
    sk2 = SigningKey.from_secret_exponent(3, BRAINPOOLP160r1)

    assert sk1.verifying_key != sk2.verifying_key


def test_SigningKey_from_pem_pkcs8v2_EdDSA():
    pem = """-----BEGIN PRIVATE KEY-----
    MFMCAQEwBQYDK2VwBCIEICc2F2ag1n1QP0jY+g9qWx5sDkx0s/HdNi3cSRHw+zsI
    oSMDIQA+HQ2xCif8a/LMWR2m5HaCm5I2pKe/cc8OiRANMHxjKQ==
    -----END PRIVATE KEY-----"""

    sk = SigningKey.from_pem(pem)
    assert sk.curve == Ed25519
