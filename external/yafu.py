import re
import subprocess

def yafu_factor(n, path=".\external\yafu-1.34\yafu-x64.exe"):
    try:
        cmd = f'{path} factor({n})'
        print(f"\n🛠 正在运行命令: {cmd}\n")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)

        # 打印原始输出，便于调试
        print("=" * 20 + "📤 YAFU 输出开始" + "=" * 20)
        print(result.stdout)
        print("=" * 20 + "📤 YAFU 输出结束" + "=" * 20 + "\n")

        output = result.stdout

        # 提取所有 Pxx = number 的因子
        factors = re.findall(r'P\d+\s*=\s*(\d+)', output)

        if len(factors) >= 2:
            p = int(factors[0])
            q = int(factors[1])
            if p * q == n:
                print(f"✅ 成功提取因子:\np = {p}\nq = {q}")
                return p, q
            else:
                print(f"⚠️ 警告：提取的因子乘积不等于 n。")
        else:
            print(f"⚠️ 未找到足够的因子 (找到 {len(factors)})。")
    except Exception as e:
        print(f"❌ 调用 YAFU 失败：{e}")
    return None