from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.git.git_chat import GitChat
from src.config import load_config, save_config
import os
import sys
from versioning.version import VERSION_STR, APP_NAME

app = FastAPI(title="SealText API")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取静态文件目录路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    static_dir = os.path.join(sys._MEIPASS, 'src', 'api', 'static')
else:
    # 如果是开发环境
    static_dir = os.path.join(os.path.dirname(__file__), 'static')

# 添加静态文件支持
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 数据模型
class Message(BaseModel):
    content: str
    author: str
    timestamp: str

class ChatConfig(BaseModel):
    platform: str
    repo_url: str
    username: str
    token: str
    chat_mnemonic: str

# 全局聊天实例
chat_instance: Optional[GitChat] = None

def get_chat():
    if not chat_instance:
        raise HTTPException(status_code=400, detail="Chat not initialized")
    return chat_instance

@app.get("/config")
async def get_config():
    """获取已保存的配置"""
    try:
        config = load_config()
        if not config:
            raise HTTPException(status_code=404, detail="未找到配置")
        return {
            "platforms": list(config.get('platforms', {}).keys()),
            "display_name": config.get('display_name'),
            "repos": config.get('repos', {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/init")
async def initialize_chat(repo_url: str, platform: str):
    """使用已保存的配置初始化聊天"""
    global chat_instance
    try:
        config = load_config()
        if not config or platform not in config['platforms']:
            raise HTTPException(status_code=400, detail="无效的平台配置")
        
        platform_info = config['platforms'][platform]
        repo_info = config.get('repos', {}).get(platform, {}).get(repo_url)
        
        if not repo_info:
            raise HTTPException(status_code=400, detail="未找到仓库配置")
        
        chat_instance = GitChat(
            repo_url,
            platform,
            platform_info['username'],
            platform_info['token'],
            repo_info['mnemonic']
        )
        return {"status": "success", "message": "Chat initialized"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/messages", response_model=List[Message])
async def get_messages(chat: GitChat = Depends(get_chat)):
    """获取所有消息"""
    try:
        messages = chat.get_messages()
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/messages")
async def send_message(message: str, chat: GitChat = Depends(get_chat)):
    """发送消息"""
    try:
        config = load_config()
        if chat.send_message(message, config['display_name']):
            return {"status": "success", "message": "Message sent"}
        raise HTTPException(status_code=500, detail="Failed to send message")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def get_chat_page():
    """返回聊天页面"""
    if getattr(sys, 'frozen', False):
        index_path = os.path.join(sys._MEIPASS, 'src', 'api', 'static', 'index.html')
    else:
        index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    return FileResponse(index_path)

@app.get("/version")
async def get_version():
    """获取版本信息"""
    return {
        "version": VERSION_STR,
        "name": APP_NAME
    } 