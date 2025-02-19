from nicegui import ui
import json
from pathlib import Path
from styles import *

# 确保messages.json文件存在
def init_messages_file():
    messages_file = Path('messages.json')
    if not messages_file.exists():
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)

# 保存消息到JSON文件
def save_message(message: str):
    messages_file = Path('messages.json')
    try:
        with open(messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        messages.append(message)
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages, ensure_ascii=False, indent=2, fp=f)
        return True
    except Exception as e:
        print(f"保存消息时出错: {e}")
        return False

# 读取所有消息
def load_messages():
    messages_file = Path('messages.json')
    try:
        with open(messages_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取消息时出错: {e}")
        return []

# 初始化消息文件
init_messages_file()

# 创建UI
messages_container = ui.column()

def refresh_messages():
    messages_container.clear()
    for message in load_messages():
        with messages_container:
            ui.label(message).classes(MESSAGE_STYLES)

def submit():
    if message_input.value.strip():
        if save_message(message_input.value):
            message_input.value = ''
            refresh_messages()
            ui.notify('消息已保存')
        else:
            ui.notify('保存失败', type='error')

with ui.card().classes(CARD_STYLES):
    with ui.row().classes(INPUT_ROW_STYLES):
        message_input = ui.input(placeholder='输入消息...').classes(INPUT_STYLES)
        ui.button('提交', on_click=submit).classes(BUTTON_STYLES)
    
    messages_container.classes(MESSAGES_CONTAINER_STYLES)
    refresh_messages()

ui.run() 