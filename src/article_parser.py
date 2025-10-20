# -*- coding: utf-8 -*-
"""
微信公众号文章解析模块
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config.settings import REQUEST_HEADERS, REQUEST_TIMEOUT


class WeChatArticleParser:
    """微信公众号文章解析器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
    
    def parse_article(self, url):
        """
        解析微信公众号文章
        
        Args:
            url (str): 文章链接
            
        Returns:
            dict: 包含文章信息的字典
                {
                    'title': '文章标题',
                    'author': '作者',
                    'publish_time': '发布时间',
                    'content_html': '文章HTML内容',
                    'images': ['图片链接列表'],
                    'url': '原文链接'
                }
        """
        try:
            # 获取文章页面
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取文章信息
            article_info = {
                'url': url,
                'title': self._extract_title(soup),
                'author': self._extract_author(soup),
                'publish_time': self._extract_publish_time(soup),
                'content_html': self._extract_content(soup),
                'images': []
            }
            
            # 提取图片链接
            article_info['images'] = self._extract_images(soup, url)
            
            return article_info
            
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"文章解析失败: {str(e)}")
    
    def _extract_title(self, soup):
        """提取文章标题"""
        # 尝试多种选择器
        selectors = [
            '#activity-name',
            '.rich_media_title',
            'h1.rich_media_title',
            'h2.rich_media_title',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and title != '微信公众平台':
                    return self._clean_text(title)
        
        return "未知标题"
    
    def _extract_author(self, soup):
        """提取作者信息"""
        selectors = [
            '#js_name',
            '.rich_media_meta_text',
            '.profile_nickname',
            '[id*="author"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text().strip()
                if author:
                    return self._clean_text(author)
        
        return "未知作者"
    
    def _extract_publish_time(self, soup):
        """提取发布时间"""
        selectors = [
            '#publish_time',
            '.rich_media_meta_text',
            '[id*="time"]',
            '[class*="time"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                time_text = element.get_text().strip()
                # 尝试匹配时间格式
                time_pattern = r'\d{4}-\d{2}-\d{2}|\d{4}年\d{1,2}月\d{1,2}日'
                match = re.search(time_pattern, time_text)
                if match:
                    return match.group()
        
        return ""
    
    def _extract_content(self, soup):
        """提取文章正文内容"""
        # 微信文章内容的常见选择器
        content_selectors = [
            '#js_content',
            '.rich_media_content',
            '#js_article_container',
            '.article_content'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # 清理不需要的元素
                self._clean_content_element(content_element)
                return str(content_element)
        
        # 如果没找到特定容器，尝试提取body内容
        body = soup.find('body')
        if body:
            self._clean_content_element(body)
            return str(body)
        
        return ""
    
    def _extract_images(self, soup, base_url):
        """提取文章中的图片链接"""
        images = []
        
        # 查找所有图片标签
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            # 获取图片链接，优先使用data-src（懒加载）
            img_src = img.get('data-src') or img.get('src')
            
            if img_src:
                # 转换为绝对链接
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_src = urljoin(base_url, img_src)
                elif not img_src.startswith('http'):
                    img_src = urljoin(base_url, img_src)
                
                # 过滤掉一些无用的图片
                if self._is_valid_image_url(img_src):
                    images.append(img_src)
        
        return list(set(images))  # 去重
    
    def _clean_content_element(self, element):
        """清理内容元素，移除不需要的标签和属性"""
        # 移除脚本和样式标签
        for tag in element.find_all(['script', 'style', 'noscript']):
            tag.decompose()
        
        # 移除广告和推荐相关的元素
        ad_selectors = [
            '[class*="ad"]',
            '[id*="ad"]',
            '[class*="recommend"]',
            '[class*="related"]',
            '.qr_code_pc',
            '.reward_area'
        ]
        
        for selector in ad_selectors:
            for tag in element.select(selector):
                tag.decompose()
        
        # 清理属性，只保留必要的
        for tag in element.find_all():
            # 保留的属性
            keep_attrs = ['src', 'href', 'alt', 'title', 'data-src']
            attrs_to_remove = []
            
            for attr in tag.attrs:
                if attr not in keep_attrs:
                    attrs_to_remove.append(attr)
            
            for attr in attrs_to_remove:
                del tag[attr]
    
    def _is_valid_image_url(self, url):
        """判断是否为有效的图片链接"""
        if not url:
            return False
        
        # 过滤掉一些无用的图片
        invalid_patterns = [
            r'data:image',  # base64图片
            r'\.gif$',      # gif图片（通常是表情或装饰）
            r'avatar',      # 头像
            r'qrcode',      # 二维码
            r'1x1\.png',    # 统计像素
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _clean_text(self, text):
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text


def test_parser():
    """测试解析器"""
    parser = WeChatArticleParser()
    
    # 测试链接（需要替换为实际的微信文章链接）
    test_url = "https://mp.weixin.qq.com/s/example"
    
    try:
        result = parser.parse_article(test_url)
        print("解析成功:")
        print(f"标题: {result['title']}")
        print(f"作者: {result['author']}")
        print(f"发布时间: {result['publish_time']}")
        print(f"图片数量: {len(result['images'])}")
        print(f"内容长度: {len(result['content_html'])}")
    except Exception as e:
        print(f"解析失败: {e}")


if __name__ == "__main__":
    test_parser()
