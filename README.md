# Pure-Python ECDSA and ECDH

[![Build Status](https://github.com/tlsfuzzer/python-ecdsa/workflows/GitHub%20CI/badge.svg?branch=master)](https://github.com/tlsfuzzer/python-ecdsa/actions?query=workflow%3A%22GitHub+CI%22+branch%3Amaster)
[![Documentation Status](https://readthedocs.org/projects/ecdsa/badge/?version=latest)](https://ecdsa.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/tlsfuzzer/python-ecdsa/badge.svg?branch=master)](https://coveralls.io/github/tlsfuzzer/python-ecdsa?branch=master)
![condition coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/tomato42/9b6ca1f3410207fbeca785a178781651/raw/python-ecdsa-condition-coverage.json)
[![CodeQL](https://github.com/tlsfuzzer/python-ecdsa/actions/workflows/codeql.yml/badge.svg)](https://github.com/tlsfuzzer/python-ecdsa/actions/workflows/codeql.yml)
[![Latest Version](https://img.shields.io/pypi/v/ecdsa.svg?style=flat)](https://pypi.python.org/pypi/ecdsa/)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)


This is an easy-to-use implementation of ECC (Elliptic Curve Cryptography)
with support for ECDSA (Elliptic Curve Digital Signature Algorithm),
EdDSA (Edwards-curve Digital Signature Algorithm) and ECDH
(Elliptic Curve Diffie-Hellman), implemented purely in Python, released under
the MIT license. With this library, you can quickly create key pairs (signing
key and verifying key), sign messages, and verify the signatures. You can
also agree on a shared secret key based on exchanged public keys.
The keys and signatures are very short, making them easy to handle and
incorporate into other protocols.

**NOTE: This library should not be used in production settings, see [Security](#Security) for more details.**

## Features

This library provides key generation, signing, verifying, and shared secret
derivation for five
popular NIST "Suite B" GF(p) (_prime field_) curves, with key lengths of 192,
224, 256, 384, and 521 bits. The "short names" for these curves, as known by
the OpenSSL tool (`openssl ecparam -list_curves`), are: `prime192v1`,
`secp224r1`, `prime256v1`, `secp384r1`, and `secp521r1`. It includes the
256-bit curve `secp256k1` used by Bitcoin. There is also support for the
regular (non-twisted) variants of Brainpool curves from 160 to 512 bits. The
"short names" of those curves are: `brainpoolP160r1`, `brainpoolP192r1`,
`brainpoolP224r1`, `brainpoolP256r1`, `brainpoolP320r1`, `brainpoolP384r1`,
`brainpoolP512r1`. Few of the small curves from SEC standard are also
included (mainly to speed-up testing of the library), those are:
`secp112r1`, `secp112r2`, `secp128r1`, and `secp160r1`.
Key generation, siging and verifying is also supported for Ed25519 and
Ed448 curves.
No other curves are included, but it is not too hard to add support for more
curves over prime fields.

## Dependencies

This library uses only Python and the 'six' package. It is compatible with
Python 2.6, 2.7, and 3.5+. It also supports execution on alternative
implementations like pypy and pypy3.

If `gmpy2` or `gmpy` is installed, they will be used for faster arithmetic.
Either of them can be installed after this library is installed,
`python-ecdsa` will detect their presence on start-up and use them
automatically.
You should prefer `gmpy2` on Python3 for optimal performance.

To run the OpenSSL compatibility tests, the 'openssl' tool must be in your
`PATH`. This release has been tested successfully against OpenSSL 0.9.8o,
1.0.0a, 1.0.2f, 1.1.1d and 3.0.1 (among others).


## Installation

This library is available on PyPI, it's recommended to install it using `pip`:

```
pip install ecdsa
```

In case higher performance is wanted and using native code is not a problem,
it's possible to specify installation together with `gmpy2`:

```
pip install ecdsa[gmpy2]
```

or (slower, legacy option):
```
pip install ecdsa[gmpy]
```

## Speed

The following table shows how long this library takes to generate key pairs
(`keygen`), to sign data (`sign`), to verify those signatures (`verify`),
to derive a shared secret (`ecdh`), and
to verify the signatures with no key-specific precomputation (`no PC verify`).
All those values are in seconds.
For convenience, the inverses of those values are also provided:
how many keys per second can be generated (`keygen/s`), how many signatures
can be made per second (`sign/s`), how many signatures can be verified
per second (`verify/s`), how many shared secrets can be derived per second
(`ecdh/s`), and how many signatures with no key specific
precomputation can be verified per second (`no PC verify/s`). The size of raw
signature (generally the smallest
the way a signature can be encoded) is also provided in the `siglen` column.
Use `tox -e speed` to generate this table on your own computer.
On an Intel Core i7 4790K @ 4.0GHz I'm getting the following performance:

```
                  siglen    keygen   keygen/s      sign     sign/s    verify   verify/s  no PC verify  no PC verify/s
        NIST192p:     48   0.00032s   3134.06   0.00033s   2985.53   0.00063s   1598.36       0.00129s         774.43
        NIST224p:     56   0.00040s   2469.24   0.00042s   2367.88   0.00081s   1233.41       0.00170s         586.66
        NIST256p:     64   0.00051s   1952.73   0.00054s   1867.80   0.00098s   1021.86       0.00212s         471.27
        NIST384p:     96   0.00107s    935.92   0.00111s    904.23   0.00203s    491.77       0.00446s         224.00
        NIST521p:    132   0.00210s    475.52   0.00215s    464.16   0.00398s    251.28       0.00874s         114.39
       SECP256k1:     64   0.00052s   1921.54   0.00054s   1847.49   0.00105s    948.68       0.00210s         477.01
 BRAINPOOLP160r1:     40   0.00025s   4003.88   0.00026s   3845.12   0.00053s   1893.93       0.00105s         949.92
 BRAINPOOLP192r1:     48   0.00033s   3043.97   0.00034s   2975.98   0.00063s   1581.50       0.00135s         742.29
 BRAINPOOLP224r1:     56   0.00041s   2436.44   0.00043s   2315.51   0.00078s   1278.49       0.00180s         556.16
 BRAINPOOLP256r1:     64   0.00053s   1892.49   0.00054s   1846.24   0.00114s    875.64       0.00229s         437.25
 BRAINPOOLP320r1:     80   0.00073s   1361.26   0.00076s   1309.25   0.00143s    699.29       0.00322s         310.49
 BRAINPOOLP384r1:     96   0.00107s    931.29   0.00111s    901.80   0.00230s    434.19       0.00476s         210.20
 BRAINPOOLP512r1:    128   0.00207s    483.41   0.00212s    471.42   0.00425s    235.43       0.00912s         109.61
       SECP112r1:     28   0.00015s   6672.53   0.00016s   6440.34   0.00031s   3265.41       0.00056s        1774.20
       SECP112r2:     28   0.00015s   6697.11   0.00015s   6479.98   0.00028s   3524.72       0.00058s        1716.16
       SECP128r1:     32   0.00018s   5497.65   0.00019s   5272.89   0.00036s   2747.39       0.00072s        1396.16
       SECP160r1:     42   0.00025s   3949.32   0.00026s   3894.45   0.00046s   2153.85       0.00102s         985.07
         Ed25519:     64   0.00076s   1324.48   0.00042s   2405.01   0.00109s    918.05       0.00344s         290.50
           Ed448:    114   0.00176s    569.53   0.00115s    870.94   0.00282s    355.04       0.01024s          97.69

                       ecdh     ecdh/s
        NIST192p:   0.00104s    964.89
        NIST224p:   0.00134s    748.63
        NIST256p:   0.00170s    587.08
        NIST384p:   0.00352s    283.90
        NIST521p:   0.00717s    139.51
       SECP256k1:   0.00154s    648.40
 BRAINPOOLP160r1:   0.00082s   1220.70
 BRAINPOOLP192r1:   0.00105s    956.75
 BRAINPOOLP224r1:   0.00136s    734.52
 BRAINPOOLP256r1:   0.00178s    563.32
 BRAINPOOLP320r1:   0.00252s    397.23
 BRAINPOOLP384r1:   0.00376s    266.27
 BRAINPOOLP512r1:   0.00733s    136.35
       SECP112r1:   0.00046s   2180.40
       SECP112r2:   0.00045s   2229.14
       SECP128r1:   0.00054s   1868.15
       SECP160r1:   0.00080s   1243.98
```

To test performance with `gmpy2` loaded, use `tox -e speedgmpy2`.
On the same machine I'm getting the following performance with `gmpy2`:
```
                  siglen    keygen   keygen/s      sign     sign/s    verify   verify/s  no PC verify  no PC verify/s
        NIST192p:     48   0.00017s   5933.40   0.00017s   5751.70   0.00032s   3125.28       0.00067s        1502.41
        NIST224p:     56   0.00021s   4782.87   0.00022s   4610.05   0.00040s   2487.04       0.00089s        1126.90
        NIST256p:     64   0.00023s   4263.98   0.00024s   4125.16   0.00045s   2200.88       0.00098s        1016.82
        NIST384p:     96   0.00041s   2449.54   0.00042s   2399.96   0.00083s   1210.57       0.00172s         581.43
        NIST521p:    132   0.00071s   1416.07   0.00072s   1389.81   0.00144s    692.93       0.00312s         320.40
       SECP256k1:     64   0.00024s   4245.05   0.00024s   4122.09   0.00045s   2206.40       0.00094s        1068.32
 BRAINPOOLP160r1:     40   0.00014s   6939.17   0.00015s   6681.55   0.00029s   3452.43       0.00057s        1769.81
 BRAINPOOLP192r1:     48   0.00017s   5920.05   0.00017s   5774.36   0.00034s   2979.00       0.00069s        1453.19
 BRAINPOOLP224r1:     56   0.00021s   4732.12   0.00022s   4622.65   0.00041s   2422.47       0.00087s        1149.87
 BRAINPOOLP256r1:     64   0.00024s   4233.02   0.00024s   4115.20   0.00047s   2143.27       0.00098s        1015.60
 BRAINPOOLP320r1:     80   0.00032s   3162.38   0.00032s   3077.62   0.00063s   1598.83       0.00136s         737.34
 BRAINPOOLP384r1:     96   0.00041s   2436.88   0.00042s   2395.62   0.00083s   1202.68       0.00178s         562.85
 BRAINPOOLP512r1:    128   0.00063s   1587.60   0.00064s   1558.83   0.00125s    799.96       0.00281s         355.83
       SECP112r1:     28   0.00009s  11118.66   0.00009s  10775.48   0.00018s   5456.00       0.00033s        3020.83
       SECP112r2:     28   0.00009s  11322.97   0.00009s  10857.71   0.00017s   5748.77       0.00032s        3094.28
       SECP128r1:     32   0.00010s  10078.39   0.00010s   9665.27   0.00019s   5200.58       0.00036s        2760.88
       SECP160r1:     42   0.00015s   6875.51   0.00015s   6647.35   0.00029s   3422.41       0.00057s        1768.35
         Ed25519:     64   0.00030s   3322.56   0.00018s   5568.63   0.00046s   2165.35       0.00153s         654.02
           Ed448:    114   0.00060s   1680.53   0.00039s   2567.40   0.00096s   1036.67       0.00350s         285.62

                       ecdh     ecdh/s
        NIST192p:   0.00050s   1985.70
        NIST224p:   0.00066s   1524.16
        NIST256p:   0.00071s   1413.07
        NIST384p:   0.00127s    788.89
        NIST521p:   0.00230s    434.85
       SECP256k1:   0.00071s   1409.95
 BRAINPOOLP160r1:   0.00042s   2374.65
 BRAINPOOLP192r1:   0.00051s   1960.01
 BRAINPOOLP224r1:   0.00066s   1518.37
 BRAINPOOLP256r1:   0.00071s   1399.90
 BRAINPOOLP320r1:   0.00100s    997.21
 BRAINPOOLP384r1:   0.00129s    777.51
 BRAINPOOLP512r1:   0.00210s    475.99
       SECP112r1:   0.00022s   4457.70
       SECP112r2:   0.00024s   4252.33
       SECP128r1:   0.00028s   3589.31
       SECP160r1:   0.00043s   2305.02
```

(there's also `gmpy` version, execute it using `tox -e speedgmpy`)

For comparison, a highly optimised implementation (including curve-specific
assembly for some curves), like the one in OpenSSL 1.1.1d, provides the
following performance numbers on the same machine.
Run `openssl speed ecdsa` and `openssl speed ecdh` to reproduce it:
```
                              sign    verify    sign/s verify/s
 192 bits ecdsa (nistp192)   0.0002s   0.0002s   4785.6   5380.7
 224 bits ecdsa (nistp224)   0.0000s   0.0001s  22475.6   9822.0
 256 bits ecdsa (nistp256)   0.0000s   0.0001s  45069.6  14166.6
 384 bits ecdsa (nistp384)   0.0008s   0.0006s   1265.6   1648.1
 521 bits ecdsa (nistp521)   0.0003s   0.0005s   3753.1   1819.5
 256 bits ecdsa (brainpoolP256r1)   0.0003s   0.0003s   2983.5   3333.2
 384 bits ecdsa (brainpoolP384r1)   0.0008s   0.0007s   1258.8   1528.1
 512 bits ecdsa (brainpoolP512r1)   0.0015s   0.0012s    675.1    860.1

                              sign    verify    sign/s verify/s
 253 bits EdDSA (Ed25519)   0.0000s   0.0001s  28217.9  10897.7
 456 bits EdDSA (Ed448)     0.0003s   0.0005s   3926.5   2147.7

                               op      op/s
 192 bits ecdh (nistp192)   0.0002s   4853.4
 224 bits ecdh (nistp224)   0.0001s  15252.1
 256 bits ecdh (nistp256)   0.0001s  18436.3
 384 bits ecdh (nistp384)   0.0008s   1292.7
 521 bits ecdh (nistp521)   0.0003s   2884.7
 256 bits ecdh (brainpoolP256r1)   0.0003s   3066.5
 384 bits ecdh (brainpoolP384r1)   0.0008s   1298.0
 512 bits ecdh (brainpoolP512r1)   0.0014s    694.8
```

Keys and signature can be serialized in different ways (see Usage, below).
For a NIST192p key, the three basic representations require strings of the
following lengths (in bytes):

    to_string:  signkey= 24, verifykey= 48, signature=48
    compressed: signkey=n/a, verifykey= 25, signature=n/a
    DER:        signkey=106, verifykey= 80, signature=55
    PEM:        signkey=278, verifykey=162, (no support for PEM signatures)

## History

In 2006, Peter Pearson announced his pure-python implementation of ECDSA in a
[message to sci.crypt][1], available from his [download site][2]. In 2010,
Brian Warner wrote a wrapper around this code, to make it a bit easier and
safer to use. In 2020, Hubert Kario included an implementation of elliptic
curve cryptography that uses Jacobian coordinates internally, improving
performance about 20-fold. You are looking at the README for this wrapper.

[1]: http://www.derkeiler.com/Newsgroups/sci.crypt/2006-01/msg00651.html
[2]: http://webpages.charter.net/curryfans/peter/downloads.html

## Testing

To run the full test suite, do this:

    tox -e coverage

On an Intel Core i7 4790K @ 4.0GHz, the tests take about 18 seconds to execute.
The test suite uses
[`hypothesis`](https://github.com/HypothesisWorks/hypothesis) so there is some
inherent variability in the test suite execution time.

One part of `test_pyecdsa.py` and `test_ecdh.py` checks compatibility with
OpenSSL, by running the "openssl" CLI tool, make sure it's in your `PATH` if
you want to test compatibility with it (if OpenSSL is missing, too old, or
doesn't support all the curves supported in upstream releases you will see
skipped tests in the above `coverage` run).

## Security

This library was not designed with security in mind. If you are processing
data that needs to be protected we suggest you use a quality wrapper around
OpenSSL. [pyca/cryptography](https://cryptography.io) is one example of such
a wrapper. The primary use-case of this library is as a portable library for
interoperability testing and as a teaching tool.

**This library does not protect against side-channel attacks.**

Do not allow attackers to measure how long it takes you to generate a key pair
or sign a message. Do not allow attackers to run code on the same physical
machine when key pair generation or signing is taking place (this includes
virtual machines). Do not allow attackers to measure how much power your
computer uses while generating the key pair or signing a message. Do not allow
attackers to measure RF interference coming from your computer while generating
a key pair or signing a message. Note: just loading the private key will cause
key pair generation. Other operations or attack vectors may also be
vulnerable to attacks. **For a sophisticated attacker observing just one
operation with a private key will be sufficient to completely
reconstruct the private key**.

Please also note that any Pure-python cryptographic library will be vulnerable
to the same side-channel attacks. This is because Python does not provide
side-channel secure primitives (with the exception of
[`hmac.compare_digest()`][3]), making side-channel secure programming
impossible.

This library depends upon a strong source of random numbers. Do not use it on
a system where `os.urandom()` does not provide cryptographically secure
random numbers.

[3]: https://docs.python.org/3/library/hmac.html#hmac.compare_digest

## Usage

You start by creating a `SigningKey`. You can use this to sign data, by passing
in data as a byte string and getting back the signature (also a byte string).
You can also ask a `SigningKey` to give you the corresponding `VerifyingKey`.
The `VerifyingKey` can be used to verify a signature, by passing it both the
data string and the signature byte string: it either returns True or raises
`BadSignatureError`.

```python
from ecdsa import SigningKey
sk = SigningKey.generate() # uses NIST192p
vk = sk.verifying_key
signature = sk.sign(b"message")
assert vk.verify(signature, b"message")
```

Each `SigningKey`/`VerifyingKey` is associated with a specific curve, like
NIST192p (the default one). Longer curves are more secure, but take longer to
use, and result in longer keys and signatures.

```python
from ecdsa import SigningKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
vk = sk.verifying_key
signature = sk.sign(b"message")
assert vk.verify(signature, b"message")
```

The `SigningKey` can be serialized into several different formats: the shortest
is to call `s=sk.to_string()`, and then re-create it with
`SigningKey.from_string(s, curve)` . This short form does not record the
curve, so you must be sure to pass to `from_string()` the same curve you used
for the original key. The short form of a NIST192p-based signing key is just 24
bytes long. If a point encoding is invalid or it does not lie on the specified
curve, `from_string()` will raise `MalformedPointError`.

```python
from ecdsa import SigningKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
sk_string = sk.to_string()
sk2 = SigningKey.from_string(sk_string, curve=NIST384p)
print(sk_string.hex())
print(sk2.to_string().hex())
```

Note: while the methods are called `to_string()` the type they return is
actually `bytes`, the "string" part is leftover from Python 2.

`sk.to_pem()` and `sk.to_der()` will serialize the signing key into the same
formats that OpenSSL uses. The PEM file looks like the familiar ASCII-armored
`"-----BEGIN EC PRIVATE KEY-----"` base64-encoded format, and the DER format
is a shorter binary form of the same data.
`SigningKey.from_pem()/.from_der()` will undo this serialization. These
formats include the curve name, so you do not need to pass in a curve
identifier to the deserializer. In case the file is malformed `from_der()`
and `from_pem()` will raise `UnexpectedDER` or` MalformedPointError`.

```python
from ecdsa import SigningKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
sk_pem = sk.to_pem()
sk2 = SigningKey.from_pem(sk_pem)
# sk and sk2 are the same key
```

Likewise, the `VerifyingKey` can be serialized in the same way:
`vk.to_string()/VerifyingKey.from_string()`, `to_pem()/from_pem()`, and
`to_der()/from_der()`. The same `curve=` argument is needed for
`VerifyingKey.from_string()`.

```python
from ecdsa import SigningKey, VerifyingKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
vk = sk.verifying_key
vk_string = vk.to_string()
vk2 = VerifyingKey.from_string(vk_string, curve=NIST384p)
# vk and vk2 are the same key

from ecdsa import SigningKey, VerifyingKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
vk = sk.verifying_key
vk_pem = vk.to_pem()
vk2 = VerifyingKey.from_pem(vk_pem)
# vk and vk2 are the same key
```

There are a couple of different ways to compute a signature. Fundamentally,
ECDSA takes a number that represents the data being signed, and returns a
pair of numbers that represent the signature. The `hashfunc=` argument to
`sk.sign()` and `vk.verify()` is used to turn an arbitrary string into a
fixed-length digest, which is then turned into a number that ECDSA can sign,
and both sign and verify must use the same approach. The default value is
`hashlib.sha1`, but if you use NIST256p or a longer curve, you can use
`hashlib.sha256` instead.

There are also multiple ways to represent a signature. The default
`sk.sign()` and `vk.verify()` methods present it as a short string, for
simplicity and minimal overhead. To use a different scheme, use the
`sk.sign(sigencode=)` and `vk.verify(sigdecode=)` arguments. There are helper
functions in the `ecdsa.util` module that can be useful here.

It is also possible to create a `SigningKey` from a "seed", which is
deterministic. This can be used in protocols where you want to derive
consistent signing keys from some other secret, for example when you want
three separate keys and only want to store a single master secret. You should
start with a uniformly-distributed unguessable seed with about `curve.baselen`
bytes of entropy, and then use one of the helper functions in `ecdsa.util` to
convert it into an integer in the correct range, and then finally pass it
into `SigningKey.from_secret_exponent()`, like this:

```python
import os
from ecdsa import NIST384p, SigningKey
from ecdsa.util import randrange_from_seed__trytryagain

def make_key(seed):
  secexp = randrange_from_seed__trytryagain(seed, NIST384p.order)
  return SigningKey.from_secret_exponent(secexp, curve=NIST384p)

seed = os.urandom(NIST384p.baselen) # or other starting point
sk1a = make_key(seed)
sk1b = make_key(seed)
# note: sk1a and sk1b are the same key
assert sk1a.to_string() == sk1b.to_string()
sk2 = make_key(b"2-"+seed)  # different key
assert sk1a.to_string() != sk2.to_string()
```

In case the application will verify a lot of signatures made with a single
key, it's possible to precompute some of the internal values to make
signature verification significantly faster. The break-even point occurs at
about 100 signatures verified.

To perform precomputation, you can call the `precompute()` method
on `VerifyingKey` instance:
```python
from ecdsa import SigningKey, NIST384p
sk = SigningKey.generate(curve=NIST384p)
vk = sk.verifying_key
vk.precompute()
signature = sk.sign(b"message")
assert vk.verify(signature, b"message")
```

Once `precompute()` was called, all signature verifications with this key will
be faster to execute.

## OpenSSL Compatibility

To produce signatures that can be verified by OpenSSL tools, or to verify
signatures that were produced by those tools, use:

```python
# openssl ecparam -name prime256v1 -genkey -out sk.pem
# openssl ec -in sk.pem -pubout -out vk.pem
# echo "data for signing" > data
# openssl dgst -sha256 -sign sk.pem -out data.sig data
# openssl dgst -sha256 -verify vk.pem -signature data.sig data
# openssl dgst -sha256 -prverify sk.pem -signature data.sig data

import hashlib
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der

with open("vk.pem") as f:
   vk = VerifyingKey.from_pem(f.read())

with open("data", "rb") as f:
   data = f.read()

with open("data.sig", "rb") as f:
   signature = f.read()

assert vk.verify(signature, data, hashlib.sha256, sigdecode=sigdecode_der)

with open("sk.pem") as f:
   sk = SigningKey.from_pem(f.read(), hashlib.sha256)

new_signature = sk.sign_deterministic(data, sigencode=sigencode_der)

with open("data.sig2", "wb") as f:
   f.write(new_signature)

# openssl dgst -sha256 -verify vk.pem -signature data.sig2 data
```

Note: if compatibility with OpenSSL 1.0.0 or earlier is necessary, the
`sigencode_string` and `sigdecode_string` from `ecdsa.util` can be used for
respectively writing and reading the signatures.

The keys also can be written in format that openssl can handle:

```python
from ecdsa import SigningKey, VerifyingKey

with open("sk.pem") as f:
    sk = SigningKey.from_pem(f.read())
with open("sk.pem", "wb") as f:
    f.write(sk.to_pem())

with open("vk.pem") as f:
    vk = VerifyingKey.from_pem(f.read())
with open("vk.pem", "wb") as f:
    f.write(vk.to_pem())
```

## Entropy

Creating a signing key with `SigningKey.generate()` requires some form of
entropy (as opposed to
`from_secret_exponent`/`from_string`/`from_der`/`from_pem`,
which are deterministic and do not require an entropy source). The default
source is `os.urandom()`, but you can pass any other function that behaves
like `os.urandom` as the `entropy=` argument to do something different. This
may be useful in unit tests, where you want to achieve repeatable results. The
`ecdsa.util.PRNG` utility is handy here: it takes a seed and produces a strong
pseudo-random stream from it:

```python
from ecdsa.util import PRNG
from ecdsa import SigningKey
rng1 = PRNG(b"seed")
sk1 = SigningKey.generate(entropy=rng1)
rng2 = PRNG(b"seed")
sk2 = SigningKey.generate(entropy=rng2)
# sk1 and sk2 are the same key
```

Likewise, ECDSA signature generation requires a random number, and each
signature must use a different one (using the same number twice will
immediately reveal the private signing key). The `sk.sign()` method takes an
`entropy=` argument which behaves the same as `SigningKey.generate(entropy=)`.

## Deterministic Signatures

If you call `SigningKey.sign_deterministic(data)` instead of `.sign(data)`,
the code will generate a deterministic signature instead of a random one.
This uses the algorithm from RFC6979 to safely generate a unique `k` value,
derived from the private key and the message being signed. Each time you sign
the same message with the same key, you will get the same signature (using
the same `k`).

This may become the default in a future version, as it is not vulnerable to
failures of the entropy source.

## Examples

Create a NIST192p key pair and immediately save both to disk:

```python
from ecdsa import SigningKey
sk = SigningKey.generate()
vk = sk.verifying_key
with open("private.pem", "wb") as f:
    f.write(sk.to_pem())
with open("public.pem", "wb") as f:
    f.write(vk.to_pem())
```

Load a signing key from disk, use it to sign a message (using SHA-1), and write
the signature to disk:

```python
from ecdsa import SigningKey
with open("private.pem") as f:
    sk = SigningKey.from_pem(f.read())
with open("message", "rb") as f:
    message = f.read()
sig = sk.sign(message)
with open("signature", "wb") as f:
    f.write(sig)
```

Load the verifying key, message, and signature from disk, and verify the
signature (assume SHA-1 hash):

```python
from ecdsa import VerifyingKey, BadSignatureError
vk = VerifyingKey.from_pem(open("public.pem").read())
with open("message", "rb") as f:
    message = f.read()
with open("signature", "rb") as f:
    sig = f.read()
try:
    vk.verify(sig, message)
    print "good signature"
except BadSignatureError:
    print "BAD SIGNATURE"
```

Create a NIST521p key pair:

```python
from ecdsa import SigningKey, NIST521p
sk = SigningKey.generate(curve=NIST521p)
vk = sk.verifying_key
```

Create three independent signing keys from a master seed:

```python
from ecdsa import NIST192p, SigningKey
from ecdsa.util import randrange_from_seed__trytryagain

def make_key_from_seed(seed, curve=NIST192p):
    secexp = randrange_from_seed__trytryagain(seed, curve.order)
    return SigningKey.from_secret_exponent(secexp, curve)

sk1 = make_key_from_seed("1:%s" % seed)
sk2 = make_key_from_seed("2:%s" % seed)
sk3 = make_key_from_seed("3:%s" % seed)
```

Load a verifying key from disk and print it using hex encoding in
uncompressed and compressed format (defined in X9.62 and SEC1 standards):

```python
from ecdsa import VerifyingKey

with open("public.pem") as f:
    vk = VerifyingKey.from_pem(f.read())

print("uncompressed: {0}".format(vk.to_string("uncompressed").hex()))
print("compressed: {0}".format(vk.to_string("compressed").hex()))
```

Load a verifying key from a hex string from compressed format, output
uncompressed:

```python
from ecdsa import VerifyingKey, NIST256p

comp_str = '022799c0d0ee09772fdd337d4f28dc155581951d07082fb19a38aa396b67e77759'
vk = VerifyingKey.from_string(bytearray.fromhex(comp_str), curve=NIST256p)
print(vk.to_string("uncompressed").hex())
```

ECDH key exchange with remote party:

```python
from ecdsa import ECDH, NIST256p

ecdh = ECDH(curve=NIST256p)
ecdh.generate_private_key()
local_public_key = ecdh.get_public_key()
#send `local_public_key` to remote party and receive `remote_public_key` from remote party
with open("remote_public_key.pem") as e:
    remote_public_key = e.read()
ecdh.load_received_public_key_pem(remote_public_key)
secret = ecdh.generate_sharedsecret_bytes()
```
