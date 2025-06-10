import gmpy2

def continued_fraction(n, d):
    """生成 n/d 的连分数展开"""
    while d:
        a = n // d
        yield a
        n, d = d, n - a * d

def convergents(cf):
    """从连分数构造逼近（收敛项）"""
    convs = []
    for i in range(len(cf)):
        num, denom = 1, 0
        for a in reversed(cf[:i+1]):
            num, denom = denom + num * a, num
        convs.append((num, denom))
    return convs

def is_perfect_square(n):
    root = gmpy2.isqrt(n)
    return root * root == n

def wiener_attack(e, n):
    cf = list(continued_fraction(e, n))
    for k, d in convergents(cf):
        if k == 0:
            continue
        # phi = (ed - 1) / k must be integer
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # Solve for p and q from phi and n
        s = n - phi + 1
        discrim = s * s - 4 * n
        if discrim >= 0 and is_perfect_square(discrim):
            return d
    return None
