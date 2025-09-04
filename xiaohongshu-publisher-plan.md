# 小红书发布工具开发计划书

## 项目概述
基于Python的小红书自动化发布工具，通过浏览器模拟实现内容自动发布，支持图片/视频上传、定时发布、批量操作等功能。

## 技术架构

### 核心技术栈
- **浏览器自动化**: Playwright (优于Selenium，更稳定，反检测能力强)
- **配置管理**: YAML + Python Dataclasses
- **任务调度**: APScheduler (支持Cron表达式)
- **数据存储**: SQLite + JSON (轻量级，易于部署)
- **日志系统**: Loguru (结构化日志，自动轮转)
- **图片处理**: Pillow (图片压缩、格式转换)

### 运行环境要求
- Python 3.8+
- Chromium浏览器 (Playwright自动安装)
- 2GB+ 可用内存
- 网络连接 (用于浏览器操作)

## 项目结构

```
xiaohongshu-publisher/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── main.py                  # 主程序入口
│   ├── config/                  # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py          # 配置加载与验证
│   │   ├── accounts.example.yml # 账号配置模板
│   │   └── rules.example.yml    # 发布规则模板
│   ├── browser/                 # 浏览器相关
│   │   ├── __init__.py
│   │   ├── browser_manager.py   # 浏览器生命周期管理
│   │   ├── auth_handler.py      # 登录认证处理
│   │   └── stealth.py          # 反检测配置
│   ├── publisher/               # 发布核心逻辑
│   │   ├── __init__.py
│   │   ├── content_uploader.py  # 图片/视频上传
│   │   ├── post_creator.py      # 帖子创建流程
│   │   ├── scheduler.py         # 定时发布调度
│   │   └── queue_manager.py     # 发布队列管理
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py           # 日志配置
│   │   ├── image_processor.py  # 图片处理工具
│   │   ├── retry_handler.py    # 重试机制
│   │   └── notification.py     # 通知功能
│   └── models/                  # 数据模型
│       ├── __init__.py
│       ├── post.py             # 帖子数据模型
│       └── account.py          # 账号信息模型
├── data/                       # 数据目录
│   ├── uploads/               # 待发布内容
│   │   ├── images/           # 图片文件
│   │   └── videos/           # 视频文件
│   ├── logs/                 # 日志文件
│   └── db/                   # SQLite数据库
├── tests/                    # 测试代码
│   ├── __init__.py
│   ├── test_browser.py       # 浏览器测试
│   ├── test_publisher.py     # 发布功能测试
│   └── test_scheduler.py     # 调度器测试
├── requirements.txt          # 依赖列表
├── README.md                # 项目说明
├── .gitignore              # Git忽略规则
└── docker-compose.yml      # Docker部署配置
```

## 功能模块详解

### 1. 配置系统 (config/settings.py)

#### 配置结构
```yaml
# accounts.yml
accounts:
  - name: "主账号"
    username: "your_username"
    password: "your_password"  # 可选，优先使用cookies
    cookies_file: "cookies.json"
    user_agent: "Mozilla/5.0..."
    proxy: null  # 可选代理配置

# rules.yml
publish_rules:
  default_delay: 30  # 默认延迟(秒)
  max_retry: 3
  image_quality: 85
  concurrent_posts: 1
  time_slots:  # 可发布时间段
    - start: "09:00"
      end: "22:00"
```

### 2. 浏览器管理 (browser/browser_manager.py)

#### 核心功能
- 浏览器实例生命周期管理
- 反检测配置(stealth插件)
- 代理支持
- 用户代理模拟
- 会话持久化

#### 反检测措施
- 禁用webdriver属性
- 修改navigator属性
- 随机化视窗大小
- 模拟人类操作延迟
- 禁用自动化标志

### 3. 认证系统 (browser/auth_handler.py)

#### 登录方式优先级
1. **Cookie登录** (优先)
   - 从文件加载cookies
   - 验证cookies有效性
   - 失效时自动更新

2. **二维码登录** (备选)
   - 生成登录二维码
   - 手机扫码确认
   - 保存cookies到文件

3. **账号密码登录** (最后选择)
   - 需要验证码处理
   - 风险较高，慎用

### 4. 内容上传 (publisher/content_uploader.py)

#### 支持的文件类型
- **图片**: JPG, PNG, WebP (最大20MB)
- **视频**: MP4, MOV (最大500MB)

#### 图片处理功能
- 自动压缩到合适尺寸
- 格式转换 (WebP优化)
- EXIF信息清理
- 质量调整

#### 上传流程
1. 检查文件完整性
2. 图片预处理(压缩、格式转换)
3. 分片上传(大文件)
4. 上传进度监控
5. 失败重试机制

### 5. 帖子创建 (publisher/post_creator.py)

#### 发布流程
```python
1. 点击发布按钮
2. 选择上传方式(图片/视频)
3. 批量上传文件
4. 等待文件处理完成
5. 填写标题和正文
6. 添加标签和话题
7. 选择发布位置
8. 最终发布确认
```

#### 内容规范
- **标题**: 最多20个字符
- **正文**: 最多1000个字符
- **标签**: 最多10个，每个最多20字符
- **图片**: 最多9张，推荐3:4比例
- **视频**: 时长5分钟以内

