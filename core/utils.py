from Crypto.Util.number import bytes_to_long, long_to_bytes

# ========== 通用方法 ==========

def parse_input_int(s):
    """
    支持十进制、十六进制（0x）、八进制（0o）、二进制（0b）输入。
    """
    s = s.strip().lower()
    if s.startswith("0x"):
        return int(s, 16)
    elif s.startswith("0o"):
        return int(s, 8)
    elif s.startswith("0b"):
        return int(s, 2)
    else:
        return int(s)

def display_decryption(m, mode=3):
    decrypted_bytes = long_to_bytes(m)

    if mode == 1:
        print(f"\n🔟 明文整数: {m}")
    elif mode == 2:
        try:
            decoded = decrypted_bytes.decode('utf-8')
            print(f"\n✅ 解码为 UTF-8 文本: {decoded}")
        except UnicodeDecodeError:
            print("\n❌ 解码失败：非 UTF-8 文本。")
    elif mode == 3:
        print(f"\n🔟 明文整数: {m}")
        print(f"📦 字节流: {decrypted_bytes}")
        try:
            decoded = decrypted_bytes.decode('utf-8')
            print(f"✅ UTF-8 解码结果: {decoded}")
        except UnicodeDecodeError:
            print("❌ 无法解码为 UTF-8 文本。")

def check_message_length(p, q, message):
    n = p * q
    m = bytes_to_long(message.encode())
    return m < n