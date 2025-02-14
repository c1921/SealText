import os
import sys
import shutil
from PyInstaller.__main__ import run

def clean_build():
    """清理构建文件"""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['SealText.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)

def build():
    """打包程序"""
    # 清理旧的构建文件
    clean_build()
    
    # PyInstaller 参数
    args = [
        'main.py',                    # 入口文件
        '--name=SealText',            # 程序名称
        '--onefile',                  # 打包成单个文件
        '--icon=assets/icon.ico',     # 程序图标
        '--add-data=README.md:.',     # 添加额外文件
        '--clean',                    # 清理临时文件
        '--noupx',                    # 不使用UPX压缩
    ]
    
    # Windows 特定配置
    if sys.platform.startswith('win'):
        args.extend([
            '--version-file=version.txt',  # 版本信息文件
        ])
    
    # 运行打包
    run(args)
    
    print("✅ 打包完成！")
    if sys.platform.startswith('win'):
        print("📦 输出文件: dist/SealText.exe")
    else:
        print("📦 输出文件: dist/SealText")

if __name__ == "__main__":
    build() 