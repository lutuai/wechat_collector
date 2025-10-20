# -*- coding: utf-8 -*-
"""
桌面GUI界面模块
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime

from article_parser import WeChatArticleParser
from markdown_converter import MarkdownConverter
from file_manager import FileManager
from config.settings import DEFAULT_OUTPUT_DIR


class WeChatArticleCollectorGUI:
    """微信公众号文章采集器GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        self.setup_layout()
        
        # 初始化核心组件
        self.parser = WeChatArticleParser()
        self.converter = MarkdownConverter()
        self.file_manager = FileManager()
        
        # 工作线程
        self.worker_thread = None
        self.is_working = False
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("微信文章采集器 - WeChatScribe")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_variables(self):
        """设置变量"""
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="就绪")
    
    def setup_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="微信文章采集器 - WeChatScribe", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL输入区域
        url_frame = ttk.LabelFrame(main_frame, text="文章链接", padding="10")
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=("Arial", 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        paste_button = ttk.Button(url_frame, text="粘贴", command=self.paste_url)
        paste_button.grid(row=0, column=1)
        
        clear_button = ttk.Button(url_frame, text="清空", command=self.clear_url)
        clear_button.grid(row=0, column=2, padx=(5, 0))
        
        # 输出目录选择区域
        dir_frame = ttk.LabelFrame(main_frame, text="保存目录", padding="10")
        dir_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, font=("Arial", 10))
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_button = ttk.Button(dir_frame, text="浏览", command=self.browse_directory)
        browse_button.grid(row=0, column=1)
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.collect_button = ttk.Button(button_frame, text="开始采集", 
                                        command=self.start_collection, 
                                        style="Accent.TButton")
        self.collect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止", 
                                     command=self.stop_collection, 
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        open_dir_button = ttk.Button(button_frame, text="打开目录", 
                                    command=self.open_output_directory)
        open_dir_button.pack(side=tk.LEFT)
        
        # 进度和状态区域
        progress_frame = ttk.LabelFrame(main_frame, text="进度和状态", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # 日志文本区域
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, 
                                                 font=("Consolas", 9))
        self.log_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_layout(self):
        """设置布局"""
        # 绑定回车键到开始采集
        self.root.bind('<Return>', lambda e: self.start_collection())
        
        # 设置焦点到URL输入框
        self.url_entry.focus()
    
    def paste_url(self):
        """粘贴URL"""
        try:
            clipboard_content = self.root.clipboard_get()
            self.url_var.set(clipboard_content.strip())
        except:
            pass
    
    def clear_url(self):
        """清空URL"""
        self.url_var.set("")
        self.url_entry.focus()
    
    def browse_directory(self):
        """浏览目录"""
        directory = filedialog.askdirectory(
            title="选择保存目录",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)
    
    def open_output_directory(self):
        """打开输出目录"""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showwarning("警告", "输出目录不存在")
    
    def log_message(self, message, level="INFO"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        # 在主线程中更新GUI
        self.root.after(0, self._append_log, log_entry)
    
    def _append_log(self, log_entry):
        """在主线程中添加日志"""
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, status):
        """更新状态"""
        self.root.after(0, lambda: self.status_var.set(status))
    
    def update_progress(self, progress):
        """更新进度"""
        self.root.after(0, lambda: self.progress_var.set(progress))
    
    def start_collection(self):
        """开始采集"""
        if self.is_working:
            return
        
        url = self.url_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        
        # 验证输入
        if not url:
            messagebox.showerror("错误", "请输入文章链接")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择保存目录")
            return
        
        # 验证URL格式
        url_validation = self.validate_url_with_confidence(url)
        if url_validation['confidence'] == 'low':
            result = messagebox.askyesno("确认", f"链接格式可能不正确：{url_validation['reason']}\n是否继续？")
            if not result:
                return
        elif url_validation['confidence'] == 'invalid':
            messagebox.showerror("错误", f"无效的链接格式：{url_validation['reason']}")
            return
        
        # 开始工作
        self.is_working = True
        self.collect_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 启动工作线程
        self.worker_thread = threading.Thread(target=self.collection_worker, 
                                             args=(url, output_dir))
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def stop_collection(self):
        """停止采集"""
        self.is_working = False
        self.update_status("正在停止...")
        self.log_message("用户请求停止采集", "WARN")
    
    def collection_worker(self, url, output_dir):
        """采集工作线程"""
        try:
            self.update_status("正在解析文章...")
            self.update_progress(10)
            self.log_message("开始解析文章...")
            
            # 解析文章
            article_info = self.parser.parse_article(url)
            
            if not self.is_working:
                return
            
            self.update_progress(30)
            self.log_message(f"文章解析成功: {article_info['title']}")
            self.log_message(f"作者: {article_info['author']}")
            self.log_message(f"发布时间: {article_info['publish_time']}")
            self.log_message(f"图片数量: {len(article_info['images'])}")
            
            # 转换为Markdown
            self.update_status("正在转换为Markdown...")
            self.update_progress(50)
            self.log_message("开始转换为Markdown格式...")
            
            markdown_content = self.converter.convert_to_markdown(
                article_info, output_dir
            )
            
            if not self.is_working:
                return
            
            self.update_progress(80)
            self.log_message("Markdown转换完成")
            
            # 保存文件
            self.update_status("正在保存文件...")
            self.log_message("开始保存文件...")
            
            filepath = self.file_manager.save_article(
                article_info, markdown_content, output_dir
            )
            
            self.update_progress(100)
            self.update_status("采集完成")
            self.log_message(f"文件保存成功: {filepath}", "SUCCESS")
            
            # 显示成功消息
            self.root.after(0, lambda: messagebox.showinfo(
                "成功", f"文章采集完成！\n保存位置: {filepath}"
            ))
            
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"采集失败: {error_msg}", "ERROR")
            self.update_status("采集失败")
            
            # 显示错误消息
            self.root.after(0, lambda: messagebox.showerror("错误", f"采集失败:\n{error_msg}"))
        
        finally:
            # 恢复按钮状态
            self.root.after(0, self.collection_finished)
    
    def collection_finished(self):
        """采集完成后的清理工作"""
        self.is_working = False
        self.collect_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if self.progress_var.get() < 100:
            self.update_progress(0)
            self.update_status("就绪")
    
    def is_valid_wechat_url(self, url):
        """验证是否为有效的微信文章URL"""
        import re
        
        # 更全面的微信文章URL模式
        wechat_patterns = [
            # 标准微信公众号文章链接
            r'https?://mp\.weixin\.qq\.com/s/',
            r'https?://mp\.weixin\.qq\.com/s\?',
            # 微信内部链接
            r'https?://weixin\.qq\.com/',
            # 短链接形式
            r'https?://.*\.weixin\.qq\.com/',
            # 包含__biz参数的链接（微信文章特有）
            r'.*__biz=.*',
            # 包含mid参数的链接
            r'.*mid=.*',
            # 包含sn参数的链接（微信文章特有）
            r'.*sn=.*'
        ]
        
        url_lower = url.lower().strip()
        
        # 基本URL格式检查
        if not url_lower.startswith(('http://', 'https://')):
            return False
        
        # 检查是否匹配微信文章模式
        for pattern in wechat_patterns:
            if re.search(pattern, url_lower):
                return True
        
        # 如果包含微信相关的关键参数，也认为是有效的
        wechat_params = ['__biz', 'mid', 'sn', 'idx']
        for param in wechat_params:
            if param in url_lower:
                return True
        
        return False
    
    def validate_url_with_confidence(self, url):
        """
        智能验证URL，返回置信度和原因
        
        Returns:
            dict: {
                'confidence': 'high'|'medium'|'low'|'invalid',
                'reason': '原因说明'
            }
        """
        import re
        from urllib.parse import urlparse, parse_qs
        
        url = url.strip()
        
        # 基本格式检查
        if not url:
            return {'confidence': 'invalid', 'reason': '链接为空'}
        
        if not url.startswith(('http://', 'https://')):
            return {'confidence': 'invalid', 'reason': '链接必须以http://或https://开头'}
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return {'confidence': 'invalid', 'reason': '链接格式不正确'}
        except Exception:
            return {'confidence': 'invalid', 'reason': '链接格式不正确'}
        
        url_lower = url.lower()
        
        # 高置信度：标准微信文章链接
        high_confidence_patterns = [
            r'https?://mp\.weixin\.qq\.com/s/',
            r'https?://mp\.weixin\.qq\.com/s\?'
        ]
        
        for pattern in high_confidence_patterns:
            if re.search(pattern, url_lower):
                return {'confidence': 'high', 'reason': '标准微信文章链接'}
        
        # 中等置信度：包含微信特有参数
        wechat_params = ['__biz', 'sn', 'mid', 'idx']
        has_wechat_params = any(param in url_lower for param in wechat_params)
        
        if has_wechat_params:
            return {'confidence': 'high', 'reason': '包含微信文章参数'}
        
        # 中等置信度：微信相关域名
        wechat_domains = [
            'weixin.qq.com',
            'wx.qq.com',
            'mp.weixin.qq.com'
        ]
        
        parsed_url = urlparse(url_lower)
        domain = parsed_url.netloc
        
        for wechat_domain in wechat_domains:
            if wechat_domain in domain:
                return {'confidence': 'medium', 'reason': '微信相关域名'}
        
        # 低置信度：其他HTTP链接
        if url_lower.startswith(('http://', 'https://')):
            return {'confidence': 'low', 'reason': '非微信域名，但可能是有效链接'}
        
        return {'confidence': 'invalid', 'reason': '不是有效的网页链接'}
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_working:
            result = messagebox.askyesno("确认", "正在采集中，确定要退出吗？")
            if not result:
                return
            
            self.is_working = False
        
        self.root.destroy()
    
    def run(self):
        """运行GUI应用"""
        self.root.mainloop()


def main():
    """主函数"""
    app = WeChatArticleCollectorGUI()
    app.run()


if __name__ == "__main__":
    main()
