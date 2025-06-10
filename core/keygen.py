from Crypto.Util.number import bytes_to_long
import gmpy2

def gen_keys(p, q, e):
    n = p * q
    phi = (p - 1) * (q - 1)
    d = gmpy2.invert(e, phi)
    return n, phi, d

def encrypt(p, q, e, message):
    n = p * q
    m = bytes_to_long(message.encode())
    if m >= n:
        raise ValueError("明文过长，无法加密，请使用更大的 p 和 q。")
    c = pow(m, e, n)
    return c