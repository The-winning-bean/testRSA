### 目录结构

![image-20250529113745137](.\img\1.png)

```shell
RSA_tool/
├── __main__.py           # 运行程序入口
├── cli.py                # 命令行界面逻辑
├── core/
│   ├── keygen.py         # 密钥生成，加密
│   ├── decrypt.py        # 解密方式（已知 phi, d，素数假设等）
│   ├── attacks.py        # 各种攻击方式
│   ├── factoring.py      # Fermat、试除、自动分解逻辑
│   ├── utils.py          # 输入解析、输出格式化
│   └── wiener.py         # wiener_attack 攻击函数
└── external/
    ├── yafu.py           # 调用 YAFU 分解 n
    └── factordb.py       # 调用 FactorDB API 分解 n
```



