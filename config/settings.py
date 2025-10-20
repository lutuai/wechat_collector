# -*- coding: utf-8 -*-
"""
配置文件
"""

# HTTP请求配置
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 请求超时设置（秒）
REQUEST_TIMEOUT = 30

# 图片下载配置
IMAGE_DOWNLOAD_TIMEOUT = 15
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# 文件命名配置
INVALID_FILENAME_CHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
MAX_FILENAME_LENGTH = 100

# Markdown转换配置
MARKDOWN_CONFIG = {
    'body_width': 0,  # 不限制行宽
    'unicode_snob': True,  # 使用Unicode字符
    'escape_snob': True,  # 转义特殊字符
    'mark_code': True,  # 标记代码块
}

# 默认输出目录
DEFAULT_OUTPUT_DIR = 'output'
