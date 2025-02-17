import json
import os
from src.crypto.crypto_utils import MessageCrypto
from cryptography.fernet import Fernet
import base64

# 将配置文件放在用户主目录下的 .gitchat 文件夹中
CONFIG_DIR = os.path.expanduser('~/.gitchat')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
KEY_FILE = os.path.join(CONFIG_DIR, '.key')

def get_config_key():
    """获取或创建配置加密密钥"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as f:
            return f.read().strip()
    else:
        # 使用随机生成的密钥而不是助记词
        key = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(KEY_FILE, 'w') as f:
            f.write(key)
        os.chmod(KEY_FILE, 0o600)
        return key

def load_config():
    """加载并解密配置"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        # 读取加密的配置文件
        with open(CONFIG_FILE, 'r') as f:
            encrypted_data = f.read().strip()
        
        if not encrypted_data:
            return {}
        
        # 使用配置密钥解密
        fernet = Fernet(get_config_key())
        decrypted_bytes = fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception as e:
        print(f"⚠️ 配置文件损坏或被篡改: {str(e)}")
        return {}

def save_config(config):
    """加密并保存配置"""
    try:
        # 确保配置目录存在
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # 加密配置数据
        fernet = Fernet(get_config_key())
        encrypted_data = fernet.encrypt(
            json.dumps(config, ensure_ascii=False).encode('utf-8')
        )
        
        # 保存加密的配置文件
        with open(CONFIG_FILE, 'w') as f:
            f.write(encrypted_data.decode('utf-8'))
        
        # 设置配置文件权限（仅当前用户可读写）
        os.chmod(CONFIG_FILE, 0o600)
        
    except Exception as e:
        print(f"❌ 保存配置失败: {str(e)}")
        raise

def get_default_repo_path():
    """获取默认的仓库保存路径"""
    return os.path.expanduser('~/.gitchat/repos')

def setup_config():
    """初始化配置"""
    config = load_config()
    
    if not config:
        config = {
            'platforms': {},      # 存储多个平台的配置
            'display_name': '',   # 聊天显示名称
            'repo_path': '',      # 仓库保存路径
            'repos': {}          # 存储每个平台的所有仓库
        }
    
    print("=== Git平台配置 ===")
    print("1. 添加/修改平台配置")
    print("2. 设置基本信息")
    print("0. 完成配置")
    
    while True:
        choice = input("\n请选择操作 (0-2): ").strip()
        
        if choice == '0':
            if not config['platforms']:
                print("❌ 至少需要配置一个Git平台！")
                continue
            if not config['display_name']:
                print("❌ 需要设置显示名称！")
                continue
            break
            
        elif choice == '1':
            # 添加/修改平台配置
            print("\n支持的平台：")
            print("1. GitHub")
            print("2. Gitee")
            platform_choice = input("请选择平台 (1/2): ").strip()
            
            if platform_choice == '1':
                platform_name = 'GitHub'
                api_url = 'https://api.github.com'
                token_url = 'https://github.com/settings/tokens'
            elif platform_choice == '2':
                platform_name = 'Gitee'
                api_url = 'https://gitee.com/api/v5'
                token_url = 'https://gitee.com/profile/personal_access_tokens'
            else:
                print("❌ 无效的选择！")
                continue
            
            username = input(f"请输入{platform_name}用户名: ").strip()
            print(f"\n获取{platform_name}令牌:")
            print(f"1. 访问 {token_url}")
            print("2. 生成新的访问令牌")
            print("3. 设置必要的权限（repo/projects）")
            token = input("请输入访问令牌: ").strip()
            
            if username and token:
                config['platforms'][platform_name] = {
                    'username': username,
                    'token': token,
                    'api_url': api_url
                }
                save_config(config)  # 立即保存配置
                print(f"✅ {platform_name}配置已保存")
            
        elif choice == '2':
            # 设置基本信息
            display_name = input("请输入聊天显示名称: ").strip()
            if display_name:
                config['display_name'] = display_name
            
            default_path = get_default_repo_path()
            print(f"\n请指定聊天仓库的保存路径")
            print(f"默认路径: {default_path}")
            repo_path = input(f"请输入保存路径 (直接回车使用默认路径): ").strip()
            repo_path = repo_path if repo_path else default_path
            repo_path = os.path.expanduser(repo_path)
            os.makedirs(repo_path, exist_ok=True)
            config['repo_path'] = repo_path
            
            save_config(config)  # 立即保存配置
        
        else:
            print("❌ 无效的选择！")
            continue
    
    return config

