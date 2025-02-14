#!/usr/bin/env python3
import sys
import os
from git_chat import run_chat

def print_banner():
    """打印程序启动横幅"""
    print("""
███████╗███████╗ █████╗ ██╗  ████████╗███████╗██╗  ██╗████████╗
██╔════╝██╔════╝██╔══██╗██║  ╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝
███████╗█████╗  ███████║██║     ██║   █████╗   ╚███╔╝    ██║   
╚════██║██╔══╝  ██╔══██║██║     ██║   ██╔══╝   ██╔██╗    ██║   
███████║███████╗██║  ██║███████╗██║   ███████╗██╔╝ ██╗   ██║   
╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   
                                                               
=====================基于 Git 的加密聊天工具=====================
    """)

def main():
    """程序主入口"""
    try:
        print_banner()
        run_chat()
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 