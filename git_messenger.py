import os
import git
import json
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GitMessenger:
    def __init__(self, repo_path, remote_url=None, username=None, token=None):
        self.repo_path = repo_path
        self.remote_url = remote_url
        self.username = username
        self.token = token
        
        logger.debug(f"初始化 GitMessenger: repo_path={repo_path}, remote_url={remote_url}, username={username}")
        
        # 如果提供了用户名和令牌，修改远程URL以包含认证信息
        if remote_url and username and token:
            if remote_url.startswith('https://'):
                self.remote_url = remote_url.replace('https://', f'https://{username}:{token}@')
                logger.debug(f"设置认证URL: {self.remote_url.replace(token, '****')}")
        
        self.repo = self._init_repo()
    
    def _init_repo(self):
        try:
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
                    
                    # 创建初始提交
                    logger.debug("创建初始提交")
                    message_file = os.path.join(self.repo_path, 'messages.json')
                    open(message_file, 'w', encoding='utf-8').write('[]')
                    repo.index.add(['messages.json'])
                    repo.index.commit('Initial commit')
                    
                    # 设置上游分支并推送
                    logger.debug("推送初始提交")
                    repo.git.push('--set-upstream', 'origin', 'main')
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
                    repo.create_head('main')
                
                if repo.active_branch.name != 'main':
                    logger.debug("切换到 main 分支")
                    repo.heads.main.checkout()
                
                # 尝试设置上游分支
                try:
                    logger.debug("设置上游分支")
                    repo.git.branch('--set-upstream-to=origin/main', 'main')
                except git.exc.GitCommandError:
                    logger.warning("设置上游分支失败，尝试先拉取")
                    origin = repo.remote('origin')
                    origin.fetch()
                    repo.git.branch('--set-upstream-to=origin/main', 'main')
            
            return repo
            
        except Exception as e:
            logger.error(f"初始化仓库失败: {str(e)}", exc_info=True)
            raise
    
    def send_message(self, message, author):
        try:
            logger.debug("开始发送消息")
            # 先拉取最新更改
            origin = self.repo.remotes.origin
            logger.debug("拉取最新更改")
            origin.pull()
            
            message_file = os.path.join(self.repo_path, 'messages.json')
            logger.debug(f"读取消息文件: {message_file}")
            
            # 读取或创建消息文件
            if os.path.exists(message_file):
                with open(message_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # 添加新消息
            messages.append({
                'content': message,
                'author': author,
                'timestamp': datetime.now().isoformat()
            })
            
            # 保存消息
            logger.debug("保存消息")
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # 提交更改
            logger.debug("提交更改")
            self.repo.index.add(['messages.json'])
            self.repo.index.commit(f"Message from {author}")
            
            # 推送到远程仓库
            logger.debug("推送到远程仓库")
            origin.push()
            
        except git.exc.GitCommandError as e:
            logger.error(f"Git操作失败: {str(e)}", exc_info=True)
            if "no upstream branch" in str(e):
                logger.debug("尝试设置上游分支")
                self.repo.git.push('--set-upstream', 'origin', 'main')
            else:
                raise
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}", exc_info=True)
            raise
    
    def receive_messages(self):
        # 拉取最新更改
        origin = self.repo.remotes.origin
        origin.pull()
        
        message_file = os.path.join(self.repo_path, 'messages.json')
        if os.path.exists(message_file):
            with open(message_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return [] 