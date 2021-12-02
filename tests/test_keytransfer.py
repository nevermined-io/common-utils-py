import pytest

from common_utils_py.utils import keytransfer


def test_poseidon():
    assert keytransfer.poseidon([1,2]) == 7853200120776062878684798364095072458815029376092732009249414926327459813530

def test_mimc():
    assert keytransfer.mimc(1, 2, 8496618697356220059886051648941066104102428018438044414794308085967084497473) == [17405299444732615738647569185121043774784715854244839029575270519342275455504, 12697608136635457114705488273155937541518518394149826673715293889909126944425]

def test_jubjub():
    buyer_k = 123
    provider_k = 234
    buyer_pub = keytransfer.mulPointEscalar(keytransfer.base8, buyer_k)
    provider_pub = keytransfer.mulPointEscalar(keytransfer.base8, provider_k)
    assert keytransfer.mulPointEscalar(buyer_pub, provider_k) == keytransfer.mulPointEscalar(provider_pub, buyer_k)

def test_prover():
    data = b"123456789q01234567890q1234567890"
    buyer_k = 123
    provider_k = 234
    buyer_pub = keytransfer.mulPointEscalar(keytransfer.base8, buyer_k)

    prover = keytransfer.make_prover("/usr/local/share/keytransfer/keytransfer.zkey", "/usr/local/share/keytransfer/keytransfer.dat")
    res = keytransfer.prove_transfer(prover, buyer_pub, provider_k, data)

def test_signature():
    data = b"123456789q"
    buyer_secret = "abc123"
    buyer_k = keytransfer.make_key(buyer_secret)
    dta_num = int(data.hex(), 16)
    buyer_pub = keytransfer.mulPointEscalar(keytransfer.base8, buyer_k)
    sig = keytransfer.sign(buyer_secret, dta_num)
    assert keytransfer.verify(buyer_pub, dta_num, sig)

