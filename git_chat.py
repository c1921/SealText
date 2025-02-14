import os
import git
import json
from datetime import datetime
import time
import sys
from git_messenger import GitMessenger
from config import (
    load_config, 
    save_config, 
    setup_config, 
    update_config, 
    save_recent_repo,
    get_repo_url
)

class GitChat:
    def __init__(self, repo_url, platform_name, username=None, token=None):
        self.repo_url = repo_url
        self.platform_name = platform_name
        config = load_config()
        self.local_path = config.get('repo_path', os.path.expanduser('~/.gitchat/repos'))
        self.messenger = None
        self._setup_repo(username, token)
    
    def _setup_repo(self, username, token):
        try:
            repo_name = self.repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.local_path, f"{self.platform_name.lower()}_{repo_name}")
            
            config = load_config()
            if not config.get('mnemonic'):
                print("❌ 未找到助记词配置！")
                sys.exit(1)
            
            self.messenger = GitMessenger(repo_path, self.repo_url, username, token, config['mnemonic'])
            print("✅ 仓库连接成功！")
            print(f"📂 本地仓库路径: {repo_path}")
        except Exception as e:
            print(f"❌ 仓库连接失败: {str(e)}")
            sys.exit(1)
    
    def send_message(self, message, author):
        try:
            self.messenger.send_message(message, author)
            print("✅ 消息发送成功！")
            return True
        except Exception as e:
            print(f"❌ 消息发送失败: {str(e)}")
            return False
    
    def get_messages(self):
        try:
            return self.messenger.receive_messages()
        except Exception as e:
            print(f"❌ 获取消息失败: {str(e)}")
            return []
    
    def display_messages(self):
        messages = self.get_messages()
        if not messages:
            print("\n暂无消息记录")
            return
        
        print("\n=== 消息记录 ===")
        for msg in messages:
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {msg['author']}: {msg['content']}")
        print("==============")

def run_chat():
    print("=== Git 聊天工具 ===")
    
    # 检查是否需要修改配置
    if os.path.exists(os.path.join(os.path.expanduser('~/.gitchat'), 'config.json')):
        if input("是否需要修改现有配置？(y/n): ").lower() == 'y':
            config = update_config()
            if not config:
                return
        else:
            config = load_config()
    else:
        print("首次运行，需要进行配置")
        config = setup_config()
        if not config:
            return
    
    print("\n=== 选择Git平台 ===")
    if not config['platforms']:
        print("❌ 没有配置任何Git平台！")
        return
    
    # 显示已配置的平台
    platforms = list(config['platforms'].items())
    for i, (name, info) in enumerate(platforms, 1):
        print(f"{i}. {name} ({info['username']})")
    
    while True:
        choice = input("\n请选择平台 (输入序号): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(platforms):
                platform_name, platform_info = platforms[idx]
                break
            else:
                print("❌ 无效的选择！")
        except ValueError:
            print("❌ 请输入数字！")
    
    print(f"\n已选择平台: {platform_name}")
    print(f"用户名: {platform_info['username']}")
    
    # 使用 get_repo_url 函数获取仓库地址
    repo_url = get_repo_url(platform_name, config)
    if not repo_url:
        print("❌ 已取消操作")
        return
    
    # 验证仓库地址格式
    platform_domain = f"{platform_name.lower()}.com"
    if platform_domain not in repo_url:
        print(f"❌ 仓库地址与选择的平台({platform_name})不匹配！")
        return
    
    # 保存仓库地址到最近使用列表
    save_recent_repo(platform_name, repo_url)
    
    # 初始化聊天
    chat = GitChat(
        repo_url,
        platform_name,
        platform_info['username'],
        platform_info['token']
    )
    
    print("\n🎉 欢迎使用Git聊天工具！")
    print("- 输入消息后按回车发送")
    print("- 输入 'q' 退出")
    print("- 输入 'r' 刷新消息")
    
    last_update = time.time()
    
    while True:
        # 每30秒自动刷新一次消息
        if time.time() - last_update > 30:
            chat.display_messages()
            last_update = time.time()
        
        user_input = input("\n请输入消息: ").strip()
        
        if user_input.lower() == 'q':
            print("👋 再见！")
            break
        elif user_input.lower() == 'r':
            chat.display_messages()
            last_update = time.time()
        elif user_input:
            if chat.send_message(user_input, config['display_name']):
                chat.display_messages()
                last_update = time.time()

if __name__ == "__main__":
    try:
        run_chat()
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}") 