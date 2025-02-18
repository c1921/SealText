import uvicorn
import argparse
from src.api.api import app
from versioning.version import VERSION_STR, APP_NAME

def main():
    parser = argparse.ArgumentParser(description=f'{APP_NAME} Web Server')
    parser.add_argument('--host', default='127.0.0.1', help='监听地址')
    parser.add_argument('--port', type=int, default=8000, help='监听端口')
    args = parser.parse_args()

    print(f"启动 {APP_NAME} Web 服务器 v{VERSION_STR}")
    print(f"访问地址: http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main() 