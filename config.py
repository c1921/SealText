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
        config = {
            'platforms': {},      # 存储多个平台的配置
            'display_name': '',   # 聊天显示名称
            'repo_path': '',      # 仓库保存路径
            'chat_password': '',  # 加密密码
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
            if not config['chat_password']:
                print("❌ 需要设置加密密码！")
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
            
            chat_password = input("请设置聊天加密密码: ").strip()
            if chat_password:
                config['chat_password'] = chat_password
        
        else:
            print("❌ 无效的选择！")
            continue
        
        # 保存配置
        save_config(config)
    
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
        print("4. 修改加密密码")
        print("0. 完成修改")
        
        choice = input("\n请选择要修改的项目 (0-4): ").strip()
        
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
                    # 添加新平台（使用与setup_config相同的逻辑）
                    print("\n支持的平台：")
                    print("1. GitHub")
                    print("2. Gitee")
                    # ... 添加平台的代码 ...
                elif platform_choice == 'D':
                    platform_name = input("请输入要删除的平台名称: ").strip()
                    if platform_name in config['platforms']:
                        del config['platforms'][platform_name]
                        print(f"✅ {platform_name}配置已删除")
                elif platform_choice == 'M':
                    platform_name = input("请输入要修改的平台名称: ").strip()
                    if platform_name in config['platforms']:
                        username = input(f"请输入新的{platform_name}用户名 (直接回车保持不变): ").strip()
                        token = input(f"请输入新的{platform_name}令牌 (直接回车保持不变): ").strip()
                        if username:
                            config['platforms'][platform_name]['username'] = username
                        if token:
                            config['platforms'][platform_name]['token'] = token
                        print(f"✅ {platform_name}配置已更新")
        
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
                
        elif choice == '4':
            password = input("请输入新的聊天加密密码: ").strip()
            if password:
                config['chat_password'] = password
        
        # 保存更新后的配置
        save_config(config)
        print("✅ 配置已更新")
    
    return config 

def save_recent_repo(platform_name, repo_url):
    """保存仓库地址"""
    config = load_config()
    if 'repos' not in config:
        config['repos'] = {}
    
    if platform_name not in config['repos']:
        config['repos'][platform_name] = {}  # 改用字典存储，key为仓库地址，value为备注
    
    # 如果是新仓库，添加到字典中并请求备注
    if repo_url not in config['repos'][platform_name]:
        note = input("\n为仓库添加备注（直接回车跳过）: ").strip()
        config['repos'][platform_name][repo_url] = note
    
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
    """获取仓库地址，支持选择已有仓库"""
    repos = config.get('repos', {}).get(platform_name, {})
    
    if repos:
        while True:
            print("\n已保存的仓库：")
            # 将字典转换为列表，便于分页显示
            repo_list = [(url, note) for url, note in repos.items()]
            repo_list.sort()  # 按仓库地址排序
            
            # 分页显示仓库列表
            page_size = 10
            total_pages = (len(repo_list) + page_size - 1) // page_size
            page = 1
            
            while True:
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, len(repo_list))
                
                print(f"\n=== 第 {page}/{total_pages} 页 ===")
                for i, (url, note) in enumerate(repo_list[start_idx:end_idx], start_idx + 1):
                    note_text = f"【{note}】" if note else ""
                    print(f"{i}. {note_text}{url}")
                
                print("\n操作：")
                if total_pages > 1:
                    if page > 1:
                        print("p. 上一页")
                    if page < total_pages:
                        print("n. 下一页")
                print("a. 添加新仓库")
                print("m. 修改备注")
                print("q. 返回主菜单")
                
                choice = input("\n请选择 (输入序号或操作): ").strip().lower()
                
                if choice == 'q':
                    return None
                elif choice == 'a':
                    break
                elif choice == 'p' and page > 1:
                    page -= 1
                    continue
                elif choice == 'n' and page < total_pages:
                    page += 1
                    continue
                elif choice == 'm':
                    repo_idx = input("请输入要修改备注的仓库序号: ").strip()
                    try:
                        idx = int(repo_idx) - 1
                        if 0 <= idx < len(repo_list):
                            url, _ = repo_list[idx]
                            update_repo_note(platform_name, url, config)
                            continue
                        else:
                            print("❌ 无效的序号！")
                    except ValueError:
                        print("❌ 请输入数字！")
                    continue
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(repo_list):
                        return repo_list[idx][0]  # 返回仓库地址
                    else:
                        print("❌ 无效的选择！")
                except ValueError:
                    print("❌ 请输入有效的选项！")
            
            if choice == 'a':
                break
    
    # 输入新的仓库地址
    print("\n请输入仓库地址，格式如下：")
    print(f"{platform_name}: https://{platform_name.lower()}.com/用户名/仓库名.git")
    return input("请输入仓库地址: ").strip() 