# -*- coding: utf-8 -*-
"""
Markdown转换模块
"""

import os
import re
import html2text
import requests
from urllib.parse import urlparse, urljoin
from PIL import Image
from config.settings import (
    MARKDOWN_CONFIG, 
    IMAGE_DOWNLOAD_TIMEOUT, 
    MAX_IMAGE_SIZE,
    REQUEST_HEADERS
)


class MarkdownConverter:
    """HTML到Markdown转换器"""
    
    def __init__(self):
        self.h2t = html2text.HTML2Text()
        self._configure_html2text()
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
    
    def _configure_html2text(self):
        """配置html2text转换器"""
        self.h2t.body_width = MARKDOWN_CONFIG['body_width']
        self.h2t.unicode_snob = MARKDOWN_CONFIG['unicode_snob']
        self.h2t.escape_snob = MARKDOWN_CONFIG['escape_snob']
        self.h2t.mark_code = MARKDOWN_CONFIG['mark_code']
        
        # 其他配置
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.skip_internal_links = True
        self.h2t.inline_links = True
        self.h2t.protect_links = True
        self.h2t.wrap_links = False
    
    def convert_to_markdown(self, article_info, output_dir, images_dir="images"):
        """
        将文章信息转换为Markdown格式
        
        Args:
            article_info (dict): 文章信息字典
            output_dir (str): 输出目录
            images_dir (str): 图片子目录名
            
        Returns:
            str: Markdown内容
        """
        try:
            # 创建图片目录
            full_images_dir = os.path.join(output_dir, images_dir)
            os.makedirs(full_images_dir, exist_ok=True)
            
            # 下载图片并更新HTML中的图片链接
            updated_html = self._download_and_update_images(
                article_info['content_html'], 
                article_info['images'], 
                full_images_dir,
                images_dir
            )
            
            # 转换为Markdown
            markdown_content = self.h2t.handle(updated_html)
            
            # 添加文章元信息头部
            markdown_with_meta = self._add_metadata_header(article_info, markdown_content)
            
            # 清理和格式化Markdown
            final_markdown = self._clean_markdown(markdown_with_meta)
            
            return final_markdown
            
        except Exception as e:
            raise Exception(f"Markdown转换失败: {str(e)}")
    
    def _download_and_update_images(self, html_content, image_urls, images_dir, relative_images_dir):
        """
        下载图片并更新HTML中的图片链接
        
        Args:
            html_content (str): HTML内容
            image_urls (list): 图片URL列表
            images_dir (str): 图片保存的绝对路径
            relative_images_dir (str): 图片的相对路径（用于Markdown引用）
            
        Returns:
            str: 更新后的HTML内容
        """
        updated_html = html_content
        
        for i, img_url in enumerate(image_urls):
            try:
                # 下载图片
                local_filename = self._download_image(img_url, images_dir, i)
                
                if local_filename:
                    # 构建相对路径
                    relative_path = f"{relative_images_dir}/{local_filename}"
                    
                    # 更新HTML中的图片链接
                    # 处理各种可能的图片标签格式
                    patterns = [
                        rf'src="{re.escape(img_url)}"',
                        rf"src='{re.escape(img_url)}'",
                        rf'data-src="{re.escape(img_url)}"',
                        rf"data-src='{re.escape(img_url)}'"
                    ]
                    
                    for pattern in patterns:
                        updated_html = re.sub(
                            pattern, 
                            f'src="{relative_path}"', 
                            updated_html
                        )
                        
            except Exception as e:
                print(f"下载图片失败 {img_url}: {e}")
                continue
        
        return updated_html
    
    def _download_image(self, img_url, images_dir, index):
        """
        下载单个图片
        
        Args:
            img_url (str): 图片URL
            images_dir (str): 保存目录
            index (int): 图片索引
            
        Returns:
            str: 本地文件名，失败返回None
        """
        try:
            response = self.session.get(img_url, timeout=IMAGE_DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()
            
            # 检查文件大小
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_IMAGE_SIZE:
                print(f"图片过大，跳过: {img_url}")
                return None
            
            # 获取文件扩展名
            parsed_url = urlparse(img_url)
            path = parsed_url.path
            ext = os.path.splitext(path)[1].lower()
            
            # 如果没有扩展名，尝试从Content-Type获取
            if not ext:
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                else:
                    ext = '.jpg'  # 默认扩展名
            
            # 生成文件名
            filename = f"image_{index:03d}{ext}"
            filepath = os.path.join(images_dir, filename)
            
            # 保存图片
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 验证图片文件
            try:
                with Image.open(filepath) as img:
                    img.verify()
                return filename
            except Exception:
                # 如果不是有效图片，删除文件
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
                
        except Exception as e:
            print(f"下载图片失败 {img_url}: {e}")
            return None
    
    def _add_metadata_header(self, article_info, markdown_content):
        """
        添加文章元信息头部
        
        Args:
            article_info (dict): 文章信息
            markdown_content (str): Markdown内容
            
        Returns:
            str: 带有元信息头部的Markdown
        """
        metadata_lines = [
            "---",
            f"title: \"{article_info['title']}\"",
            f"author: \"{article_info['author']}\"",
        ]
        
        if article_info['publish_time']:
            metadata_lines.append(f"date: \"{article_info['publish_time']}\"")
        
        metadata_lines.extend([
            f"source: \"{article_info['url']}\"",
            "---",
            "",
        ])
        
        return "\n".join(metadata_lines) + markdown_content
    
    def _clean_markdown(self, markdown_content):
        """
        清理和格式化Markdown内容
        
        Args:
            markdown_content (str): 原始Markdown内容
            
        Returns:
            str: 清理后的Markdown内容
        """
        # 移除多余的空行
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
        
        # 清理行首行尾空白
        lines = []
        for line in markdown_content.split('\n'):
            lines.append(line.rstrip())
        
        # 移除文档末尾的多余空行
        while lines and not lines[-1].strip():
            lines.pop()
        
        # 确保文档以换行符结尾
        if lines:
            lines.append('')
        
        return '\n'.join(lines)


def test_converter():
    """测试转换器"""
    # 测试HTML内容
    test_html = """
    <div>
        <h1>测试标题</h1>
        <p>这是一段测试文本。</p>
        <img src="https://example.com/test.jpg" alt="测试图片">
        <p>更多内容...</p>
    </div>
    """
    
    test_article = {
        'title': '测试文章',
        'author': '测试作者',
        'publish_time': '2023-01-01',
        'content_html': test_html,
        'images': ['https://example.com/test.jpg'],
        'url': 'https://example.com/article'
    }
    
    converter = MarkdownConverter()
    
    try:
        # 创建测试输出目录
        test_output_dir = 'test_output'
        os.makedirs(test_output_dir, exist_ok=True)
        
        markdown = converter.convert_to_markdown(test_article, test_output_dir)
        print("转换成功:")
        print(markdown)
        
        # 清理测试目录
        import shutil
        if os.path.exists(test_output_dir):
            shutil.rmtree(test_output_dir)
            
    except Exception as e:
        print(f"转换失败: {e}")


if __name__ == "__main__":
    test_converter()
