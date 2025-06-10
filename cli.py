from core.attacks import (
    decrypt_small_e_case, common_modulus_attack, decrypt_common_modulus,
    recover_p_from_high_bits
)
from core.decrypt import (
    decrypt_standard, decrypt_with_phi, decrypt_with_d, decrypt_with_factoring
)
from core.factoring import factor_n
from core.keygen import gen_keys, encrypt
from core.utils import parse_input_int, display_decryption, check_message_length
from core.wiener import wiener_attack
import libnum
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def run_cli():
    print("═" * 50)
    print("    RSA 多功能工具 -- 支持加密、解密、分解模数")
    print("═" * 50)
    print("🔐 密钥与加密功能")
    print(" 1. 生成密钥              （输入 p, q, e）")
    print(" 2. 加密明文              （输入 p, q, e, 明文）")
    print(" 3. 检查明文是否可加密    （输入 p, q, 明文）")
    print("─" * 50)
    print("🔓 解密功能")
    print(" 4. 解密密文 - 标准模式     （输入 p, q, e, c）")
    print(" 5. 解密密文 - 已知 φ(n)    （输入 n, e, φ(n), c）")
    print(" 6. 解密密文 - 已知私钥 d   （输入 n, d, c）")
    print(" 7. 解密密文 - 假设 n 为素数（输入 n, e, c）")
    print(" 8. 解密密文 - 自动分解 n   （输入 n, e, c）")
    print(" 9. 解密文件 - 自动分解 n   （输入 n, e, (p, q), file_path）")
    print("10. 共模攻击（共 e）        （输入 n1, c1, n2, c2, e）")
    print("11. 共模攻击（共 n）        （输入 n, e1, c1, e2, c2）")
    print("12. 高位泄露攻击（已知高位 p）（输入p(泄露), n, e, c）")

    print("═" * 50)

    choice = input("📌 请选择操作 (1-12): ").strip()

    try:
        if choice == '1':
            print("\n🔧 密钥生成")
            p = parse_input_int(input("🔟 输入 p: "))
            q = parse_input_int(input("🔟 输入 q: "))
            e = parse_input_int(input("🔟 输入 e: "))
            n, phi, d = gen_keys(p, q, e)
            print("\n✅ 密钥生成完成：")
            print(f"🔐 n      = {n}")
            print(f"φ(n)     = {phi}")
            print(f"🔑 d      = {d}")

        elif choice == '2':
            print("\n📝 明文加密")
            p = parse_input_int(input("🔟 输入 p: "))
            q = parse_input_int(input("🔟 输入 q: "))
            e = parse_input_int(input("🔟 输入 e: "))
            message = input("💬 输入明文消息: ")
            c = encrypt(p, q, e, message)
            print(f"\n✅ 加密完成：密文 c = {c}")

        elif choice == '3':
            print("\n📏 检查明文长度")
            p = parse_input_int(input("🔟 输入 p: "))
            q = parse_input_int(input("🔟 输入 q: "))
            message = input("💬 输入明文消息: ")
            if check_message_length(p, q, message):
                print("✅ 明文可以加密。")
            else:
                print("❌ 明文过长，无法加密，请选择更大的 p 和 q。")

        elif choice == '4':
            print("\n🔓 解密（标准模式）")
            p = parse_input_int(input("🔟 输入 p: "))
            q = parse_input_int(input("🔟 输入 q: "))
            e = parse_input_int(input("🔟 输入 e: "))
            c = parse_input_int(input("🔐 输入密文 c: "))
            m = decrypt_standard(p, q, e, c)
            print("\n📤 请选择解密结果显示格式：")
            print(" 1. 仅输出整数")
            print(" 2. 输出 UTF-8 文本")
            print(" 3. 输出整数 + 字节流 + 尝试解码")
            mode = input("输入编号 (1-3): ").strip()
            display_decryption(m, int(mode) if mode in {'1', '2', '3'} else 3)

        elif choice == '5':
            print("\n🔓 解密（已知 φ(n)）")
            n = parse_input_int(input("🔟 输入 n: "))
            e = parse_input_int(input("🔟 输入 e: "))
            phi = parse_input_int(input("🔟 输入 φ(n): "))
            c = parse_input_int(input("🔐 输入密文 c: "))
            m = decrypt_with_phi(n, e, phi, c)
            display_decryption(m)

        elif choice == '6':
            print("\n🔓 解密（已知私钥 d）")
            n = parse_input_int(input("🔟 输入 n: "))
            d = parse_input_int(input("🔑 输入私钥 d: "))
            c = parse_input_int(input("🔐 输入密文 c: "))
            m = decrypt_with_d(n, d, c)
            display_decryption(m)

        elif choice == '7':
            print("\n🔓 解密（假设 n 为素数）")
            n = parse_input_int(input("🔟 输入 n: "))
            e = parse_input_int(input("🔟 输入 e: "))
            c = parse_input_int(input("🔐 输入密文 c: "))
            phi = n - 1
            print("⚠️ 假设 n 为素数，因此 φ(n) = n - 1")
            m = decrypt_with_phi(n, e, phi, c)
            display_decryption(m)

        elif choice == '8':
            print("\n🔓 解密（自动分解 n 或小 e 尝试）")
            n = parse_input_int(input("🔟 输入 n: "))
            e = parse_input_int(input("🔟 输入 e: "))
            c = parse_input_int(input("🔐 输入密文 c: "))

            # Step 1: 尝试小 e 攻击
            if e <= 10:
                print(f"⚠️ 由于 e = {e} 非常小，尝试小 e 解密攻击 ...")
                if decrypt_small_e_case(n, e, c):
                    return

            # Step 2: 尝试 Wiener's Attack
            print("⚡ 尝试 Wiener's Attack（低解密指数攻击） ...")
            d = wiener_attack(e, n)
            if d:
                print(f"✅ Wiener 攻击成功，恢复私钥 d = {d}")
                m = pow(c, d, n)
                display_decryption(m)
                return
            else:
                print("❌ Wiener 攻击失败，继续尝试分解 n ...")

            # Step 3: 尝试分解 n
            decrypt_with_factoring(n, e, c)


        elif choice == '9':
            print("\n📂 解密文件（通过已知 n, e, p, q 构造私钥，若未提供则自动尝试分解）")
            n = parse_input_int(input("🔟 输入 n: "))
            e = parse_input_int(input("🔟 输入 e: "))

            # 尝试读取 p 和 q，如果为空则自动触发分解
            p_input = input("🔐 输入质因子 p（可留空自动尝试）: ").strip()
            q_input = input("🔐 输入质因子 q（可留空自动尝试）: ").strip()

            if p_input and q_input:
                p = parse_input_int(p_input)
                q = parse_input_int(q_input)
                print("✅ 已输入 p 和 q，将使用它们解密文件。")
            else:
                print("🔍 未提供 p 和 q，尝试自动分解 n ...")
                factors = factor_n(n)
                if not factors:
                    print("❌ 分解失败，无法解密。")
                    return
                p, q = factors
                print(f"✅ 分解成功: p = {p}, q = {q}")

            try:
                phi = (p - 1) * (q - 1)
                d = libnum.invmod(e, phi)
            except Exception as ex:
                print(f"❌ 无法计算私钥 d: {ex}")
                return

            try:
                private_key = RSA.construct((n, e, d, p, q))
                rsa = PKCS1_OAEP.new(private_key)
                file_path = input("📂 请输入加密文件路径（如 flag.enc）: ").strip()
                with open(file_path, 'rb') as f:
                    ciphertext = f.read()
                plaintext = rsa.decrypt(ciphertext)
                print("✅ 解密成功，内容如下：")
                try:
                    print(plaintext.decode())
                except:
                    print(plaintext)
            except Exception as ex:
                print(f"❌ 解密失败: {ex}")


        elif choice == '10':
            print("\n🔓 共模攻击解密")
            n1 = parse_input_int(input("🔟 输入 n1: "))
            c1 = parse_input_int(input("🔐 输入密文 c1: "))
            n2 = parse_input_int(input("🔟 输入 n2: "))
            c2 = parse_input_int(input("🔐 输入密文 c2: "))
            e = parse_input_int(input("🔟 输入公钥 e: "))
            decrypt_common_modulus(n1, c1, n2, c2, e)

        elif choice == '11':
            print("\n🔓 共模攻击（相同模数，不同指数）")
            n = parse_input_int(input("🔟 输入模数 n: "))
            e1 = parse_input_int(input("🔐 输入公钥 e1: "))
            c1 = parse_input_int(input("🔐 输入密文 c1: "))
            e2 = parse_input_int(input("🔐 输入公钥 e2: "))
            c2 = parse_input_int(input("🔐 输入密文 c2: "))
            common_modulus_attack(n, e1, e2, c1, c2)

        elif choice == '12':
            print("\n🔓 高位泄露攻击：恢复 p 并解密")
            n = parse_input_int(input("🔟 输入模数 n: "))
            e = parse_input_int(input("🔟 输入公钥 e: "))
            c = parse_input_int(input("🔐 输入密文 c: "))
            p_high = parse_input_int(input("🧩 输入已知的 p 高位（右对齐前）: "))
            bit_len = parse_input_int(input("📏 高位位数（如 128）: "))
            recover_p_from_high_bits(n, e, c, p_high, bit_len)


        else:
            print("❌ 无效选项，请选择 1~12 之间的数字。")

    except Exception as e:
        print(f"\n🚨 出现异常：{e}")
