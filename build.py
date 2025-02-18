import PyInstaller.__main__
import os
import sys
from string import Template
from versioning.version import *

def generate_version():
    """生成版本信息文件"""
    # 添加版本信息日志
    # 使用 sys.stdout.buffer.write 来处理编码问题
    sys.stdout.buffer.write(f"当前版本号: {VERSION_STR}\n".encode('utf-8'))
    
    try:
        # 读取模板文件
        with open('versioning/version.template', 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 准备替换变量
        version_tuple = VERSION + (0,)  # 添加一个0作为第四个版本号
        variables = {
            'VERSION_TUPLE': str(version_tuple),
            'VERSION_STR': VERSION_STR,
            'APP_NAME': APP_NAME,
            'COMPANY': COMPANY,
            'DESCRIPTION': DESCRIPTION,
            'COPYRIGHT': COPYRIGHT
        }
        
        # 替换变量生成最终内容
        version = template.substitute(variables)
        
        # 写入文件
        with open('versioning/version.txt', 'w', encoding='utf-8') as f:
            f.write(version)
            
    except Exception as e:
        sys.stderr.buffer.write(f"生成版本信息时出错: {str(e)}\n".encode('utf-8'))
        raise

def build():
    """构建Web版本"""
    output_name = f"SealText_v{VERSION_STR}"
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'api', 'static')
    
    # 确保静态文件目录存在
    if not os.path.exists(static_path):
        os.makedirs(static_path)
        os.makedirs(os.path.join(static_path, 'css'))
        print(f"创建静态文件目录: {static_path}")
    
    PyInstaller.__main__.run([
        'run_api.py',
        f'--name={output_name}',
        '--onefile',
        '--icon=assets/icon.ico',
        '--version-file=versioning/version.txt',
        '--clean',
        '--noupx',
        f'--add-data={static_path};src/api/static',
        '--console'
    ])

if __name__ == "__main__":
    # 设置默认编码为 UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    # 生成版本信息
    generate_version()

    # 确保在正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 构建
    print("开始构建...")
    build()
    print("构建完成！") 