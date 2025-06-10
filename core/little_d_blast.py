from Crypto.Util.number import *
from sympy import nextprime
import gmpy2

# 已知明文（从 flag 中 bytes_to_long 计算得到）
m = 365570067986928236989573788230270407130085464313909252527513197832758480604817399268366313889131551088558394832418649150417321940578277210433329648095352247884911033780856767602238960538520312352025465812228462858158997175162265505345470937926646520732298730237509998898024691120409770049168658027104966429925920045510148612448817

print("🔍 正在尝试爆破 d（1~100）...")

# 枚举 d
for d in range(1, 100):
    print(f"尝试 d = {d}")
    # 枚举 p（4096 位是猜测，也可以从 m 开始估计）
    p = nextprime(2 ** 2047)

    for _ in range(1000):  # 尝试 1000 对 (p, q)
        q = nextprime(p + 2 ** 16)
        n = p * q
        phi = (p - 1) * (q - 1)

        try:
            e = inverse(d, phi)
        except:
            p = nextprime(p)
            continue

        c = pow(m, e, n)
        m_test = pow(c, d, n)

        if m_test == m:
            print("🎯 找到了正确的参数！")
            print(f"p = {p}")
            print(f"q = {q}")
            print(f"n = {n}")
            print(f"d = {d}")
            print(f"e = {e}")
            print(f"c = {c}")
            print("flag:", long_to_bytes(m))
            exit(0)

        p = nextprime(p)

print("❌ 未找到合适参数，请扩大搜索空间")
