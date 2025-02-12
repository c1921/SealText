from git_messenger import GitMessenger

# GitHub 仓库地址（使用HTTPS或SSH地址）
GITHUB_REPO = "https://github.com/你的用户名/仓库名.git"

def setup_sender():
    """用户A：首次设置和发送消息"""
    sender = GitMessenger('./sender_repo', GITHUB_REPO)
    sender.send_message("你好！这是一条测试消息", "用户A")
    print("消息已发送")

def setup_receiver():
    """用户B：克隆仓库并接收消息"""
    receiver = GitMessenger('./receiver_repo', GITHUB_REPO)
    messages = receiver.receive_messages()
    for msg in messages:
        print(f"[{msg['timestamp']}] {msg['author']}: {msg['content']}")

if __name__ == "__main__":
    # 根据角色选择运行不同的函数
    role = input("请选择角色 (sender/receiver): ").lower()
    if role == 'sender':
        setup_sender()
    elif role == 'receiver':
        setup_receiver() 