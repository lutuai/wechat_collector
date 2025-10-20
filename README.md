# 微信文章采集器 (WeChatScribe)

**WeChatScribe** - 一个优雅的微信公众号文章采集和转换工具

一个简单易用的微信公众号文章采集工具，支持将公众号文章转换为Markdown格式并保存到本地。

## 功能特点

- 🔗 通过文章链接直接采集
- 📝 自动转换为Markdown格式
- 🖼️ 自动下载文章图片到本地
- 💾 保存到指定目录
- 🖥️ 友好的桌面GUI界面

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 在界面中输入微信公众号文章链接

3. 选择保存目录

4. 点击"开始采集"按钮

5. 等待采集完成，文章将保存为Markdown文件

## 输出格式

采集的文章将保存在指定目录下：
```
output/
├── article_title.md        # 文章Markdown文件
└── images/                 # 文章图片目录
    ├── image1.jpg
    └── image2.jpg
```

## 注意事项

- 确保网络连接正常
- 某些文章可能因为微信的访问限制而无法采集
- 建议使用Chrome浏览器打开文章后复制链接

## 技术栈

- Python 3.x
- tkinter (GUI)
- requests (HTTP请求)
- BeautifulSoup4 (HTML解析)
- html2text (Markdown转换)
- Pillow (图片处理)

## 许可证

MIT License

