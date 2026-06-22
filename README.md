# OmniScribeAgent

端到端自动化内容生产与分发Agent系统

## 功能特性

- 热点监控：自动抓取和分析热点话题
- 智能写作：基于AI的内容生成
- 多平台发布：一键发布到多个平台

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+

## 快速开始

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入配置

# 启动应用
uvicorn src.main:app --reload
```

### Docker部署

1. 克隆代码
```bash
git clone <repository-url>
cd omni-scribe-agent
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入配置
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 应用地址: http://localhost:8000
- 管理界面: http://localhost

5. 查看日志
```bash
docker-compose logs -f
```

6. 停止服务
```bash
docker-compose down
```

## 项目结构

```
├── config/              # 配置文件
│   ├── settings.yaml    # 应用配置
│   └── platforms.yaml   # 平台配置
├── src/
│   ├── main.py          # 应用入口
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接
│   ├── api/             # API路由
│   ├── models/          # 数据模型
│   ├── core/            # 核心业务逻辑
│   ├── hotspot/         # 热点监控模块
│   ├── content/         # 内容生产模块
│   └── publish/         # 发布模块
├── data/                # 数据存储
├── Dockerfile           # Docker镜像配置
├── docker-compose.yml   # Docker Compose配置
└── requirements.txt     # Python依赖
```

## 配置说明

### 环境变量

配置通过环境变量或`.env`文件管理：

```bash
cp .env.example .env
# 编辑.env文件配置API密钥等
```

主要配置项：
- `DATABASE_URL`: 数据库连接地址
- `REDIS_URL`: Redis连接地址
- `OPENAI_API_KEY`: OpenAI API密钥
- `CLAUDE_API_KEY`: Claude API密钥

### 热点源配置
在管理界面的"热点监控"页面添加热点源。

### 平台配置
在管理界面的"系统设置"页面配置各平台账号信息，或直接编辑 `config/platforms.yaml`。

### LLM配置
在 `.env` 文件中配置各LLM服务的API密钥。

## 开发

```bash
# 运行测试
pytest tests/ -v

# 代码检查
flake8 src/
```

## 许可证

MIT
