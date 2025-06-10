import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
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
import time

class RSAToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA 多功能工具")
        self.root.geometry("900x700")
        self.root.configure(bg="#0d1117")
        
        # 设置可爱风格字体
        self.title_font = ("Arial Rounded MT Bold", 16)
        self.section_font = ("Arial Rounded MT Bold", 12)
        self.label_font = ("Segoe UI", 9)
        self.button_font = ("Segoe UI", 9, "bold")
        
        # 创建主题颜色
        self.bg_color = "#0d1117"        # 深色背景
        self.section_bg = "#161b22"       # 区块背景
        self.text_bg = "#0d1117"          # 文本背景
        self.accent_color = "#58a6ff"     # 蓝色强调色
        self.hacker_green = "#39ff14"     # 黑客绿
        self.purple = "#d2a8ff"           # 紫色
        self.pink = "#ff7b72"             # 粉色
        
        # 创建主框架
        self.create_widgets()
        
        # 初始化状态
        self.current_tab = "keygen"
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, "⚡ RSA 多功能工具已启动！\n")
        self.output_text.insert(tk.END, "💻 请选择左侧功能开始操作...\n")
        self.output_text.configure(state=tk.DISABLED)
        
    def create_widgets(self):
        # 创建标题栏
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(title_frame, text="🔒 RSA 多功能工具", 
                              font=self.title_font, fg=self.accent_color, 
                              bg=self.bg_color)
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(title_frame, 
                                 text="支持加密、解密、攻击和密钥生成", 
                                 font=("Segoe UI", 10), fg="#8b949e", 
                                 bg=self.bg_color)
        subtitle_label.pack(side=tk.LEFT, padx=10)
        
        # 创建分隔线
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建主内容区
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建左侧导航栏
        nav_frame = tk.Frame(main_frame, bg=self.section_bg, width=180)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 导航标题
        nav_title = tk.Label(nav_frame, text="功能导航", 
                            font=self.section_font, fg=self.pink, 
                            bg=self.section_bg, padx=10, pady=10)
        nav_title.pack(fill=tk.X)
        
        # 导航按钮
        nav_buttons = [
            ("🔑 密钥生成", "keygen"),
            ("📝 加密明文", "encrypt"),
            ("🔓 解密功能", "decrypt"),
            ("⚔️ 攻击工具", "attacks"),
            ("📂 文件操作", "file"),
            ("📊 状态输出", "output")
        ]
        
        self.nav_vars = {}
        for text, var in nav_buttons:
            btn = tk.Button(nav_frame, text=text, font=self.button_font,
                           command=lambda v=var: self.show_tab(v),
                           bg=self.section_bg, fg="#c9d1d9", 
                           activebackground="#30363d", activeforeground="white",
                           relief=tk.FLAT, padx=10, pady=8, anchor=tk.W)
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.nav_vars[var] = btn
        
        # 创建右侧内容区
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建选项卡容器
        self.tabs_container = tk.Frame(content_frame, bg=self.bg_color)
        self.tabs_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建输出区域
        output_frame = tk.Frame(content_frame, bg=self.bg_color)
        output_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        output_label = tk.Label(output_frame, text="操作日志", 
                               font=self.section_font, fg=self.accent_color, 
                               bg=self.bg_color)
        output_label.pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, width=80, height=10,
            bg=self.text_bg, fg=self.hacker_green, insertbackground="white",
            font=("Consolas", 9)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.configure(state=tk.DISABLED)
        
        # 初始化各个功能选项卡
        self.tabs = {}
        self.create_keygen_tab()
        self.create_encrypt_tab()
        self.create_decrypt_tab()
        self.create_attacks_tab()
        self.create_file_tab()
        
        # 默认显示密钥生成选项卡
        self.show_tab("keygen")
    
    def show_tab(self, tab_name):
        # 隐藏所有选项卡
        for tab in self.tabs.values():
            tab.pack_forget()
        
        # 显示选中的选项卡
        self.tabs[tab_name].pack(fill=tk.BOTH, expand=True)
        self.current_tab = tab_name
        
        # 更新导航按钮状态
        for var, btn in self.nav_vars.items():
            if var == tab_name:
                btn.configure(bg="#30363d", fg="white")
            else:
                btn.configure(bg=self.section_bg, fg="#c9d1d9")
    
    def log(self, message, color=None):
        self.output_text.configure(state=tk.NORMAL)
        if color:
            self.output_text.tag_configure(color, foreground=color)
            self.output_text.insert(tk.END, message + "\n", color)
        else:
            self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)
    
    def create_keygen_tab(self):
        frame = tk.Frame(self.tabs_container, bg=self.bg_color)
        self.tabs["keygen"] = frame
        
        section = tk.LabelFrame(frame, text="🔑 密钥生成", 
                               font=self.section_font, fg=self.accent_color,
                               bg=self.section_bg, padx=10, pady=10)
        section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 输入字段
        input_frame = tk.Frame(section, bg=self.section_bg)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="质数 p:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.p_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.p_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="质数 q:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.q_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.q_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="公钥指数 e:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.e_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.e_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 按钮
        btn_frame = tk.Frame(section, bg=self.section_bg)
        btn_frame.pack(fill=tk.X, pady=10)
        
        gen_btn = tk.Button(btn_frame, text="生成密钥", font=self.button_font,
                          command=self.generate_keys,
                          bg=self.accent_color, fg="white", padx=15, pady=5)
        gen_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        result_frame = tk.Frame(section, bg=self.section_bg)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(result_frame, text="生成结果:", font=self.section_font, 
                bg=self.section_bg, fg=self.purple).pack(anchor=tk.W, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, width=70, height=8,
            bg="#161b22", fg=self.hacker_green, 
            font=("Consolas", 9)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.configure(state=tk.DISABLED)
    
    def create_encrypt_tab(self):
        frame = tk.Frame(self.tabs_container, bg=self.bg_color)
        self.tabs["encrypt"] = frame
        
        section = tk.LabelFrame(frame, text="🔐 加密功能", 
                               font=self.section_font, fg=self.accent_color,
                               bg=self.section_bg, padx=10, pady=10)
        section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 输入字段
        input_frame = tk.Frame(section, bg=self.section_bg)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="公钥模数 n:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.enc_n_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.enc_n_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="公钥指数 e:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.enc_e_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.enc_e_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="明文消息:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.message_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.message_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 按钮
        btn_frame = tk.Frame(section, bg=self.section_bg)
        btn_frame.pack(fill=tk.X, pady=10)
        
        encrypt_btn = tk.Button(btn_frame, text="加密消息", font=self.button_font,
                          command=self.encrypt_message,
                          bg=self.accent_color, fg="white", padx=15, pady=5)
        encrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        result_frame = tk.Frame(section, bg=self.section_bg)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(result_frame, text="加密结果:", font=self.section_font, 
                bg=self.section_bg, fg=self.purple).pack(anchor=tk.W, pady=5)
        
        self.enc_result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, width=70, height=8,
            bg="#161b22", fg=self.hacker_green, 
            font=("Consolas", 9)
        )
        self.enc_result_text.pack(fill=tk.BOTH, expand=True)
        self.enc_result_text.configure(state=tk.DISABLED)
    
    def create_decrypt_tab(self):
        frame = tk.Frame(self.tabs_container, bg=self.bg_color)
        self.tabs["decrypt"] = frame
        
        section = tk.LabelFrame(frame, text="🔓 解密功能", 
                               font=self.section_font, fg=self.accent_color,
                               bg=self.section_bg, padx=10, pady=10)
        section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 解密方法选择
        method_frame = tk.Frame(section, bg=self.section_bg)
        method_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(method_frame, text="解密方法:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").pack(side=tk.LEFT, padx=5)
        
        self.decrypt_method = tk.StringVar(value="standard")
        methods = [
            ("标准模式 (p, q, e, c)", "standard"),
            ("已知 φ(n) (n, e, φ(n), c)", "phi"),
            ("已知私钥 d (n, d, c)", "d"),
            ("自动分解 n (n, e, c)", "factoring")
        ]
        
        for text, mode in methods:
            rb = tk.Radiobutton(method_frame, text=text, variable=self.decrypt_method, 
                               value=mode, font=self.label_font, bg=self.section_bg, 
                               fg="#c9d1d9", selectcolor=self.bg_color)
            rb.pack(side=tk.LEFT, padx=5)
        
        # 输入字段
        input_frame = tk.Frame(section, bg=self.section_bg)
        input_frame.pack(fill=tk.X, pady=10)
        
        # 创建所有输入字段，根据方法显示/隐藏
        self.dec_entries = {}
        fields = [
            ("n", "公钥模数 n:"),
            ("e", "公钥指数 e:"),
            ("p", "质数 p:"),
            ("q", "质数 q:"),
            ("phi", "φ(n):"),
            ("d", "私钥 d:"),
            ("c", "密文 c:")
        ]
        
        for i, (field, label) in enumerate(fields):
            tk.Label(input_frame, text=label, font=self.label_font, 
                    bg=self.section_bg, fg="#c9d1d9").grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.dec_entries[field] = entry
        
        # 按钮
        btn_frame = tk.Frame(section, bg=self.section_bg)
        btn_frame.pack(fill=tk.X, pady=10)
        
        decrypt_btn = tk.Button(btn_frame, text="解密密文", font=self.button_font,
                          command=self.decrypt_message,
                          bg=self.accent_color, fg="white", padx=15, pady=5)
        decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        result_frame = tk.Frame(section, bg=self.section_bg)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(result_frame, text="解密结果:", font=self.section_font, 
                bg=self.section_bg, fg=self.purple).pack(anchor=tk.W, pady=5)
        
        self.dec_result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, width=70, height=8,
            bg="#161b22", fg=self.hacker_green, 
            font=("Consolas", 9)
        )
        self.dec_result_text.pack(fill=tk.BOTH, expand=True)
        self.dec_result_text.configure(state=tk.DISABLED)
    
    def create_attacks_tab(self):
        frame = tk.Frame(self.tabs_container, bg=self.bg_color)
        self.tabs["attacks"] = frame
        
        section = tk.LabelFrame(frame, text="⚔️ RSA 攻击工具", 
                               font=self.section_font, fg=self.accent_color,
                               bg=self.section_bg, padx=10, pady=10)
        section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 攻击方法选择
        method_frame = tk.Frame(section, bg=self.section_bg)
        method_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(method_frame, text="攻击方法:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").pack(side=tk.LEFT, padx=5)
        
        self.attack_method = tk.StringVar(value="common_modulus")
        methods = [
            ("共模攻击 (相同 n)", "common_modulus"),
            ("共模攻击 (相同 e)", "common_e"),
            ("高位泄露攻击", "high_bits"),
            ("Wiener 攻击", "wiener")
        ]
        
        for text, mode in methods:
            rb = tk.Radiobutton(method_frame, text=text, variable=self.attack_method, 
                               value=mode, font=self.label_font, bg=self.section_bg, 
                               fg="#c9d1d9", selectcolor=self.bg_color)
            rb.pack(side=tk.LEFT, padx=5)
        
        # 输入字段
        input_frame = tk.Frame(section, bg=self.section_bg)
        input_frame.pack(fill=tk.X, pady=10)
        
        # 创建所有输入字段
        self.attack_entries = {}
        fields = [
            ("n1", "模数 n1:"),
            ("n2", "模数 n2:"),
            ("e1", "指数 e1:"),
            ("e2", "指数 e2:"),
            ("c1", "密文 c1:"),
            ("c2", "密文 c2:"),
            ("p_high", "p 的高位:"),
            ("bit_len", "高位位数:")
        ]
        
        for i, (field, label) in enumerate(fields):
            row = i // 2
            col = i % 2 * 2
            tk.Label(input_frame, text=label, font=self.label_font, 
                    bg=self.section_bg, fg="#c9d1d9").grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            entry = tk.Entry(input_frame, width=30, bg="#161b22", fg="white", insertbackground="white")
            entry.grid(row=row, column=col+1, padx=5, pady=5)
            self.attack_entries[field] = entry
        
        # 按钮
        btn_frame = tk.Frame(section, bg=self.section_bg)
        btn_frame.pack(fill=tk.X, pady=10)
        
        attack_btn = tk.Button(btn_frame, text="执行攻击", font=self.button_font,
                          command=self.perform_attack,
                          bg=self.accent_color, fg="white", padx=15, pady=5)
        attack_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        result_frame = tk.Frame(section, bg=self.section_bg)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(result_frame, text="攻击结果:", font=self.section_font, 
                bg=self.section_bg, fg=self.purple).pack(anchor=tk.W, pady=5)
        
        self.attack_result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, width=70, height=8,
            bg="#161b22", fg=self.hacker_green, 
            font=("Consolas", 9)
        )
        self.attack_result_text.pack(fill=tk.BOTH, expand=True)
        self.attack_result_text.configure(state=tk.DISABLED)
    
    def create_file_tab(self):
        frame = tk.Frame(self.tabs_container, bg=self.bg_color)
        self.tabs["file"] = frame
        
        section = tk.LabelFrame(frame, text="📂 文件操作", 
                               font=self.section_font, fg=self.accent_color,
                               bg=self.section_bg, padx=10, pady=10)
        section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 输入字段
        input_frame = tk.Frame(section, bg=self.section_bg)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="公钥模数 n:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_n_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.file_n_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="公钥指数 e:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_e_entry = tk.Entry(input_frame, width=50, bg="#161b22", fg="white", insertbackground="white")
        self.file_e_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 质数输入
        prime_frame = tk.Frame(input_frame, bg=self.section_bg)
        prime_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        tk.Label(prime_frame, text="质数 p (可选):", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_p_entry = tk.Entry(prime_frame, width=25, bg="#161b22", fg="white", insertbackground="white")
        self.file_p_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(prime_frame, text="质数 q (可选):", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.file_q_entry = tk.Entry(prime_frame, width=25, bg="#161b22", fg="white", insertbackground="white")
        self.file_q_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 文件选择
        file_frame = tk.Frame(input_frame, bg=self.section_bg)
        file_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        tk.Label(file_frame, text="加密文件路径:", font=self.label_font, 
                bg=self.section_bg, fg="#c9d1d9").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_path_entry = tk.Entry(file_frame, width=40, bg="#161b22", fg="white", insertbackground="white")
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)
        
        browse_btn = tk.Button(file_frame, text="浏览...", font=self.button_font,
                             command=self.browse_file,
                             bg="#6e7681", fg="white", padx=5)
        browse_btn.grid(row=0, column=2, padx=5)
        
        # 按钮
        btn_frame = tk.Frame(section, bg=self.section_bg)
        btn_frame.pack(fill=tk.X, pady=10)
        
        decrypt_btn = tk.Button(btn_frame, text="解密文件", font=self.button_font,
                          command=self.decrypt_file,
                          bg=self.accent_color, fg="white", padx=15, pady=5)
        decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        result_frame = tk.Frame(section, bg=self.section_bg)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(result_frame, text="解密结果:", font=self.section_font, 
                bg=self.section_bg, fg=self.purple).pack(anchor=tk.W, pady=5)
        
        self.file_result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, width=70, height=8,
            bg="#161b22", fg=self.hacker_green, 
            font=("Consolas", 9)
        )
        self.file_result_text.pack(fill=tk.BOTH, expand=True)
        self.file_result_text.configure(state=tk.DISABLED)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择加密文件",
            filetypes=[("All files", "*.*")]
        )
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
    
    def generate_keys(self):
        try:
            p = parse_input_int(self.p_entry.get())
            q = parse_input_int(self.q_entry.get())
            e = parse_input_int(self.e_entry.get())
            
            self.log(f"🔧 开始生成密钥... p={p}, q={q}, e={e}")
            
            # 在后台线程中执行耗时操作
            threading.Thread(target=self._generate_keys, args=(p, q, e)).start()
            
        except Exception as e:
            self.log(f"🚨 错误: {str(e)}", self.pink)
            messagebox.showerror("输入错误", f"无效输入: {str(e)}")
    
    def _generate_keys(self, p, q, e):
        try:
            n, phi, d = gen_keys(p, q, e)
            
            self.result_text.configure(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"✅ 密钥生成完成：\n")
            self.result_text.insert(tk.END, f"🔐 n      = {n}\n")
            self.result_text.insert(tk.END, f"φ(n)     = {phi}\n")
            self.result_text.insert(tk.END, f"🔑 d      = {d}\n")
            self.result_text.configure(state=tk.DISABLED)
            
            self.log(f"✅ 密钥生成成功！n={n}, d={d}")
        except Exception as e:
            self.log(f"🚨 密钥生成失败: {str(e)}", self.pink)
    
    def encrypt_message(self):
        try:
            n = parse_input_int(self.enc_n_entry.get())
            e = parse_input_int(self.enc_e_entry.get())
            message = self.message_entry.get()
            
            if not message:
                raise ValueError("明文消息不能为空")
            
            self.log(f"🔐 开始加密消息: n={n}, e={e}, message='{message}'")
            
            # 在后台线程中执行耗时操作
            threading.Thread(target=self._encrypt_message, args=(n, e, message)).start()
            
        except Exception as e:
            self.log(f"🚨 错误: {str(e)}", self.pink)
            messagebox.showerror("输入错误", f"无效输入: {str(e)}")
    
    def _encrypt_message(self, n, e, message):
        try:
            # 这里简化处理，实际应用中需要根据n的大小处理消息
            c = encrypt(None, None, e, message, n=n)
            
            self.enc_result_text.configure(state=tk.NORMAL)
            self.enc_result_text.delete(1.0, tk.END)
            self.enc_result_text.insert(tk.END, f"✅ 加密完成：\n")
            self.enc_result_text.insert(tk.END, f"🔐 密文 c = {c}\n")
            self.enc_result_text.configure(state=tk.DISABLED)
            
            self.log(f"✅ 消息加密成功！c={c}")
        except Exception as e:
            self.log(f"🚨 加密失败: {str(e)}", self.pink)
    
    def decrypt_message(self):
        method = self.decrypt_method.get()
        self.log(f"🔓 开始解密，方法: {method}")
        
        try:
            # 根据方法收集必要的参数
            params = {}
            if method == "standard":
                params["p"] = parse_input_int(self.dec_entries["p"].get())
                params["q"] = parse_input_int(self.dec_entries["q"].get())
                params["e"] = parse_input_int(self.dec_entries["e"].get())
                params["c"] = parse_input_int(self.dec_entries["c"].get())
            elif method == "phi":
                params["n"] = parse_input_int(self.dec_entries["n"].get())
                params["e"] = parse_input_int(self.dec_entries["e"].get())
                params["phi"] = parse_input_int(self.dec_entries["phi"].get())
                params["c"] = parse_input_int(self.dec_entries["c"].get())
            elif method == "d":
                params["n"] = parse_input_int(self.dec_entries["n"].get())
                params["d"] = parse_input_int(self.dec_entries["d"].get())
                params["c"] = parse_input_int(self.dec_entries["c"].get())
            elif method == "factoring":
                params["n"] = parse_input_int(self.dec_entries["n"].get())
                params["e"] = parse_input_int(self.dec_entries["e"].get())
                params["c"] = parse_input_int(self.dec_entries["c"].get())
            
            # 在后台线程中执行解密
            threading.Thread(target=self._decrypt_message, args=(method, params)).start()
            
        except Exception as e:
            self.log(f"🚨 错误: {str(e)}", self.pink)
            messagebox.showerror("输入错误", f"无效输入: {str(e)}")
    
    def _decrypt_message(self, method, params):
        try:
            if method == "standard":
                m = decrypt_standard(params["p"], params["q"], params["e"], params["c"])
            elif method == "phi":
                m = decrypt_with_phi(params["n"], params["e"], params["phi"], params["c"])
            elif method == "d":
                m = decrypt_with_d(params["n"], params["d"], params["c"])
            elif method == "factoring":
                # 这里简化处理，实际应用中需要实现自动分解
                m = decrypt_with_factoring(params["n"], params["e"], params["c"])
            
            self.dec_result_text.configure(state=tk.NORMAL)
            self.dec_result_text.delete(1.0, tk.END)
            self.dec_result_text.insert(tk.END, f"✅ 解密完成：\n")
            self.dec_result_text.insert(tk.END, f"🔓 明文 m = {m}\n")
            self.dec_result_text.insert(tk.END, f"\n尝试解码为文本:\n")
            
            # 尝试解码为文本
            try:
                decoded = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode(errors='replace')
                self.dec_result_text.insert(tk.END, decoded)
            except:
                self.dec_result_text.insert(tk.END, "无法解码为文本，请检查是否为有效消息")
            
            self.dec_result_text.configure(state=tk.DISABLED)
            
            self.log(f"✅ 解密成功！m={m}")
        except Exception as e:
            self.log(f"🚨 解密失败: {str(e)}", self.pink)
    
    def perform_attack(self):
        method = self.attack_method.get()
        self.log(f"⚔️ 开始攻击，方法: {method}")
        
        try:
            params = {}
            if method == "common_modulus":
                params["n"] = parse_input_int(self.attack_entries["n1"].get())
                params["e1"] = parse_input_int(self.attack_entries["e1"].get())
                params["c1"] = parse_input_int(self.attack_entries["c1"].get())
                params["e2"] = parse_input_int(self.attack_entries["e2"].get())
                params["c2"] = parse_input_int(self.attack_entries["c2"].get())
            elif method == "common_e":
                params["n1"] = parse_input_int(self.attack_entries["n1"].get())
                params["c1"] = parse_input_int(self.attack_entries["c1"].get())
                params["n2"] = parse_input_int(self.attack_entries["n2"].get())
                params["c2"] = parse_input_int(self.attack_entries["c2"].get())
                params["e"] = parse_input_int(self.attack_entries["e1"].get())
            elif method == "high_bits":
                params["n"] = parse_input_int(self.attack_entries["n1"].get())
                params["e"] = parse_input_int(self.attack_entries["e1"].get())
                params["c"] = parse_input_int(self.attack_entries["c1"].get())
                params["p_high"] = parse_input_int(self.attack_entries["p_high"].get())
                params["bit_len"] = parse_input_int(self.attack_entries["bit_len"].get())
            elif method == "wiener":
                params["n"] = parse_input_int(self.attack_entries["n1"].get())
                params["e"] = parse_input_int(self.attack_entries["e1"].get())
            
            # 在后台线程中执行攻击
            threading.Thread(target=self._perform_attack, args=(method, params)).start()
            
        except Exception as e:
            self.log(f"🚨 错误: {str(e)}", self.pink)
            messagebox.showerror("输入错误", f"无效输入: {str(e)}")
    
    def _perform_attack(self, method, params):
        try:
            result = "攻击结果:\n"
            
            if method == "common_modulus":
                m = common_modulus_attack(
                    params["n"], params["e1"], params["e2"], params["c1"], params["c2"]
                )
                result += f"✅ 共模攻击成功！恢复的明文: {m}\n"
            elif method == "common_e":
                m = decrypt_common_modulus(
                    params["n1"], params["c1"], params["n2"], params["c2"], params["e"]
                )
                result += f"✅ 共模攻击（相同 e）成功！恢复的明文: {m}\n"
            elif method == "high_bits":
                p = recover_p_from_high_bits(
                    params["n"], params["e"], params["c"], params["p_high"], params["bit_len"]
                )
                result += f"✅ 高位泄露攻击成功！恢复的 p: {p}\n"
            elif method == "wiener":
                d = wiener_attack(params["e"], params["n"])
                if d:
                    result += f"✅ Wiener 攻击成功！恢复的私钥 d: {d}\n"
                else:
                    result += "❌ Wiener 攻击失败\n"
            
            self.attack_result_text.configure(state=tk.NORMAL)
            self.attack_result_text.delete(1.0, tk.END)
            self.attack_result_text.insert(tk.END, result)
            self.attack_result_text.configure(state=tk.DISABLED)
            
            self.log(f"✅ {method} 攻击成功！")
        except Exception as e:
            self.log(f"🚨 攻击失败: {str(e)}", self.pink)
    
    def decrypt_file(self):
        try:
            n = parse_input_int(self.file_n_entry.get())
            e = parse_input_int(self.file_e_entry.get())
            p_str = self.file_p_entry.get()
            q_str = self.file_q_entry.get()
            file_path = self.file_path_entry.get()
            
            if not file_path:
                raise ValueError("请选择文件")
            
            self.log(f"📂 开始解密文件: {file_path}")
            
            # 在后台线程中执行解密
            threading.Thread(target=self._decrypt_file, args=(n, e, p_str, q_str, file_path)).start()
            
        except Exception as e:
            self.log(f"🚨 错误: {str(e)}", self.pink)
            messagebox.showerror("输入错误", f"无效输入: {str(e)}")
    
    def _decrypt_file(self, n, e, p_str, q_str, file_path):
        try:
            # 尝试读取 p 和 q，如果为空则自动触发分解
            if p_str and q_str:
                p = parse_input_int(p_str)
                q = parse_input_int(q_str)
                self.log("✅ 已输入 p 和 q，将使用它们解密文件。")
            else:
                self.log("🔍 未提供 p 和 q，尝试自动分解 n ...")
                factors = factor_n(n)
                if not factors:
                    raise Exception("分解失败，无法解密")
                p, q = factors
                self.log(f"✅ 分解成功: p = {p}, q = {q}")
            
            # 计算私钥
            phi = (p - 1) * (q - 1)
            d = libnum.invmod(e, phi)
            
            # 构造私钥并解密
            private_key = RSA.construct((n, e, d, p, q))
            rsa = PKCS1_OAEP.new(private_key)
            
            with open(file_path, 'rb') as f:
                ciphertext = f.read()
            
            plaintext = rsa.decrypt(ciphertext)
            
            self.file_result_text.configure(state=tk.NORMAL)
            self.file_result_text.delete(1.0, tk.END)
            self.file_result_text.insert(tk.END, "✅ 解密成功，内容如下：\n\n")
            try:
                decoded = plaintext.decode()
                self.file_result_text.insert(tk.END, decoded)
            except:
                self.file_result_text.insert(tk.END, plaintext.hex())
                self.file_result_text.insert(tk.END, "\n\n(二进制数据，显示为十六进制)")
            self.file_result_text.configure(state=tk.DISABLED)
            
            self.log(f"✅ 文件解密成功！")
        except Exception as e:
            self.log(f"🚨 文件解密失败: {str(e)}", self.pink)

if __name__ == "__main__":
    root = tk.Tk()
    app = RSAToolGUI(root)
    root.mainloop()