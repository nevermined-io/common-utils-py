
from poseidon_constants import constants
from mimc_constants import mimc_constants

F = 21888242871839275222246405745257275088548364400416034343698204186575808495617

N_ROUNDS_F = 8
N_ROUNDS_P = [56, 57, 56, 60, 60, 63, 64, 63, 60, 66, 60, 65, 70, 60, 64, 68]

def C(a,b):
    return int(constants['C'][a][b], 16)

def M(a,b,c):
    return int(constants['M'][a][b][c], 16)

def pow5(a):
    return (a ** 5) % F

def add(a,b):
    return (a+b) % F

def sub(a,b):
    return (a-b + F) % F

def div(a,b):
    return mul(a, pow(b, -1, F))

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

print(poseidon([1,2]))

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

print(mimc(1, 2, 8496618697356220059886051648941066104102428018438044414794308085967084497473))

generator = [
    995203441582195749578291179787384436505546430278305826713579947235728471134,
    5472060717959818805561601436314318772137091100104008585924551046643952123905,
]
base8 = [
    5299619240641551281634865583518297030282874472190772894086521144482721001553,
    16950150798460657717958625567821834550301663161624707787222815936182638968203,
]
order = 21888242871839275222246405745257275088614511777268538073601725287587578984328
subOrder = order / 8
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
        # print(res, rem, rem % 2)
        if rem % 2 == 1:
            res = addPoint(res, exp)
        exp = addPoint(exp, exp)
        rem = rem // 2

    return res

buyer_k = 123
provider_k = 234
buyer_pub = mulPointEscalar(base8, buyer_k)
provider_pub = mulPointEscalar(base8, provider_k)
print(buyer_pub)
print(provider_pub)

print(mulPointEscalar(buyer_pub, provider_k))
print(mulPointEscalar(provider_pub, buyer_k))

