# -*- coding: utf-8 -*-
"""
文件管理模块
"""

import os
import re
from datetime import datetime
from config.settings import INVALID_FILENAME_CHARS, MAX_FILENAME_LENGTH


class FileManager:
    """文件管理器"""
    
    def __init__(self):
        pass
    
    def save_article(self, article_info, markdown_content, output_dir):
        """
        保存文章到指定目录
        
        Args:
            article_info (dict): 文章信息
            markdown_content (str): Markdown内容
            output_dir (str): 输出目录
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            filename = self._generate_filename(article_info)
            
            # 确保文件名唯一
            filepath = self._get_unique_filepath(output_dir, filename)
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
    
    def _generate_filename(self, article_info):
        """
        生成文件名
        
        Args:
            article_info (dict): 文章信息
            
        Returns:
            str: 文件名（不包含路径）
        """
        # 优先使用标题作为文件名
        title = article_info.get('title', '').strip()
        
        if title and title != "未知标题":
            filename = self._clean_filename(title)
        else:
            # 如果没有标题，使用时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_{timestamp}"
        
        # 限制文件名长度
        if len(filename) > MAX_FILENAME_LENGTH:
            filename = filename[:MAX_FILENAME_LENGTH]
        
        # 添加扩展名
        filename += ".md"
        
        return filename
    
    def _clean_filename(self, filename):
        """
        清理文件名，移除无效字符
        
        Args:
            filename (str): 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除无效字符
        for char in INVALID_FILENAME_CHARS:
            filename = filename.replace(char, '_')
        
        # 移除多余的空白字符
        filename = re.sub(r'\s+', '_', filename)
        
        # 移除连续的下划线
        filename = re.sub(r'_+', '_', filename)
        
        # 移除首尾的下划线和点
        filename = filename.strip('_.')
        
        # 如果清理后为空，使用默认名称
        if not filename:
            filename = "untitled"
        
        return filename
    
    def _get_unique_filepath(self, directory, filename):
        """
        获取唯一的文件路径，如果文件已存在则添加序号
        
        Args:
            directory (str): 目录路径
            filename (str): 文件名
            
        Returns:
            str: 唯一的文件路径
        """
        base_path = os.path.join(directory, filename)
        
        # 如果文件不存在，直接返回
        if not os.path.exists(base_path):
            return base_path
        
        # 文件已存在，添加序号
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_path = os.path.join(directory, new_filename)
            
            if not os.path.exists(new_path):
                return new_path
            
            counter += 1
            
            # 防止无限循环
            if counter > 9999:
                raise Exception("无法生成唯一文件名")
    
    def create_directory_structure(self, base_dir, article_info):
        """
        创建目录结构
        
        Args:
            base_dir (str): 基础目录
            article_info (dict): 文章信息
            
        Returns:
            dict: 包含各种路径的字典
        """
        try:
            # 创建基础目录
            os.makedirs(base_dir, exist_ok=True)
            
            # 可以根据需要创建子目录结构
            # 例如：按作者、按日期等分类
            
            paths = {
                'base_dir': base_dir,
                'images_dir': os.path.join(base_dir, 'images'),
                'articles_dir': base_dir  # 文章直接保存在基础目录
            }
            
            # 创建图片目录
            os.makedirs(paths['images_dir'], exist_ok=True)
            
            return paths
            
        except Exception as e:
            raise Exception(f"创建目录结构失败: {str(e)}")
    
    def get_file_info(self, filepath):
        """
        获取文件信息
        
        Args:
            filepath (str): 文件路径
            
        Returns:
            dict: 文件信息
        """
        try:
            if not os.path.exists(filepath):
                return None
            
            stat = os.stat(filepath)
            
            return {
                'path': filepath,
                'name': os.path.basename(filepath),
                'size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'is_file': os.path.isfile(filepath),
                'is_dir': os.path.isdir(filepath)
            }
            
        except Exception as e:
            raise Exception(f"获取文件信息失败: {str(e)}")
    
    def list_articles(self, directory):
        """
        列出目录中的所有文章文件
        
        Args:
            directory (str): 目录路径
            
        Returns:
            list: 文章文件列表
        """
        try:
            if not os.path.exists(directory):
                return []
            
            articles = []
            
            for filename in os.listdir(directory):
                if filename.endswith('.md'):
                    filepath = os.path.join(directory, filename)
                    file_info = self.get_file_info(filepath)
                    if file_info:
                        articles.append(file_info)
            
            # 按修改时间排序（最新的在前）
            articles.sort(key=lambda x: x['modified_time'], reverse=True)
            
            return articles
            
        except Exception as e:
            raise Exception(f"列出文章失败: {str(e)}")
    
    def delete_file(self, filepath):
        """
        删除文件
        
        Args:
            filepath (str): 文件路径
            
        Returns:
            bool: 是否成功删除
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
            
        except Exception as e:
            raise Exception(f"删除文件失败: {str(e)}")
    
    def get_directory_size(self, directory):
        """
        获取目录大小
        
        Args:
            directory (str): 目录路径
            
        Returns:
            int: 目录大小（字节）
        """
        try:
            total_size = 0
            
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            return total_size
            
        except Exception as e:
            return 0
    
    def format_file_size(self, size_bytes):
        """
        格式化文件大小显示
        
        Args:
            size_bytes (int): 文件大小（字节）
            
        Returns:
            str: 格式化的大小字符串
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


def test_file_manager():
    """测试文件管理器"""
    fm = FileManager()
    
    # 测试文章信息
    test_article = {
        'title': '测试文章标题：包含特殊字符<>?*',
        'author': '测试作者',
        'publish_time': '2023-01-01',
        'url': 'https://example.com/article'
    }
    
    test_content = """---
title: "测试文章"
author: "测试作者"
---

# 测试文章

这是测试内容。
"""
    
    try:
        # 测试保存文章
        test_dir = "test_output"
        filepath = fm.save_article(test_article, test_content, test_dir)
        print(f"文章保存成功: {filepath}")
        
        # 测试文件信息
        file_info = fm.get_file_info(filepath)
        print(f"文件信息: {file_info}")
        
        # 测试列出文章
        articles = fm.list_articles(test_dir)
        print(f"找到 {len(articles)} 篇文章")
        
        # 清理测试文件
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    test_file_manager()
