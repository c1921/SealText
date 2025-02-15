import os
import git
import json
from datetime import datetime
import logging
import time
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from config import load_config
from crypto_utils import MessageCrypto
import hashlib
import sys

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GitMessenger:
    def __init__(self, repo_path, remote_url=None, username=None, token=None, chat_mnemonic=None):
        self.repo_path = repo_path
        self.remote_url = remote_url
        self.username = username
        self.token = token
        # 只使用聊天助记词
        self.crypto = MessageCrypto(chat_mnemonic) if chat_mnemonic else None
        
        # 配置 git 的全局设置
        self._configure_git()
        
        logger.debug(f"初始化 GitMessenger: repo_path={repo_path}, remote_url={remote_url}, username={username}")
        
        # 如果提供了用户名和令牌，修改远程URL以包含认证信息
        if remote_url and username and token:
            if remote_url.startswith('https://'):
                self.remote_url = remote_url.replace('https://', f'https://{username}:{token}@')
                logger.debug(f"设置认证URL: {self.remote_url.replace(token, '****')}")
        
        self.repo = self._init_repo()
    
    def _configure_git(self):
        """配置git全局设置"""
        try:
            # 设置较长的超时时间
            os.environ['GIT_HTTP_CONNECT_TIMEOUT'] = '60'
            os.environ['GIT_HTTP_LOW_SPEED_LIMIT'] = '1000'
            os.environ['GIT_HTTP_LOW_SPEED_TIME'] = '60'
            
            # 禁用 SSL 验证（如果需要的话）
            # os.environ['GIT_SSL_NO_VERIFY'] = '1'
            
            # 设置 HTTP 代理（如果需要的话）
            # os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
            # os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'
        except Exception as e:
            logger.warning(f"配置git设置时出错: {str(e)}")
    
    def _check_git_connection(self):
        """检查与Git服务器的连接"""
        try:
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=0.5)
            session.mount('https://', HTTPAdapter(max_retries=retries))
            
            # 根据URL判断是GitHub还是Gitee
            if 'github.com' in self.remote_url:
                test_url = 'https://api.github.com'
                response = session.get(test_url, timeout=10)
            elif 'gitee.com' in self.remote_url:
                # Gitee API需要带上token才能访问
                config = load_config()
                if 'platforms' in config and 'Gitee' in config['platforms']:
                    token = config['platforms']['Gitee']['token']
                    test_url = 'https://gitee.com/api/v5/user'
                    headers = {'Authorization': f'token {token}'}
                    response = session.get(test_url, headers=headers, timeout=10)
                else:
                    # 如果没有配置Gitee，直接检查gitee.com是否可访问
                    test_url = 'https://gitee.com'
                    response = session.get(test_url, timeout=10)
            else:
                raise ValueError("不支持的Git服务商，目前仅支持GitHub和Gitee")
            
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Git服务器连接测试失败: {str(e)}")
            return False
    
    def _git_operation_with_retry(self, operation, max_retries=3):
        """带重试机制的git操作"""
        for attempt in range(max_retries):
            try:
                return operation()
            except git.exc.GitCommandError as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Git操作失败，尝试重试 ({attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)  # 指数退避
    
    def _get_message_file(self, username):
        """获取用户特定的消息文件路径"""
        # 使用用户名创建文件名，避免特殊字符
        safe_username = "".join(c for c in username if c.isalnum() or c in '-_')
        return os.path.join(self.repo_path, f'messages_{safe_username}.json')
    
    def _init_repo(self):
        try:
            # 首先检查Git服务器连接
            if not self._check_git_connection():
                raise Exception("无法连接到Git服务器，请检查网络连接")
            
            if not os.path.exists(self.repo_path):
                logger.debug(f"创建新仓库: {self.repo_path}")
                os.makedirs(self.repo_path)
                repo = git.Repo.init(self.repo_path)
                
                # 配置用户信息
                if self.username:
                    repo.config_writer().set_value("user", "name", self.username).release()
                    repo.config_writer().set_value("user", "email", f"{self.username}@users.noreply.github.com").release()
                
                # 设置默认分支为 main
                logger.debug("创建并切换到 main 分支")
                repo.git.checkout('-b', 'main')
                
                if self.remote_url:
                    logger.debug("添加远程仓库")
                    origin = repo.create_remote('origin', self.remote_url)
                    
                    try:
                        # 尝试拉取远程仓库
                        logger.debug("尝试拉取远程仓库")
                        origin.fetch()
                        origin.pull('main')
                    except git.exc.GitCommandError:
                        # 如果拉取失败（可能是新仓库），创建初始提交
                        logger.debug("创建初始提交")
                        message_file = self._get_message_file(self.username)
                        open(message_file, 'w', encoding='utf-8').write('[]')
                        repo.index.add([os.path.basename(message_file)])
                        repo.index.commit('Initial commit')
                        
                    # 设置上游分支并推送
                    logger.debug("推送到远程仓库")
                    try:
                        repo.git.push('--set-upstream', 'origin', 'main')
                    except git.exc.GitCommandError as e:
                        if "fetch first" in str(e):
                            # 如果推送被拒绝，先拉取再推送
                            logger.debug("推送被拒绝，尝试先拉取")
                            origin.pull('main')
                            repo.git.push('--set-upstream', 'origin', 'main')
                        else:
                            raise
            else:
                logger.debug(f"打开已存在的仓库: {self.repo_path}")
                repo = git.Repo(self.repo_path)
                
                # 配置用户信息
                if self.username:
                    repo.config_writer().set_value("user", "name", self.username).release()
                    repo.config_writer().set_value("user", "email", f"{self.username}@users.noreply.github.com").release()
                
                # 确保远程仓库配置正确
                if self.remote_url:
                    if 'origin' in repo.remotes:
                        origin = repo.remote('origin')
                        if origin.url != self.remote_url:
                            logger.debug("更新远程仓库URL")
                            origin.set_url(self.remote_url)
                    else:
                        logger.debug("添加远程仓库")
                        origin = repo.create_remote('origin', self.remote_url)
                
                # 确保在 main 分支上
                if 'main' not in repo.heads:
                    logger.debug("创建 main 分支")
                    repo.create_head('main', origin.refs.main)
                
                if repo.active_branch.name != 'main':
                    logger.debug("切换到 main 分支")
                    repo.heads.main.checkout()
                
                # 同步远程更改
                logger.debug("同步远程更改")
                origin.pull('main')
            
            return repo
            
        except Exception as e:
            logger.error(f"初始化仓库失败: {str(e)}")
            raise
    
    def send_message(self, message, author):
        try:
            logger.debug("开始发送消息")
            # 先拉取最新更改
            origin = self.repo.remotes.origin
            logger.debug("拉取最新更改")
            origin.pull()
            
            message_file = self._get_message_file(self.username)
            logger.debug(f"读取消息文件: {message_file}")
            
            # 读取或创建消息文件
            if os.path.exists(message_file):
                with open(message_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # 获取前一条消息的哈希值
            prev_hash = None
            if messages:
                try:
                    decrypted_msg = self.crypto.decrypt_message(messages[-1])
                    prev_hash = decrypted_msg.get('hash')
                except Exception as e:
                    logger.error(f"获取前一条消息哈希失败: {str(e)}")
            
            # 创建消息字典
            message_dict = {
                'content': message.strip(),
                'author': author,
                'timestamp': datetime.now().isoformat()
            }
            
            # 加密消息并添加到消息列表
            encrypted_message = self.crypto.encrypt_message(message_dict, prev_hash)
            messages.append(encrypted_message)
            
            # 保存消息
            logger.debug("保存消息")
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # 提交更改
            logger.debug("提交更改")
            self.repo.index.add([os.path.basename(message_file)])
            self.repo.index.commit(f"Message from {author}")
            
            # 推送到远程仓库
            logger.debug("推送到远程仓库")
            origin.push()
            
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            raise
    
    def receive_messages(self):
        # 拉取最新更改
        origin = self.repo.remotes.origin
        origin.pull()
        
        # 获取所有消息文件
        message_files = [f for f in os.listdir(self.repo_path) 
                        if f.startswith('messages_') and f.endswith('.json')]
        
        all_messages = []
        prev_hash = None
        
        for file_name in message_files:
            message_file = os.path.join(self.repo_path, file_name)
            try:
                with open(message_file, 'r', encoding='utf-8') as f:
                    raw_messages = json.load(f)
                    
                    for encrypted_msg in raw_messages:
                        try:
                            decrypted_msg = self.crypto.decrypt_message(encrypted_msg)
                            
                            # 验证哈希链
                            if prev_hash and decrypted_msg.get('prev_hash') != prev_hash:
                                logger.error("哈希链断裂，消息可能被篡改")
                                decrypted_msg['content'] = '【警告：消息完整性验证失败】'
                            
                            prev_hash = decrypted_msg.get('hash')
                            all_messages.append(decrypted_msg)
                            
                        except ValueError as e:
                            logger.error(f"解密消息失败: {str(e)}")
                            all_messages.append({
                                'content': '【无法解密或验证的消息】',
                                'author': '未知',
                                'timestamp': '未知'
                            })
                            
            except Exception as e:
                logger.error(f"读取消息文件 {file_name} 失败: {str(e)}")
        
        # 按时间戳排序所有消息
        all_messages.sort(key=lambda x: x['timestamp'])
        return all_messages

def _setup_repo(self, username, token, chat_mnemonic):
    try:
        repo_name = self.repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(self.local_path, f"{self.platform_name.lower()}_{repo_name}")
        
        # 移除配置助记词检查
        if not chat_mnemonic:
            print("❌ 未找到聊天助记词！")
            sys.exit(1)
        
        self.messenger = GitMessenger(repo_path, self.repo_url, username, token, chat_mnemonic)
        print("✅ 仓库连接成功！")
        print(f"📂 本地仓库路径: {repo_path}")
    except Exception as e:
        print(f"❌ 仓库连接失败: {str(e)}")
        sys.exit(1) 