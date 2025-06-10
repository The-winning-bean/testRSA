import gmpy2
from external.yafu import yafu_factor
from external.factordb import factordb_lookup

# ========== n 分解方法 ==========
def fermat_factor(n):
    a = gmpy2.isqrt(n)
    if a * a < n:
        a += 1
    b2 = a * a - n
    while not gmpy2.is_square(b2):
        a += 1
        b2 = a * a - n
        if a - gmpy2.isqrt(n) > 1000000:
            return None
    b = gmpy2.isqrt(b2)
    p = a - b
    q = a + b
    return int(p), int(q)

def trial_division(n, limit=1000000):
    for i in range(2, limit):
        if n % i == 0:
            return i, n // i
    return None

def factor_n(n):
    print("\n🔍 正在尝试分解 n ...")

    res = fermat_factor(n)
    if res:
        print("✅ Fermat 分解成功。")
        return res

    print("❗ Fermat 分解失败，尝试试除法 ...")
    res = trial_division(n)
    if res:
        print("✅ 试除成功。")
        return res

    print("❗ 试除失败，尝试调用 YAFU 工具分解（如配置正确） ...")
    res = yafu_factor(n)
    if res:
        print("✅ YAFU 分解成功。")
        return res

    print("❗ YAFU 失败，尝试使用 FactorDB API 分解 ...")
    res = factordb_lookup(n)
    if res:
        print("✅ FactorDB 分解成功。")
        return res

    print("❌ 所有方法均失败，无法分解 n。")
    return None