#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章采集器
主程序入口

使用方法:
    python main.py

功能:
    - 通过GUI界面输入微信公众号文章链接
    - 自动解析文章内容并转换为Markdown格式
    - 下载文章中的图片到本地
    - 保存到指定目录

作者: AI Assistant
版本: 1.0.0
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.gui_app import WeChatArticleCollectorGUI
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖包:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = [
        'requests',
        'beautifulsoup4',
        'lxml',
        'html2text',
        'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            # 特殊处理一些包名不一致的情况
            if package == 'beautifulsoup4':
                try:
                    __import__('bs4')
                except ImportError:
                    missing_packages.append(package)
            elif package == 'Pillow':
                try:
                    __import__('PIL')
                except ImportError:
                    missing_packages.append(package)
            else:
                missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def create_default_directories():
    """创建默认目录"""
    try:
        from config.settings import DEFAULT_OUTPUT_DIR
        
        if not os.path.exists(DEFAULT_OUTPUT_DIR):
            os.makedirs(DEFAULT_OUTPUT_DIR)
            print(f"创建默认输出目录: {DEFAULT_OUTPUT_DIR}")
    
    except Exception as e:
        print(f"创建默认目录失败: {e}")


def main():
    """主函数"""
    print("微信文章采集器 (WeChatScribe) v1.0.0")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 创建默认目录
    create_default_directories()
    
    try:
        # 启动GUI应用
        print("启动GUI界面...")
        app = WeChatArticleCollectorGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        return 0
    
    except Exception as e:
        print(f"程序运行出错: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
