import json
import os

# 将配置文件放在用户主目录下的 .gitchat 文件夹中
CONFIG_DIR = os.path.expanduser('~/.gitchat')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    # 确保配置目录存在
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_default_repo_path():
    """获取默认的仓库保存路径"""
    return os.path.expanduser('~/.gitchat/repos')

def setup_config():
    """初始化配置"""
    config = load_config()
    
    if not config:
        print("=== 首次运行配置 ===")
        
        # 获取GitHub用户信息
        github_username = input("请输入GitHub用户名: ").strip()
        github_token = input("请输入GitHub个人访问令牌(PAT): ").strip()
        display_name = input("请输入聊天显示名称: ").strip()
        
        # 获取仓库保存路径
        default_path = get_default_repo_path()
        print(f"\n请指定聊天仓库的保存路径")
        print(f"默认路径: {default_path}")
        repo_path = input(f"请输入保存路径 (直接回车使用默认路径): ").strip()
        
        if not repo_path:
            repo_path = default_path
        
        # 展开用户路径（如 ~/gitchat）
        repo_path = os.path.expanduser(repo_path)
        
        # 确保仓库目录存在
        os.makedirs(repo_path, exist_ok=True)
        
        # 创建配置
        config = {
            'github_username': github_username,
            'github_token': github_token,
            'display_name': display_name,
            'repo_path': repo_path
        }
        
        # 保存配置
        save_config(config)
        print(f"✅ 配置已保存")
    
    return config 