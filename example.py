from git_messenger import GitMessenger

# 用户 A - 发送消息
sender = GitMessenger('/path/to/repo')
sender.send_message("你好！这是一条测试消息", "用户A")

# 用户 B - 接收消息
receiver = GitMessenger('/path/to/repo')
messages = receiver.receive_messages()
for msg in messages:
    print(f"[{msg['timestamp']}] {msg['author']}: {msg['content']}") 