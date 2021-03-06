import logging
import string
from hashlib import sha256
from random import randint, sample

import base58

from config.config import cmod

from anoncreds.protocol.globals import LARGE_PRIME, KEYS, PK_R, \
    LARGE_MASTER_SECRET, LARGE_VPRIME
from anoncreds.protocol.types import SerFmt


def randomQR(n):
    return cmod.random(n) ** 2


def get_hash(*args):
    """
    Enumerate over the input tuple and generate a hash using the tuple values

    :param args:
    :return:
    """

    numbers = [cmod.Conversion.IP2OS(arg) for arg in args]
    h_challenge = sha256()
    for n in sorted(numbers, key=str):
        h_challenge.update(n)
    return h_challenge.digest()


def get_values_of_dicts(*args):
    l = list()
    for d in args:
        l.extend(list(d.values()))
    return l


def get_prime_in_range(start, end):
    n = 0
    maxIter = 100000
    while n < maxIter:
        r = randint(start, end)
        if cmod.isPrime(r):
            logging.debug("Found prime in {} iterations".format(n))
            return r
        n += 1
    raise Exception("Cannot find prime in {} iterations".format(maxIter))


def splitRevealedAttrs(encodedAttrs, revealedAttrs):
    # Revealed attributes
    Ar = {}
    # Unrevealed attributes
    Aur = {}

    for k, value in encodedAttrs.items():
        if k in revealedAttrs:
            Ar[k] = value
        else:
            Aur[k] = value
    return Ar, Aur


def randomString(size: int = 20,
                 chars: str = string.ascii_letters + string.digits) -> str:
    """
    Generate a random string of the specified size.

    Ensure that the size is less than the length of chars as this function uses random.choice
    which uses random sampling without replacement.

    :param size: size of the random string to generate
    :param chars: the set of characters to use to generate the random string. Uses alphanumerics by default.
    :return: the random string generated
    """

    return ''.join(sample(chars, size))


def getUnrevealedAttrs(encodedAttrs, revealedAttrsList):
    flatAttrs = flattenDict(encodedAttrs)
    revealedAttrs, unrevealedAttrs = splitRevealedAttrs(flatAttrs, revealedAttrsList)
    return flatAttrs, unrevealedAttrs


def flattenDict(attrs):
    return {x: y for z in attrs.values()
            for x, y in z.items()}


def strToCryptoInteger(n):
    if "mod" in n:
        a, b = n.split("mod")
        return cmod.integer(int(a.strip())) % cmod.integer(int(b.strip()))
    else:
        return cmod.integer(int(n))


def isCryptoInteger(n):
    return isinstance(n, cmod.integer)


def genPrime():
    """
    Generate 2 large primes `p_prime` and `q_prime` and use them
    to generate another 2 primes `p` and `q` of 1024 bits
    """
    prime = cmod.randomPrime(LARGE_PRIME)
    i = 0
    while not cmod.isPrime(2 * prime + 1):
        prime = cmod.randomPrime(LARGE_PRIME)
        i += 1
    return prime


def base58encode(i):
    return base58.b58encode(str(i).encode())


def base58decode(i):
    return base58.b58decode(str(i)).decode()


def base58decodedInt(i):
    try:
        return int(base58.b58decode(str(i)).decode())
    except Exception as ex:
        raise AttributeError from ex


SerFuncs = {
    SerFmt.py3Int: int,
    SerFmt.default: cmod.integer,
    SerFmt.base58: base58encode,
}


def serialize(data, serFmt):
    serfunc = SerFuncs[serFmt]
    if KEYS in data:
        for k, v in data[KEYS].items():
            if isinstance(v, cmod.integer):
                # int casting works with Python 3 only.
                # for Python 2, charm's serialization api must be used.
                data[KEYS][k] = serfunc(v)
            if k == PK_R:
                data[KEYS][k] = {key: serfunc(val) for key, val in v.items()}
    return data


def generateMasterSecret():
    # Generate the master secret
    return cmod.integer(
        cmod.randomBits(LARGE_MASTER_SECRET))


def generateVPrime():
    return cmod.randomBits(LARGE_VPRIME)


def shorten(s, size=None):
    size = size or 10
    if isinstance(s, str):
        if len(s) <= size:
            return s
        else:
            head = int((size - 2) * 5 / 8)
            tail = int(size) - 2 - head
            return s[:head] + '..' + s[-tail:]
    else:  # assume it's an iterable
        return [shorten(x, size) for x in iter(s)]


def shortenMod(s, size=None):
    return ' mod '.join(shorten(str(s).split(' mod '), size))


def shortenDictVals(d, size=None):
    r = {}
    for k, v in d.items():
        if isinstance(v, dict):
            r[k] = shortenDictVals(v, size)
        else:
            r[k] = shortenMod(v, size)
    return r