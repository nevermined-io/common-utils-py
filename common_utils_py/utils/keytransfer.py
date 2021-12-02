from common_utils_py.utils.poseidon_constants import constants
from common_utils_py.utils.mimc_constants import mimc_constants
from ctypes import *
import json
from web3 import Web3

F = 21888242871839275222246405745257275088548364400416034343698204186575808495617

N_ROUNDS_F = 8
N_ROUNDS_P = [56, 57, 56, 60, 60, 63, 64, 63, 60, 66, 60, 65, 70, 60, 64, 68]

def C(a,b):
    return int(constants['C'][a][b], 16)

def M(a,b,c):
    return int(constants['M'][a][b][c], 16)

def square(a):
    return (a ** 2) % F

def pow5(a):
    return (a ** 5) % F

def add(a,b):
    return (a+b) % F

def sub(a,b):
    return (a-b + F) % F

def div(a,b):
    return mul(a, pow(b, F-2, F))
#    return mul(a, pow(b, -1, F))

def mul(a,b):
    return (a*b) % F

def poseidon(inputs):
    assert(len(inputs) > 0)
    assert(len(inputs) < len(N_ROUNDS_P) - 1)

    t = len(inputs) + 1
    nRoundsF = N_ROUNDS_F
    nRoundsP = N_ROUNDS_P[t - 2]

    state = [0] + inputs
    for r in range(0,nRoundsF + nRoundsP):
        nstate = []
        for i in range(0, len(state)):
            nstate.append(add(state[i], C(t - 2,r * t + i)))
        state = nstate

        if (r < nRoundsF / 2 or r >= nRoundsF / 2 + nRoundsP):
            state = list(map(pow5, state))
        else:
            state[0] = pow5(state[0])

        nstate = []
        for i in range(0, len(state)):
            acc = 0
            for j in range(0, len(state)):
                acc = add(acc, mul(M(t - 2,i,j), state[j]))
            nstate.append(acc)
        state = nstate
    return state[0] % F

NROUNDS = 220

def cts(a):
    return int(mimc_constants[a], 16)

def mimc(_xL_in, _xR_in, _k):
    xL = _xL_in
    xR = _xR_in
    k = _k
    for i in range(0, NROUNDS):
        c = cts(i)
        if i==0:
            t = add(xL, k)
        else:
            t = add(add(xL, k), c)
        xR_tmp = xR
        if i < (NROUNDS - 1):
            xR = xL
            xL = add(xR_tmp, pow5(t))
        else:
            xR = add(xR_tmp, pow5(t))
    return [xL%F, xR%F]

generator = [
    995203441582195749578291179787384436505546430278305826713579947235728471134,
    5472060717959818805561601436314318772137091100104008585924551046643952123905,
]
base8 = [
    5299619240641551281634865583518297030282874472190772894086521144482721001553,
    16950150798460657717958625567821834550301663161624707787222815936182638968203,
]
order = 21888242871839275222246405745257275088614511777268538073601725287587578984328
subOrder = order // 8
A = 168700
D = 168696

def addPoint(a,b):
    beta = mul(a[0],b[1])
    gamma = mul(a[1],b[0])
    delta = mul(sub(a[1], mul(A, a[0])), add(b[0], b[1]))
    tau = mul(beta, gamma)
    dtau = mul(D, tau)
    return [div(add(beta, gamma), add(1, dtau)), div(add(delta, sub(mul(A,beta), gamma)), sub(1, dtau))]

def mulPointEscalar(base, e):
    res = [0,1]
    rem = e
    exp = base

    while rem != 0:
        if rem % 2 == 1:
            res = addPoint(res, exp)
        exp = addPoint(exp, exp)
        rem = rem // 2

    return res

def inCurve(P):
    x2 = square(P[0])
    y2 = square(P[1])

    if add(mul(A, x2), y2) != add(1, mul(mul(x2, y2), D)):
        return False

    return True

def make_key(provider_secret):
    c = Web3.keccak(text=provider_secret)
    return int(c.hex()[0:60], 16)

def make_public(secret):
    k = make_key(secret)
    buyerPub = mulPointEscalar(base8, k)
    res = hex(buyerPub[0])[2:].zfill(64) + hex(buyerPub[1])[2:].zfill(64)
    return res

def sign(provider_secret, msg):
    r = make_key(provider_secret + 'a')
    r = r % subOrder
    s = make_key(provider_secret)
    R8 = mulPointEscalar(base8, r)
    A = mulPointEscalar(base8, s)
    hm = poseidon([R8[0], R8[1], A[0], A[1], msg % F])
    S = (r + hm*s) % subOrder
    return {
        'R8': [hex(R8[0]), hex(R8[1])],
        'S': hex(S),
    }

def verify(A, msg, sig):
    sig_R8 = [int(sig['R8'][0], 16), int(sig['R8'][1], 16)]
    sig_S = int(sig['S'], 16)
    if not inCurve(sig_R8):
        return False
    if not inCurve(A):
        return False
    if sig_S >= subOrder:
        return False

    hm = poseidon([sig_R8[0], sig_R8[1], A[0], A[1], msg % F])

    Pleft = mulPointEscalar(base8, sig_S*8)
    Pright = mulPointEscalar(A, hm*8)
    Pright = addPoint(mulPointEscalar(sig_R8, 8), Pright)

    if Pleft[0] != Pright[0]:
        return False
    if Pleft[1] != Pright[1]:
        return False
    return True

libkey = 0

def init_prover():
    global libkey
    libname = "libkeytransfer.so"
    file = open("/proc/cpuinfo").read()
    if not 'adx' in file:
        libname = "libkeytransfer_noadx.so"
    cdll.LoadLibrary(libname)
    libkey = CDLL(libname)
    libkey.make.restype = c_void_p
    libkey.fullprove.restype = c_char_p

def make_prover(zkey, dat):
    if libkey == 0:
        init_prover()
    return libkey.make(zkey.encode('utf-8'), dat.encode('utf-8'))

def prove(prover, input):
    with open('/tmp/input.json', 'w') as outfile:
        json.dump(input, outfile)
    res = libkey.fullprove(c_void_p(prover), b"/tmp/keytransfer.wtns", b"/tmp/input.json")
    return res.decode()

def split(data):
    return [int(data[0:16].hex(), 16), int(data[16:32].hex(), 16)]

def hash_key(data):
    lst = split(data)
    return hex(poseidon(lst))

def hx(a):
    return str(a)

def prove_transfer(prover, buyerPub, providerK, data):
    orig = split(data)

    k = mulPointEscalar(buyerPub, providerK)
    cipher = mimc(orig[0], orig[1], k[0])
    origHash = poseidon([orig[0], orig[1]])
    providerPub = mulPointEscalar(base8, providerK)


    snarkParams = {
        'buyer_x': hx(buyerPub[0]),
        'buyer_y': hx(buyerPub[1]),
        'provider_x': hx(providerPub[0]),
        'provider_y': hx(providerPub[1]),
        'xL_in': hx(orig[0]),
        'xR_in': hx(orig[1]),
        'cipher_xL_in': hx(cipher[0]),
        'cipher_xR_in': hx(cipher[1]),
        'provider_k': hx(providerK),
        'hash_plain': hx(origHash)
    }

    res = {
        'proof': prove(prover, snarkParams),
        'hash': hash_key(data),
        'cipher': [hex(cipher[0]), hex(cipher[1])]
    }
    return res

