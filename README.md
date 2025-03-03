# Google Scholar 引用信息爬虫 🔍

这是一个强大的 Google Scholar 文献引用信息爬取工具。它能自动收集学者的所有论文信息及其引用情况，支持断点续爬，并能智能处理验证码，是科研工作者的得力助手！

## 项目结构

```
Google-Scholar/
├── Google_scholar.py   # 主程序文件
├── requirements.txt    # 项目依赖
├── author_information.txt     # 文献引用信息（运行结束后生成）
└── README.md          # 项目说明文件
```

## 功能特点 ✨

- 🤖 自动获取学者的所有论文信息
- 📊 智能收集每篇论文的引用次数
- 📚 获取引用文章的详细信息（标题、作者、期刊等）
- 🛡️ 自动处理 Google reCAPTCHA 验证
- 🎯 自动管理 WebDriver，无需手动配置
- 💾 将结果保存为易读的文本格式

## 工作原理 🔧

本项目使用以下技术实现自动化爬取：

1. **Selenium WebDriver**
   - 模拟真实浏览器行为
   - 自动处理动态加载内容
   - 智能等待页面元素

2. **腾讯云语音识别**
   - 自动识别验证码音频
   - 突破 reCAPTCHA 限制

3. **智能化设计**
   - 自动管理浏览器驱动
   - 随机延时避免反爬
   - 异常自动处理和恢复

## 快速开始 🚀

1. 克隆项目并安装依赖：
```bash
git clone https://github.com/onef1shy/Google-Scholar.git
cd Google-Scholar
pip install -r requirements.txt
```

2. 配置腾讯云 API：
   - 注册腾讯云账号并开通语音识别服务
   - 获取 SecretId 和 SecretKey
   - 在 `Google_scholar.py` 中填写您的密钥：
```python
self.SecretId = "您的SecretId"
self.SecretKey = "您的SecretKey"
```

3. 运行程序：
```bash
python Google_scholar.py
```

4. 输入目标学者主页 URL：
```
https://scholar.google.com/citations?user=XXXXXXXXXXXXXXXX
```

## 系统要求 💻

- Python 3.9+
- Google Chrome 浏览器
- 稳定的网络连接
- 腾讯云账号（用于语音识别服务）

## 输出说明 📝

程序会生成一个以学者名字命名的文本文件（`作者名_Information.txt`），包含以下信息：

- 📄 论文标题
- 📈 引用次数
- 📚 引用文章的详细信息
  - 标题
  - 作者
  - 发表期刊/会议
  - 文章链接

## 使用技巧 💡

1. **避免验证码**
   - 合理控制爬取频率
   - 建议使用代理服务器
   - 确保腾讯云 API 配置正确

2. **断点续爬**
   - 程序中断会自动保存进度
   - 重启时可选择继续上次任务
   - 完成后自动清理断点文件

3. **数据导出**
   - 结果保存为易读的文本格式
   - 支持后续数据分析和处理
   - 可方便地导入到其他工具中

## 常见问题 ❓

1. **验证码处理**
   - 程序会自动处理 Google reCAPTCHA
   - 确保已正确配置腾讯云 API
   - 如果频繁遇到验证码，建议降低爬取频率

2. **网络问题**
   - 确保能够正常访问 Google Scholar
   - 考虑使用代理服务器（需要额外配置）
   - 检查网络连接稳定性

## 注意事项 ⚠️

- 遵守 Google Scholar 的使用条款
- 合理控制爬取频率，避免 IP 被封
- 定期检查腾讯云 API 额度
- 建议使用代理服务器轮换 IP

## License 📄

MIT License © [onefishy](https://github.com/onef1shy)

## 支持

欢迎 Fork 和 Star ⭐，也欢迎提出建议和 PR～

---

> 🤖 如果你基于这个项目做出了有趣的改进，别忘了分享给我，让我们一起提升技术～