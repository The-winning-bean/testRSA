import gmpy2
from core.utils import display_decryption
from core.decrypt import decrypt_standard
from core.wiener import wiener_attack

def decrypt_small_e_case(n, e, c):
    """
    当 e 较小且 m^e < n 时，尝试通过 e 次整数根恢复明文。
    """
    print("\n⚡ 正在尝试小 e 解密攻击 ...")

    # 如果 m^e < n，则密文就是 m^e，无需 mod
    m_root, exact = gmpy2.iroot(c, e)
    if exact:
        print("✅ 成功从密文中取 e 次根，说明 m^e < n")
        display_decryption(int(m_root))
        return True

    # 否则尝试 m^e = c + k*n 的情况，寻找 k 使得根存在
    k = 1
    max_attempts = 100000
    while k < max_attempts:
        test = c + k * n
        m_root, exact = gmpy2.iroot(test, e)
        if exact:
            print(f"✅ 成功找到 k = {k} 使得 (c + k*n) 可开 e 次整数根")
            display_decryption(int(m_root))
            return True
        k += 1

    print("❌ 小 e 攻击尝试失败。")
    return False

def common_modulus_attack(n, e1, e2, c1, c2):
    print("\n⚡ 正在尝试真正的共模攻击 ...")
    if gmpy2.gcd(e1, e2) != 1:
        print("❌ e1 与 e2 不互质，无法执行共模攻击。")
        return

    try:
        # 使用扩展欧几里得算法求解 s1 和 s2
        _, s1, s2 = gmpy2.gcdext(e1, e2)

        # 如果 s1 或 s2 为负，则使用模逆元处理
        if s1 < 0:
            c1 = gmpy2.invert(c1, n)
            s1 = -s1
        if s2 < 0:
            c2 = gmpy2.invert(c2, n)
            s2 = -s2

        m = pow(c1, s1, n) * pow(c2, s2, n) % n
        print("✅ 共模攻击成功，恢复明文如下：")
        display_decryption(m)
    except Exception as e:
        print(f"❌ 共模攻击失败: {e}")

def decrypt_common_modulus(n1, c1, n2, c2, e):
    print("\n⚡ 尝试共模攻击 ...")
    p = int(gmpy2.gcd(n1, n2))
    if p == 1 or p == n1 or p == n2:
        print("❌ 两个模数没有共享素因子，无法进行共模攻击。")
        return

    q = n1 // p
    phi = (p - 1) * (q - 1)
    d = int(gmpy2.invert(e, phi))
    m = pow(c1, d, n1)

    print(f"✅ 共模攻击成功，提取因子: p = {p}")
    display_decryption(m)

def recover_p_from_high_bits(n, e, c, p_high_bits, bit_len=128):
    print(f"\n🔍 正在尝试恢复 p，给定高 {bit_len} 位...")

    high = p_high_bits << bit_len
    low_max = 1 << bit_len

    for low in range(low_max):
        candidate_p = high | low
        if n % candidate_p == 0:
            p = candidate_p
            q = n // p
            print(f"✅ 成功恢复 p！\np = {p}\nq = {q}")
            m = decrypt_standard(p, q, e, c)
            display_decryption(m)
            return True

        # 可以根据需要设置更小的尝试次数以加速测试
        if low % 1000000 == 0:
            print(f"⏳ 已尝试低位 {low}/{low_max}")

    print("❌ 未能恢复 p，请检查高位是否正确，或增加低位位数。")
    return False

def try_wiener_attack(n, e, c):
    d = wiener_attack(e, n)
    if d:
        m = pow(c, d, n)
        display_decryption(m)
        return True
    return False