def update_config():
    """修改现有配置"""
    config = load_config()
    if not config:
        print("❌ 没有找到现有配置，请先运行程序完成初始配置")
        return None
    
    while True:
        print("\n=== 修改配置 ===")
        print("1. 管理Git平台")
        print("2. 修改显示名称")
        print("3. 修改仓库路径")
        print("0. 完成修改")
        
        choice = input("\n请选择要修改的项目 (0-3): ").strip()
        
        if choice == '0':
            break
            
        elif choice == '1':
            while True:
                print("\n当前配置的平台：")
                for i, (name, info) in enumerate(config['platforms'].items(), 1):
                    print(f"{i}. {name} ({info['username']})")
                print("A. 添加新平台")
                print("D. 删除平台")
                print("M. 修改平台配置")
                print("0. 返回")
                
                platform_choice = input("请选择操作: ").strip().upper()
                
                if platform_choice == '0':
                    break
                elif platform_choice == 'A':
                    print("\n支持的平台：")
                    print("1. GitHub")
                    print("2. Gitee")
                    new_platform = input("请选择要添加的平台 (1/2): ").strip()
                    
                    if new_platform == '1':
                        platform_name = 'GitHub'
                        api_url = 'https://api.github.com'
                        token_url = 'https://github.com/settings/tokens'
                    elif new_platform == '2':
                        platform_name = 'Gitee'
                        api_url = 'https://gitee.com/api/v5'
                        token_url = 'https://gitee.com/profile/personal_access_tokens'
                    else:
                        print("❌ 无效的选择！")
                        continue
                    
                    # 检查平台是否已存在
                    if platform_name in config['platforms']:
                        print(f"❌ {platform_name}平台已配置！如需修改请使用'M'选项")
                        continue
                    
                    username = input(f"请输入{platform_name}用户名: ").strip()
                    print(f"\n获取{platform_name}令牌:")
                    print(f"1. 访问 {token_url}")
                    print("2. 生成新的访问令牌")
                    print("3. 设置必要的权限（repo/projects）")
                    token = input("请输入访问令牌: ").strip()
                    
                    if username and token:
                        config['platforms'][platform_name] = {
                            'username': username,
                            'token': token,
                            'api_url': api_url
                        }
                        save_config(config)
                        print(f"✅ {platform_name}平台配置已保存")
                    
                elif platform_choice == 'D':
                    platform_name = input("请输入要删除的平台名称: ").strip()
                    if platform_name in config['platforms']:
                        confirm = input(f"确定要删除{platform_name}平台配置吗？(y/n): ").strip().lower()
                        if confirm == 'y':
                            del config['platforms'][platform_name]
                            save_config(config)
                            print(f"✅ {platform_name}配置已删除")
                    else:
                        print("❌ 未找到指定的平台！")
                
                elif platform_choice == 'M':
                    platform_name = input("请输入要修改的平台名称: ").strip()
                    if platform_name in config['platforms']:
                        username = input(f"请输入新的{platform_name}用户名 (直接回车保持不变): ").strip()
                        token = input(f"请输入新的{platform_name}令牌 (直接回车保持不变): ").strip()
                        if username:
                            config['platforms'][platform_name]['username'] = username
                        if token:
                            config['platforms'][platform_name]['token'] = token
                        save_config(config)
                        print(f"✅ {platform_name}配置已更新")
                    else:
                        print("❌ 未找到指定的平台！")
                
                else:
                    print("❌ 无效的操作！")
        
        elif choice == '2':
            name = input("请输入新的显示名称: ").strip()
            if name:
                config['display_name'] = name
                
        elif choice == '3':
            path = input("请输入新的仓库保存路径: ").strip()
            if path:
                path = os.path.expanduser(path)
                os.makedirs(path, exist_ok=True)
                config['repo_path'] = path
                
        else:
            print("❌ 无效的选择！")
            continue
        
        save_config(config)
        print("✅ 配置已更新")
    
    return config

def save_recent_repo(platform_name, repo_url, chat_mnemonic=None):
    """保存仓库地址和助记词"""
    config = load_config()
    if 'repos' not in config:
        config['repos'] = {}
    
    if platform_name not in config['repos']:
        config['repos'][platform_name] = {}
    
    # 保存仓库信息
    if repo_url not in config['repos'][platform_name]:
        note = input("\n为仓库添加备注（直接回车跳过）: ").strip()
        config['repos'][platform_name][repo_url] = {
            'note': note,
            'mnemonic': chat_mnemonic
        }
        save_config(config)

def update_repo_note(platform_name, repo_url, config):
    """更新仓库备注"""
    if platform_name in config['repos'] and repo_url in config['repos'][platform_name]:
        current_note = config['repos'][platform_name][repo_url]
        print(f"\n当前备注: {current_note if current_note else '(无)'}")
        new_note = input("请输入新的备注（直接回车保持不变）: ").strip()
        if new_note:
            config['repos'][platform_name][repo_url] = new_note
            save_config(config)
            print("✅ 备注已更新")

def get_repo_url(platform_name, config):
    """获取仓库地址和助记词"""
    repos = config.get('repos', {}).get(platform_name, {})
    
    if repos:
        print("\n已保存的仓库：")
        for i, (url, info) in enumerate(repos.items(), 1):
            note_text = f"【{info.get('note')}】" if info.get('note') else ""
            print(f"{i}. {note_text}{url}")
        print("0. 添加新仓库")
        
        choice = input("\n请选择 (输入序号): ").strip()
        if choice == '0':
            pass  # 继续执行下面的新仓库输入
        else:
            try:
                idx = int(choice) - 1
                urls = list(repos.keys())
                if 0 <= idx < len(urls):
                    url = urls[idx]
                    return url, repos[url].get('mnemonic')
            except ValueError:
                pass
    
    print(f"\n请输入仓库地址，格式如下：")
    print(f"{platform_name}: https://{platform_name.lower()}.com/用户名/仓库名.git")
    return input("请输入仓库地址: ").strip(), None 