# SealText

基于 Git 的加密通讯工具。

## 安装

1. 克隆仓库

    ```bash
    git clone https://github.com/c1921/SealText.git
    cd SealText
    ```

2. 创建并激活虚拟环境

    ```bash
    # 创建虚拟环境
    python -m venv .venv
    # 激活
    # Windows
    .venv/Scripts/activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3. 安装依赖

    ```bash
    pip install -r requirements.txt
    ```

## 使用

```bash
python main.py
```

首次运行会要求进行配置：

1. 配置 Git 平台
2. 设置显示名称
3. 生成并保存助记词

## 注意事项

- 请妥善保管助记词，它用于消息加密，丢失将无法恢复消息
- 配置文件存储在 `~/.gitchat/` 目录下
- 本地仓库默认存储在 `~/.gitchat/repos/` 目录下
