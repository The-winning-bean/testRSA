import requests

def factordb_lookup(n):
    try:
        print("🌐 查询 FactorDB API 分解 n ...")
        response = requests.get(f"https://factordb.com/api?query={n}")
        data = response.json()

        if data['status'] != 'FF' and data['status'] != 'CF':
            print("❌ FactorDB 无法确认分解，状态:", data['status'])
            return None

        factors = data['factors']
        if len(factors) != 2:
            print("❌ FactorDB 返回的因子数量异常:", len(factors))
            return None

        p, _ = factors[0]
        q, _ = factors[1]
        p = int(p)
        q = int(q)

        if p * q == n:
            print(f"✅ FactorDB 分解成功:\np = {p}\nq = {q}")
            return p, q
        else:
            print("⚠️ FactorDB 因子不匹配原始 n。")
            return None

    except Exception as e:
        print(f"❌ FactorDB API 请求失败: {e}")
        return None