import gmpy2
from core.factoring import factor_n
from core.utils import display_decryption


def decrypt_standard(p, q, e, c):
    phi = (p - 1) * (q - 1)
    d = int(gmpy2.invert(e, phi))
    return pow(c, d, p * q)

def decrypt_with_phi(n, e, phi, c):
    d = int(gmpy2.invert(e, phi))
    return pow(c, d, n)

def decrypt_with_d(n, d, c):
    return pow(c, d, n)

def decrypt_with_factoring(n, e, c):
    factors = factor_n(n)
    if not factors:
        print("❌ 无法分解 n，解密失败。")
        return
    p, q = factors
    print(f"🔓 分解结果: p = {p}, q = {q}")
    m = decrypt_standard(p, q, e, c)
    display_decryption(m)