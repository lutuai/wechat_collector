# -*- coding: utf-8 -*-
"""
微信公众号主页解析模块
用于批量获取公众号文章列表
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from config.settings import REQUEST_HEADERS, REQUEST_TIMEOUT


class WeChatProfileParser:
    """微信公众号主页解析器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
    
    def parse_profile_articles(self, profile_url, max_count=10):
        """
        解析公众号主页，获取文章列表
        
        Args:
            profile_url (str): 公众号主页链接或任意一篇文章链接
            max_count (int): 最大获取文章数量
            
        Returns:
            list: 文章信息列表
                [{
                    'title': '文章标题',
                    'url': '文章链接',
                    'publish_time': '发布时间',
                    'is_original': True/False,
                    'read_count': 0,  # 阅读量（可能无法获取）
                    'like_count': 0,  # 点赞数（可能无法获取）
                    'author': '作者',
                    'digest': '摘要'
                }]
        """
        try:
            # 如果输入的是文章链接，尝试获取公众号信息
            if '/s/' in profile_url or '/s?' in profile_url:
                return self._parse_from_article_page(profile_url, max_count)
            else:
                return self._parse_from_profile_page(profile_url, max_count)
                
        except Exception as e:
            raise Exception(f"解析公众号文章列表失败: {str(e)}")
    
    def _parse_from_article_page(self, article_url, max_count):
        """从文章页面获取公众号信息并解析文章列表"""
        try:
            # 获取文章页面
            response = self.session.get(article_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取公众号信息
            author_info = self._extract_author_info(soup)
            
            # 尝试从页面中提取更多文章链接
            articles = self._extract_articles_from_page(soup, author_info)
            
            # 如果文章数量不够，尝试其他方法
            if len(articles) < max_count:
                # 可以在这里添加更多获取文章的逻辑
                pass
            
            return articles[:max_count]
            
        except Exception as e:
            raise Exception(f"从文章页面解析失败: {str(e)}")
    
    def _parse_from_profile_page(self, profile_url, max_count):
        """从公众号主页解析文章列表"""
        # 这个方法用于处理直接的公众号主页链接
        # 由于微信公众号主页的限制，这个功能可能需要特殊处理
        raise Exception("暂不支持直接解析公众号主页，请提供任意一篇该公众号的文章链接")
    
    def _extract_author_info(self, soup):
        """提取作者信息"""
        author_info = {
            'name': '未知作者',
            'avatar': '',
            'description': ''
        }
        
        # 提取作者名称
        author_selectors = [
            '#js_name',
            '.rich_media_meta_text',
            '.profile_nickname'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author_name = element.get_text().strip()
                if author_name:
                    author_info['name'] = author_name
                    break
        
        return author_info
    
    def _extract_articles_from_page(self, soup, author_info):
        """从页面中提取文章信息"""
        articles = []
        
        # 尝试从页面底部的推荐文章中提取
        recommendation_selectors = [
            '.related_article',
            '.recommend_article',
            '[class*="recommend"]',
            '[class*="related"]'
        ]
        
        for selector in recommendation_selectors:
            elements = soup.select(selector)
            for element in elements:
                article = self._parse_article_element(element, author_info)
                if article:
                    articles.append(article)
        
        # 尝试从JavaScript数据中提取
        script_articles = self._extract_from_scripts(soup, author_info)
        articles.extend(script_articles)
        
        # 去重
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles
    
    def _parse_article_element(self, element, author_info):
        """解析单个文章元素"""
        try:
            article = {
                'title': '',
                'url': '',
                'publish_time': '',
                'is_original': False,
                'read_count': 0,
                'like_count': 0,
                'author': author_info['name'],
                'digest': ''
            }
            
            # 提取标题
            title_element = element.select_one('a') or element.select_one('[title]')
            if title_element:
                article['title'] = title_element.get('title') or title_element.get_text().strip()
                article['url'] = title_element.get('href', '')
            
            # 提取摘要
            digest_element = element.select_one('.digest') or element.select_one('[class*="desc"]')
            if digest_element:
                article['digest'] = digest_element.get_text().strip()
            
            # 检查是否为原创
            if '原创' in element.get_text():
                article['is_original'] = True
            
            # 只返回有效的文章
            if article['title'] and article['url']:
                return article
            
        except Exception:
            pass
        
        return None
    
    def _extract_from_scripts(self, soup, author_info):
        """从JavaScript代码中提取文章信息"""
        articles = []
        
        try:
            # 查找包含文章数据的script标签
            scripts = soup.find_all('script')
            
            for script in scripts:
                if not script.string:
                    continue
                
                script_content = script.string
                
                # 尝试匹配文章数据的JSON格式
                json_patterns = [
                    r'var\s+msg_list\s*=\s*(\[.*?\]);',
                    r'msgList\s*:\s*(\[.*?\])',
                    r'"articles"\s*:\s*(\[.*?\])'
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            if isinstance(data, list):
                                for item in data:
                                    article = self._parse_json_article(item, author_info)
                                    if article:
                                        articles.append(article)
                        except json.JSONDecodeError:
                            continue
                            
        except Exception:
            pass
        
        return articles
    
    def _parse_json_article(self, item, author_info):
        """解析JSON格式的文章数据"""
        try:
            if not isinstance(item, dict):
                return None
            
            article = {
                'title': item.get('title', '').strip(),
                'url': item.get('content_url', '').strip(),
                'publish_time': item.get('datetime', ''),
                'is_original': item.get('is_original', 0) == 1,
                'read_count': item.get('read_num', 0),
                'like_count': item.get('like_num', 0),
                'author': item.get('author', author_info['name']),
                'digest': item.get('digest', '').strip()
            }
            
            # 处理URL
            if article['url'] and not article['url'].startswith('http'):
                article['url'] = 'https://mp.weixin.qq.com' + article['url']
            
            # 只返回有效的文章
            if article['title'] and article['url']:
                return article
                
        except Exception:
            pass
        
        return None
    
    def get_article_stats(self, article_url):
        """
        获取文章统计信息（阅读量、点赞数等）
        注意：由于微信的限制，这些数据可能无法直接获取
        """
        try:
            response = self.session.get(article_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            stats = {
                'read_count': 0,
                'like_count': 0,
                'is_original': False
            }
            
            # 尝试从页面中提取统计信息
            # 注意：这些选择器可能需要根据实际页面结构调整
            read_count_element = soup.select_one('#readNum') or soup.select_one('[id*="read"]')
            if read_count_element:
                read_text = read_count_element.get_text().strip()
                read_match = re.search(r'\d+', read_text)
                if read_match:
                    stats['read_count'] = int(read_match.group())
            
            like_count_element = soup.select_one('#likeNum') or soup.select_one('[id*="like"]')
            if like_count_element:
                like_text = like_count_element.get_text().strip()
                like_match = re.search(r'\d+', like_text)
                if like_match:
                    stats['like_count'] = int(like_match.group())
            
            # 检查是否为原创
            if '原创' in response.text:
                stats['is_original'] = True
            
            return stats
            
        except Exception as e:
            # 如果无法获取统计信息，返回默认值
            return {'read_count': 0, 'like_count': 0, 'is_original': False}
    
    def filter_articles_by_criteria(self, articles, min_read_count=0, original_only=False):
        """
        根据条件筛选文章
        
        Args:
            articles (list): 文章列表
            min_read_count (int): 最小阅读量
            original_only (bool): 是否只要原创文章
            
        Returns:
            list: 筛选后的文章列表
        """
        filtered_articles = []
        
        for article in articles:
            # 检查阅读量
            if article.get('read_count', 0) < min_read_count:
                continue
            
            # 检查是否只要原创
            if original_only and not article.get('is_original', False):
                continue
            
            filtered_articles.append(article)
        
        return filtered_articles


def test_profile_parser():
    """测试公众号解析器"""
    parser = WeChatProfileParser()
    
    # 测试链接（需要替换为实际的微信文章链接）
    test_url = "https://mp.weixin.qq.com/s/example"
    
    try:
        articles = parser.parse_profile_articles(test_url, max_count=5)
        print(f"找到 {len(articles)} 篇文章:")
        
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   链接: {article['url']}")
            print(f"   作者: {article['author']}")
            print(f"   原创: {'是' if article['is_original'] else '否'}")
            print(f"   阅读量: {article['read_count']}")
            
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    test_profile_parser()
