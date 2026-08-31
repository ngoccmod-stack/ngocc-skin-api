import os as c
import struct as l
import lzma as e
g = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]
t = [0] * 256
for a, b in enumerate(g):
    t[b] = a
f = [1, 2, 4, 8, 16, 32, 64, 128, 27, 54]

def k(N):
    N <<= 1
    if N & 256:
        N ^= 283
    return N & 255

def d(O, P):
    Q = 0
    for N in range(8):
        if P & 1:
            Q ^= O
        R = O & 128
        O = O << 1 & 255
        if R:
            O ^= 27
        P >>= 1
    return Q

def I(U):
    S, T = (4, 10)
    R = [list(U[4 * O:4 * O + 4]) for O in range(S)]
    for O in range(S, 4 * (T + 1)):
        V = list(R[O - 1])
        if O % S == 0:
            V = V[1:] + V[:1]
            V = [g[N] for N in V]
            V[0] ^= f[O // S - 1]
        R.append([R[O - S][P] ^ V[P] for P in range(4)])
    return [sum((R[Q * 4 + c] for c in range(4)), []) for Q in range(T + 1)]

def C(P, O):
    return [P[N] ^ O[N] for N in range(16)]

def y(P, O):
    return [O[N] for N in P]

def z(Q):
    P = [0] * 16
    for N in range(4):
        for O in range(4):
            P[(N - O) % 4 * 4 + O] = Q[N * 4 + O]
    return P

def D(Q):
    P = [0] * 16
    for N in range(4):
        for O in range(4):
            P[(N + O) % 4 * 4 + O] = Q[N * 4 + O]
    return P

def A(Q):
    P = [0] * 16
    for N in range(4):
        O = Q[N * 4:N * 4 + 4]
        P[N * 4 + 0] = k(O[0]) ^ (k(O[1]) ^ O[1]) ^ O[2] ^ O[3]
        P[N * 4 + 1] = O[0] ^ k(O[1]) ^ (k(O[2]) ^ O[2]) ^ O[3]
        P[N * 4 + 2] = O[0] ^ O[1] ^ k(O[2]) ^ (k(O[3]) ^ O[3])
        P[N * 4 + 3] = k(O[0]) ^ O[0] ^ O[1] ^ O[2] ^ k(O[3])
    return P

def F(Q):
    P = [0] * 16
    for N in range(4):
        O = Q[N * 4:N * 4 + 4]
        P[N * 4 + 0] = d(O[0], 14) ^ d(O[1], 11) ^ d(O[2], 13) ^ d(O[3], 9)
        P[N * 4 + 1] = d(O[0], 9) ^ d(O[1], 14) ^ d(O[2], 11) ^ d(O[3], 13)
        P[N * 4 + 2] = d(O[0], 13) ^ d(O[1], 9) ^ d(O[2], 14) ^ d(O[3], 11)
        P[N * 4 + 3] = d(O[0], 11) ^ d(O[1], 13) ^ d(O[2], 9) ^ d(O[3], 14)
    return P

def H(R, P):
    O = I(P)
    Q = list(R)
    Q = C(Q, O[0])
    for N in range(1, 10):
        Q = y(Q, g)
        Q = z(Q)
        Q = A(Q)
        Q = C(Q, O[N])
    Q = y(Q, g)
    Q = z(Q)
    Q = C(Q, O[10])
    return bytes(Q)

def G(R, P):
    O = I(P)
    Q = list(R)
    Q = C(Q, O[10])
    for N in range(9, 0, -1):
        Q = D(Q)
        Q = y(Q, t)
        Q = C(Q, O[N])
        Q = F(Q)
    Q = D(Q)
    Q = y(Q, t)
    Q = C(Q, O[0])
    return bytes(Q)

def aes_cbc_encrypt(data, key, iv):
    assert len(data) % 16 == 0
    P = bytearray()
    Q = iv
    for N in range(0, len(data), 16):
        R = bytes((S ^ T for S, T in zip(data[N:N + 16], Q)))
        O = H(R, key)
        P += O
        Q = O
    return bytes(P)

def aes_cbc_decrypt(data, key, iv):
    assert len(data) % 16 == 0
    P = bytearray()
    Q = iv
    for N in range(0, len(data), 16):
        R = data[N:N + 16]
        O = G(R, key)
        P += bytes((S ^ T for S, T in zip(O, Q)))
        Q = R
    return bytes(P)
u = [214, 144, 233, 254, 204, 225, 61, 183, 22, 182, 20, 194, 40, 251, 44, 5, 43, 103, 154, 118, 42, 190, 4, 195, 170, 68, 19, 38, 73, 134, 6, 153, 156, 66, 80, 244, 145, 239, 152, 122, 51, 84, 11, 67, 237, 207, 172, 98, 228, 179, 28, 169, 201, 8, 232, 149, 128, 223, 148, 250, 117, 143, 63, 166, 71, 7, 167, 252, 243, 115, 23, 186, 131, 89, 60, 25, 230, 133, 79, 168, 104, 107, 129, 178, 113, 100, 218, 139, 248, 235, 15, 75, 112, 86, 157, 53, 30, 36, 14, 94, 99, 88, 209, 162, 37, 34, 124, 59, 1, 33, 120, 135, 212, 0, 70, 87, 159, 211, 39, 82, 76, 54, 2, 231, 160, 196, 200, 158, 234, 191, 138, 210, 64, 199, 56, 181, 163, 247, 242, 206, 249, 97, 21, 161, 224, 174, 93, 164, 155, 52, 26, 85, 173, 147, 50, 48, 245, 140, 177, 227, 29, 246, 226, 46, 130, 102, 202, 96, 192, 41, 35, 171, 13, 83, 78, 111, 213, 219, 55, 69, 222, 253, 142, 47, 3, 255, 106, 114, 109, 108, 91, 81, 141, 27, 175, 146, 187, 221, 188, 127, 17, 217, 92, 65, 31, 16, 90, 216, 10, 193, 49, 136, 165, 205, 123, 189, 45, 116, 208, 18, 184, 229, 180, 176, 137, 105, 151, 74, 12, 150, 119, 126, 101, 185, 241, 9, 197, 110, 198, 132, 24, 240, 125, 236, 58, 220, 77, 32, 121, 238, 95, 62, 215, 203, 57, 72]
p = [2746333894, 1453994832, 1736282519, 2993693404]
o = [462357, 472066609, 943670861, 1415275113, 1886879365, 2358483617, 2830087869, 3301692121, 3773296373, 4228057617, 404694573, 876298825, 1347903077, 1819507329, 2291111581, 2762715833, 3234320085, 3705924337, 4177462797, 337322537, 808926789, 1280531041, 1752135293, 2223739545, 2695343797, 3166948049, 3638552301, 4110090761, 269950501, 741554753, 1213159005, 1684763257]

def v(O, N):
    return (O << N | O >> 32 - N) & 4294967295

def r(P):
    N = [P >> 24 & 255, P >> 16 & 255, P >> 8 & 255, P & 255]
    N = [u[O] for O in N]
    return N[0] << 24 | N[1] << 16 | N[2] << 8 | N[3]

def j(O):
    N = r(O)
    return N ^ v(N, 2) ^ v(N, 10) ^ v(N, 18) ^ v(N, 24)

def q(O):
    N = r(O)
    return N ^ v(N, 13) ^ v(N, 23)

def E(R):
    P = [int.from_bytes(R[N:N + 4], 'big') for N in range(0, 16, 4)]
    O = [P[N] ^ p[N] for N in range(4)]
    Q = []
    for N in range(32):
        S = O[-3] ^ O[-2] ^ O[-1] ^ o[N]
        T = O[-4] ^ q(S)
        Q.append(T)
        O.append(T)
    return Q

def x(S, P):
    O = [int.from_bytes(S[N:N + 4], 'big') for N in range(0, 16, 4)]
    for N in range(32):
        Q = O[-3] ^ O[-2] ^ O[-1] ^ P[N]
        O.append(O[-4] ^ j(Q))
    R = O[32:][::-1]
    return b''.join((T.to_bytes(4, 'big') for T in R))

def sm4_cbc_encrypt_partial(data, key, iv):
    P = E(key)
    O = len(data) // 16 * 16
    S = bytearray()
    T = iv
    for N in range(0, O, 16):
        Q = data[N:N + 16]
        U = bytes((V ^ W for V, W in zip(Q, T)))
        R = x(U, P)
        S += R
        T = R
    S += data[O:]
    return bytes(S)

def sm4_cbc_decrypt_partial(data, key, iv):
    P = E(key)
    O = len(data) // 16 * 16
    S = bytearray()
    T = iv
    for N in range(0, O, 16):
        Q = data[N:N + 16]
        R = x(Q, P[::-1])
        S += bytes((U ^ V for U, V in zip(R, T)))
        T = Q
    S += data[O:]
    return bytes(S)
m = b'\xe3\x05b\x14\xd6\n %6\x96\x1b\x07t\xdc$\x02'
h = b'\x1dn\xebL\x86\xa9EDEr\x12!+C%/'
n = b'y{\xcd]}{\xb1\x11C\xd0\rq<\xda\xa8\x08'
i = n
s = 1601

def B(N):
    return N[0:8][::-1] + N[8:12][::-1] + N[12:16][::-1]

def L(S, V):
    T = S[0]
    N = T % 9
    R = T // 9
    O = R % 5
    P = R // 5
    U = l.unpack('<I', S[1:5])[0]
    Q = e.LZMADecompressor(format=e.FORMAT_RAW, filters=[{'id': e.FILTER_LZMA1, 'dict_size': U, 'lc': N, 'lp': O, 'pb': P}])
    return Q.decompress(S[5:], max_length=V)

def J(S, U=1 << 21, N=3, O=0, P=2):
    T = {'id': e.FILTER_LZMA1, 'dict_size': U, 'lc': N, 'lp': O, 'pb': P}
    R = e.LZMACompressor(format=e.FORMAT_RAW, filters=[T])
    Q = R.compress(S) + R.flush()
    V = (P * 5 + O) * 9 + N
    return bytes([V]) + l.pack('<I', U) + Q

def K(T, aa):
    S = T
    X = len(S)
    R = bytearray(aa)
    P = 0
    Q = 0
    while P < X:
        U = S[P]
        P += 1
        W = U >> 4
        if W == 15:
            while True:
                O = S[P]
                P += 1
                W += O
                if O != 255:
                    break
        if W:
            R[Q:Q + W] = S[P:P + W]
            P += W
            Q += W
        if P >= X:
            break
        V = S[P] | S[P + 1] << 8
        P += 2
        Y = (U & 15) + 4
        if U & 15 == 15:
            while True:
                O = S[P]
                P += 1
                Y += O
                if O != 255:
                    break
        Z = Q - V
        if V >= Y:
            R[Q:Q + Y] = R[Z:Z + Y]
            Q += Y
        else:
            for N in range(Y):
                R[Q] = R[Z]
                Q += 1
                Z += 1
    return bytes(R)

def w(N, O):
    P = N.index(b'\x00', O)
    return (N[O:P].decode('utf-8'), P + 1)

def decrypt_bundle(in_path, out_path):
    af = open(in_path, 'rb').read()
    Z = 0
    aa, Z = w(af, Z)
    if aa != 'UnityFS':
        raise ValueError('Khong phai file UnityFS .assetbundle')
    aD = l.unpack('>I', af[Z:Z + 4])[0]
    Z += 4
    V, Z = w(af, Z)
    U, Z = w(af, Z)
    az = af[Z:Z + 16]
    Z += 16
    ak = l.unpack('>I', af[Z:Z + 4])[0]
    Z += 4
    if aD >= 7:
        Z = (Z + 15) // 16 * 16
    aG = bool(ak & 1024)
    if not aG:
        raise ValueError('File nay khong co co AOV encryption - khong can giai ma.')
    aH = aes_cbc_decrypt(B(az), m, h)
    aF = int.from_bytes(aH[8:12], 'little')
    aK = int.from_bytes(aH[12:16], 'little')
    aJ = ak & 63
    aI = bool(ak & 128)
    ao = af[len(af) - aF:] if aI else af[Z:Z + aF]
    aw = sm4_cbc_decrypt_partial(ao, n, i)
    if aJ == 1:
        R = L(aw, aK)
    elif aJ in (2, 3):
        R = K(aw, aK)
    else:
        R = aw[:aK]
    if len(R) != aK:
        raise ValueError('Giai nen block info that bai (sai kich thuoc).')
    ac = 16
    aC = l.unpack_from('>I', R, ac)[0]
    ac += 4
    ap = []
    for N in range(aC):
        an, ae, ah, au = l.unpack_from('>HHII', R, ac)
        ac += 12
        ap.append((an, ah, au))
    aA = l.unpack_from('>I', R, ac)[0]
    ac += 4
    aj = []
    for N in range(aA):
        T, X = l.unpack_from('>QQ', R, ac)
        ac += 16
        aq = l.unpack_from('>I', R, ac)[0]
        ac += 4
        W = R.index(b'\x00', ac)
        ag = R[ac:W].decode('utf-8')
        ac = W + 1
        aj.append((X, T, aq, ag))
    if ac != len(R):
        raise ValueError('Parse block-info khong khop do dai (co the sai dinh dang).')
    aL = Z + aF if not aI else Z
    aL = (aL + 15) // 16 * 16
    S = aL
    ay = bytearray()
    for an, ah, au in ap:
        ad = af[S:S + ah]
        S += ah
        am = an & 63
        if am == 0:
            ai = ad[:au]
        elif am == 1:
            ai = L(ad, au)
        elif am in (2, 3):
            ai = K(ad, au)
        else:
            raise ValueError(f'Chua ho tro comp_type={am} cho data block (chi ho tro raw/LZMA/LZ4).')
        if len(ai) != au:
            raise ValueError('Giai nen data block that bai (sai kich thuoc).')
        ay += ai
    ax = J(bytes(ay))
    ar = bytearray()
    ar += b'\x00' * 16
    ar += l.pack('>I', 1)
    ar += l.pack('>IIH', len(ay), len(ax), 1)
    ar += l.pack('>I', aA)
    for X, T, aq, ag in aj:
        ar += l.pack('>QQI', X, T, aq)
        ar += ag.encode('utf-8') + b'\x00'
    aE = J(bytes(ar))
    at = b'UnityFS\x00' + l.pack('>I', aD) + V.encode() + b'\x00' + U.encode() + b'\x00'
    av = l.pack('>qII', 0, len(aE), len(ar)) + l.pack('>I', 1)
    ab = bytearray(at + av)
    Y = -len(ab) % 16
    ab += b'\x00' * Y
    ab += aE
    ab += ax
    al = len(ab)
    aB = len(at)
    ab[aB:aB + 8] = l.pack('>q', al)
    with open(out_path, 'wb') as O:
        O.write(bytes(ab))
    return {'files': [(P, Q) for N, Q, N, P in aj], 'out_size': al}

def M(N):

    def P(S):
        W = 16
        af = l.unpack_from('>I', S, W)[0]
        W += 4
        if not 0 < af <= 64:
            raise ValueError('block_count khong hop le')
        ab = []
        for R in range(af):
            ad, Y, aa = l.unpack_from('>IIH', S, W)
            W += 10
            ab.append((aa, Y, ad))
        ae = l.unpack_from('>I', S, W)[0]
        W += 4
        if not 0 < ae <= 256:
            raise ValueError('file_count khong hop le')
        Z = []
        for R in range(ae):
            V, T = l.unpack_from('>QQ', S, W)
            W += 16
            ac = l.unpack_from('>I', S, W)[0]
            W += 4
            U = S.index(b'\x00', W)
            X = S[W:U].decode('utf-8')
            W = U + 1
            Z.append((V, T, ac, X))
        if W != len(S):
            raise ValueError('do dai khong khop')
        return (ab, Z)

    def Q(S):
        X = 16
        ag = l.unpack_from('>I', S, X)[0]
        X += 4
        if not 0 < ag <= 64:
            raise ValueError('block_count khong hop le')
        ac = []
        for R in range(ag):
            ab, W, Z, ae = l.unpack_from('>HHII', S, X)
            X += 12
            ac.append((ab, Z, ae))
        af = l.unpack_from('>I', S, X)[0]
        X += 4
        if not 0 < af <= 256:
            raise ValueError('file_count khong hop le')
        aa = []
        for R in range(af):
            T, V = l.unpack_from('>QQ', S, X)
            X += 16
            ad = l.unpack_from('>I', S, X)[0]
            X += 4
            U = S.index(b'\x00', X)
            Y = S[X:U].decode('utf-8')
            X = U + 1
            aa.append((V, T, ad, Y))
        if X != len(S):
            raise ValueError('do dai khong khop')
        return (ac, aa)
    for O in (P, Q):
        try:
            return O(N)
        except Exception:
            continue
    raise ValueError('Khong doc duoc blocksinfo - file dau vao khong phai .assetbundle chuan (UnityFS) hoac dinh dang AOV hop le.')

def encrypt_bundle(in_path, out_path):
    ad = open(in_path, 'rb').read()
    Y = 0
    Z, Y = w(ad, Y)
    if Z != 'UnityFS':
        raise ValueError('Khong phai file UnityFS .assetbundle')
    aC = l.unpack('>I', ad[Y:Y + 4])[0]
    Y += 4
    V, Y = w(ad, Y)
    U, Y = w(ad, Y)
    ag, av, ay, ak = l.unpack('>qIII', ad[Y:Y + 20])
    Y += 20
    if ak & 1024:
        raise ValueError('File nay da o dang ma hoa AOV roi - khong can ma hoa lai.')
    if aC >= 7:
        Y = (Y + 15) // 16 * 16
    aH = ak & 63
    aG = bool(ak & 128)
    ao = ad[len(ad) - av:] if aG else ad[Y:Y + av]
    if aH == 1:
        R = L(ao, ay)
    elif aH in (2, 3):
        R = K(ao, ay)
    else:
        R = ao[:ay]
    if len(R) != ay:
        raise ValueError('Giai nen block info (nguon) that bai.')
    ab = 16
    ap, aj = M(R)
    az = len(aj)
    S = Y + av if not aG else Y
    ax = bytearray()
    for an, ah, au in ap:
        ac = ad[S:S + ah]
        S += ah
        am = an & 63
        if am == 0:
            ai = ac[:au]
        elif am in (2, 3):
            ai = K(ac, au)
        else:
            ai = L(ac, au)
        if len(ai) != au:
            raise ValueError('Giai nen data block (nguon) that bai.')
        ax += ai
    aw = J(bytes(ax))
    ar = bytearray()
    ar += b'\x00' * 16
    ar += l.pack('>I', 1)
    ar += l.pack('>HHII', 1, 0, len(aw), len(ax))
    ar += l.pack('>I', az)
    for W, T, aq, ae in aj:
        ar += l.pack('>QQI', T, W, aq)
        ar += ae.encode('utf-8') + b'\x00'
    aF = bytes(ar)
    aD = J(aF)
    aA = sm4_cbc_encrypt_partial(aD, n, i)
    at = b'UnityFS\x00' + l.pack('>I', aC) + V.encode() + b'\x00' + U.encode() + b'\x00'
    aI = l.pack('<q', 0) + l.pack('<I', len(aA)) + l.pack('<I', len(aF))
    aE = B(aes_cbc_encrypt(aI, m, h))
    aa = bytearray(at + aE + l.pack('>I', s))
    X = -len(aa) % 16
    aa += b'\x00' * X
    aa += aA
    af = -len(aa) % 16
    aa += b'\x00' * af
    aa += aw
    al = len(aa)
    aB = len(at)
    aI = l.pack('<q', al) + l.pack('<I', len(aA)) + l.pack('<I', len(aF))
    aE = B(aes_cbc_encrypt(aI, m, h))
    aa[aB:aB + 16] = aE
    with open(out_path, 'wb') as O:
        O.write(bytes(aa))
    return {'files': [(P, Q) for N, Q, N, P in aj], 'out_size': al}