### 6. 定时调度 (publisher/scheduler.py)

#### 调度功能
- **Cron表达式**: 支持复杂时间规则
- **队列管理**: 先进先出队列
- **并发控制**: 限制同时发布数量
- **失败重试**: 指数退避重试
- **时间窗口**: 限制可发布时间

#### 使用示例
```python
scheduler = PostScheduler()
scheduler.add_job(
    post_data,
    trigger='cron',
    hour='9-22',
    minute='*/30'  # 每30分钟检查一次
)
```

### 7. 监控告警 (utils/notification.py)

#### 通知方式
- **控制台日志**: 实时输出
- **文件日志**: 详细记录
- **邮件通知**: 关键事件
- **Webhook**: 自定义通知

#### 监控指标
- 发布成功率
- 平均发布时间
- 错误类型统计
- 账号状态监控

## 安装与部署

### 1. 开发环境搭建
```bash
# 克隆项目
git clone <repository-url>
cd xiaohongshu-publisher

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装浏览器
playwright install chromium

# 复制配置模板
cp config/accounts.example.yml config/accounts.yml
cp config/rules.example.yml config/rules.yml

# 编辑配置文件
# 填写账号信息、发布规则等
```

### 2. Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

COPY . .

CMD ["python", "src/main.py"]
```

### 3. 系统服务
```bash
# 创建systemd服务
sudo cp deploy/xiaohongshu-publisher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable xiaohongshu-publisher
sudo systemctl start xiaohongshu-publisher
```

## 使用方法

### 1. 基础使用
```python
from src.main import XiaohongshuPublisher

publisher = XiaohongshuPublisher()
publisher.publish({
    'title': '测试帖子',
    'content': '这是一个自动发布的测试内容',
    'images': ['path/to/image1.jpg', 'path/to/image2.jpg'],
    'tags': ['测试', '自动化']
})
```

### 2. 批量发布
```python
posts = [
    {
        'title': '帖子1',
        'content': '内容1',
        'images': ['img1.jpg'],
        'schedule_at': '2024-01-01 10:00:00'
    },
    {
        'title': '帖子2',
        'content': '内容2',
        'images': ['img2.jpg'],
        'schedule_at': '2024-01-01 14:00:00'
    }
]

publisher.batch_publish(posts)
```

### 3. 命令行使用
```bash
# 发布单个帖子
python src/main.py publish --title "测试" --content "内容" --images img1.jpg

# 批量发布
python src/main.py batch --config posts.json

# 查看发布状态
python src/main.py status

# 查看日志
python src/main.py logs --tail 100
```

## 安全考虑

### 1. 账号安全
- **Cookie优先**: 避免频繁密码登录
- **随机延迟**: 模拟人类操作节奏
- **并发限制**: 避免过于频繁的操作
- **异常处理**: 及时捕获并处理错误

### 2. 反检测措施
- **浏览器指纹**: 模拟真实浏览器环境
- **操作延迟**: 随机化点击和输入间隔
- **鼠标轨迹**: 模拟真实鼠标移动
- **滚动行为**: 自然滚动模式

### 3. 数据安全
- **敏感信息加密**: 密码、Cookie等加密存储
- **日志脱敏**: 避免记录敏感信息
- **文件权限**: 限制配置文件的访问权限

## 测试策略

### 1. 单元测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_publisher.py -v

# 覆盖率报告
pytest --cov=src tests/
```

### 2. 集成测试
- 浏览器启动测试
- 登录流程测试
- 图片上传测试
- 发布流程测试

### 3. 性能测试
- 内存使用监控
- 并发性能测试
- 长时间运行稳定性

## 错误处理与调试

### 1. 常见错误
- **元素定位失败**: 页面结构变化
- **网络超时**: 网络不稳定
- **登录失效**: Cookie过期
- **文件上传失败**: 文件格式或大小问题

### 2. 调试工具
- **截图功能**: 失败时自动截图
- **日志级别**: DEBUG模式详细记录
- **回放功能**: 重现操作过程
- **调试模式**: 非headless模式便于观察

### 3. 故障恢复
- **自动重试**: 失败后自动重试
- **断点续传**: 从中断处继续
- **状态持久化**: 保存当前进度
- **清理机制**: 异常退出时清理资源

## 扩展功能规划

### 1. 多账号管理
- 账号轮换发布
- 账号状态监控
- 权重分配策略

### 2. 内容分析
- 热门话题推荐
- 最佳发布时间分析
- 互动数据统计

### 3. API接口
- RESTful API
- WebSocket实时通信
- 第三方集成支持

### 4. Web管理界面
- 可视化配置
- 实时监控面板
- 一键发布操作

## 维护与更新

### 1. 版本管理
- 语义化版本号
- 变更日志记录
- 向后兼容性

### 2. 更新策略
- 自动检测更新
- 热更新支持
- 回滚机制

### 3. 社区支持
- 问题反馈渠道
- 文档持续更新
- 最佳实践分享

## 许可证

本项目采用MIT许可证，允许商业使用、修改和分发。

---

**文档版本**: v1.0  
**最后更新**: 2024-01-01  
**维护者**: 项目开发团队