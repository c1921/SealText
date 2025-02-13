from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QComboBox, QLabel, QMessageBox, QScrollArea,
    QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor, QKeyEvent
import sys
from datetime import datetime
from config import load_config, get_repo_url
from git_chat import GitChat

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SealText")
        self.setMinimumSize(800, 600)
        
        # 加载配置
        self.config = load_config()
        if not self.config:
            QMessageBox.critical(self, "错误", "请先运行命令行工具完成初始配置！")
            sys.exit(1)
        
        # 初始化UI
        self.setup_ui()
        
        # 初始化聊天相关变量
        self.chat = None
        self.last_update = datetime.now()
        
        # 设置定时器，每30秒刷新一次消息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_messages)
        self.timer.start(30000)  # 30秒
        
        # 在UI初始化完成后，手动触发平台切换事件
        if self.platform_combo.count() > 0:
            self.on_platform_changed(self.platform_combo.currentText())
            # 确保选中第一个仓库
            if self.repo_combo.count() > 0:
                self.repo_combo.setCurrentIndex(0)
                # 手动连接第一个仓库
                url = self.repo_combo.itemData(0)
                if url:
                    self.connect_to_repo(url)
    
    def setup_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        
        # 平台选择区域
        platform_layout = QHBoxLayout()
        platform_label = QLabel("选择平台:")
        self.platform_combo = QComboBox()
        for platform_name in self.config['platforms'].keys():
            self.platform_combo.addItem(platform_name)
        self.platform_combo.currentTextChanged.connect(self.on_platform_changed)
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_combo)
        platform_layout.addStretch()
        layout.addLayout(platform_layout)
        
        # 仓库选择区域
        repo_layout = QHBoxLayout()
        repo_label = QLabel("选择仓库:")
        self.repo_combo = QComboBox()
        self.repo_combo.setMinimumWidth(400)
        self.repo_combo.currentIndexChanged.connect(self.on_repo_changed)
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_messages)
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_combo)
        repo_layout.addWidget(self.refresh_button)
        layout.addLayout(repo_layout)
        
        # 使用分割器来分隔消息区域和输入区域
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # 消息显示区域
        self.message_area = QTextEdit()
        self.message_area.setReadOnly(True)
        self.message_area.setFont(QFont("微软雅黑", 10))
        self.message_area.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                padding: 10px;
            }
        """)
        splitter.addWidget(self.message_area)
        
        # 输入区域容器
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        # 多行文本输入框
        self.input_edit = QTextEdit()
        self.input_edit.setFont(QFont("微软雅黑", 10))
        self.input_edit.setPlaceholderText("输入消息... (Ctrl+Enter 发送)")
        self.input_edit.setMinimumHeight(60)
        self.input_edit.setMaximumHeight(120)
        input_layout.addWidget(self.input_edit)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)
        input_layout.addLayout(button_layout)
        
        splitter.addWidget(input_container)
        
        # 设置分割器的初始比例
        splitter.setStretchFactor(0, 4)  # 消息区域
        splitter.setStretchFactor(1, 1)  # 输入区域
        
        # 初始禁用输入区域
        self.input_edit.setEnabled(False)
        self.send_button.setEnabled(False)
    
    def on_platform_changed(self, platform_name):
        """平台切换时更新仓库列表"""
        self.repo_combo.clear()
        if not platform_name:
            return
        
        repos = self.config.get('repos', {}).get(platform_name, {})
        for url, note in repos.items():
            display_text = f"【{note}】{url}" if note else url
            self.repo_combo.addItem(display_text, url)  # 使用userData存储实际的URL
        
        # 添加"添加新仓库"选项
        self.repo_combo.addItem("+ 添加新仓库...", None)
        
        # 如果有仓库，自动连接第一个
        if repos:
            # 不需要手动调用connect_to_repo，因为会触发on_repo_changed
            self.repo_combo.setCurrentIndex(0)
    
    def on_repo_changed(self, index):
        """仓库切换时的处理"""
        if index < 0:
            return
        
        # 获取选中项的实际URL
        url = self.repo_combo.itemData(index)
        if not url:  # 如果是"添加新仓库"选项
            # TODO: 处理添加新仓库
            return
        
        self.connect_to_repo(url)
    
    def connect_to_repo(self, repo_url):
        """连接到指定仓库"""
        try:
            platform_name = self.platform_combo.currentText()
            platform_info = self.config['platforms'][platform_name]
            
            self.chat = GitChat(
                repo_url,
                platform_name,
                platform_info['username'],
                platform_info['token'],
                self.config['chat_password']
            )
            
            self.refresh_messages()
            self.input_edit.setEnabled(True)
            self.send_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接仓库失败：{str(e)}")
    
    def refresh_messages(self):
        """刷新消息"""
        if not self.chat:
            return
        
        try:
            messages = self.chat.get_messages()
            if not messages:
                self.message_area.setHtml("<p style='color: #999; text-align: center;'>暂无消息</p>")
                return
            
            html_content = []
            for msg in messages:
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                # 移除消息内容首尾的空白字符
                content = msg['content'].strip()
                
                message_html = f"""
                    <div style='margin-bottom: 15px;'>
                        <div style='color: #888;'>
                            [{timestamp}] <span style='color: #333; font-weight: bold;'>{msg['author']}</span>
                        </div>
                        <div style='white-space: pre-wrap; color: #000; margin-top: 3px;'>{content}</div>
                    </div>
                """
                html_content.append(message_html)
            
            # 设置完整的HTML内容
            full_html = f"""
                <div style='font-family: "微软雅黑", sans-serif;'>
                    {"".join(html_content)}
                </div>
            """
            
            self.message_area.setHtml(full_html)
            
            # 滚动到底部
            cursor = self.message_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.message_area.setTextCursor(cursor)
            self.message_area.ensureCursorVisible()
        except Exception as e:
            QMessageBox.warning(self, "警告", f"刷新消息失败：{str(e)}")
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理按键事件"""
        # 如果是在输入框中按下Ctrl+Enter
        if (event.key() == Qt.Key_Return and 
            event.modifiers() == Qt.ControlModifier and 
            self.input_edit.hasFocus()):
            self.send_message()
        else:
            super().keyPressEvent(event)
    
    def send_message(self):
        """发送消息"""
        if not self.chat:
            QMessageBox.warning(self, "警告", "请先选择聊天仓库！")
            return
        
        # 获取文本并去除首尾空白
        message = self.input_edit.toPlainText().strip()
        if not message:
            return
        
        try:
            self.input_edit.setEnabled(False)
            self.send_button.setEnabled(False)
            
            if self.chat.send_message(message, self.config['display_name']):
                self.input_edit.clear()
                self.refresh_messages()
            
            self.input_edit.setEnabled(True)
            self.send_button.setEnabled(True)
            self.input_edit.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发送消息失败：{str(e)}")
            self.input_edit.setEnabled(True)
            self.send_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 