import os
import git
import json
from datetime import datetime
import time
import sys
from git_messenger import GitMessenger
from config import load_config, save_config

class GitChat:
    def __init__(self, github_url, local_path="./git_chat_repo", username=None, token=None):
        self.github_url = github_url
        self.local_path = local_path
        self.messenger = None
        self._setup_repo(username, token)
    
    def _setup_repo(self, username, token):
        try:
            self.messenger = GitMessenger(self.local_path, self.github_url, username, token)
            print("✅ 仓库连接成功！")
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
    print("=== GitHub 聊天工具 ===")
    print("提示：每个用户需要使用自己的 GitHub 账号和访问令牌")
    
    # 获取GitHub仓库地址
    github_url = input("请输入GitHub仓库地址 (https://github.com/用户名/仓库名.git): ").strip()
    if not github_url:
        print("❌ 仓库地址不能为空！")
        return
    
    # 尝试从配置文件加载用户信息
    config = load_config()
    github_username = config.get('github_username')
    github_token = config.get('github_token')
    display_name = config.get('display_name')
    
    # 如果配置文件中没有用户名，要求输入
    if not github_username:
        github_username = input("请输入你的GitHub用户名: ").strip()
        if not github_username:
            print("❌ GitHub用户名不能为空！")
            return
    
    # 如果配置文件中没有令牌，尝试从环境变量获取
    if not github_token:
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            print("\n请创建你的GitHub个人访问令牌(PAT):")
            print("1. 访问 https://github.com/settings/tokens")
            print("2. 点击 'Generate new token (classic)'")
            print("3. 设置权限：repo (对于私有仓库) 或 public_repo (对于公开仓库)")
            github_token = input("请输入你的GitHub个人访问令牌: ").strip()
            if not github_token:
                print("❌ GitHub令牌不能为空！")
                return
    
    # 如果配置文件中没有显示名称，要求输入
    if not display_name:
        display_name = input("请输入你的聊天显示名称: ").strip()
        if not display_name:
            print("❌ 显示名称不能为空！")
            return
    
    # 保存配置
    save_config({
        'github_username': github_username,
        'github_token': github_token,
        'display_name': display_name
    })
    
    # 初始化聊天，注意这里传入正确的参数顺序
    chat = GitChat(github_url, "./git_chat_repo", github_username, github_token)
    
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
            if chat.send_message(user_input, display_name):
                chat.display_messages()
                last_update = time.time()

if __name__ == "__main__":
    try:
        run_chat()
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}") 