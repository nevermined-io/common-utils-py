from web3 import Web3

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

#asset_plain = '0x23fefefefefefefefefeefefefefefefef2323abababababababab'
#data = bytes.fromhex(asset_plain[2:])
#c = Web3.keccak(text="abc")
#print('keccak::::::::::::::::::::::::::::')
#provider_key=int(c.hex()[0:60], 16)
#print(c.hex())
#res = prove_transfer(prover, [0x0d7cdd240c2f5b0640839c49fbaaf016a8c5571b8f592e2b62ea939063545981,0x14b14fa0a30ec744dde9f32d519c65ebaa749bfe991a32deea44b83a4e5c65bb], provider_key, data)
# print(res)

# print(res)

