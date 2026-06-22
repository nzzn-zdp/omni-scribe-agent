# OmniScribeAgent

端到端自动化内容生产与分发Agent系统

## 功能特性

- 热点监控：自动抓取和分析热点话题
- 智能写作：基于AI的内容生成
- 多平台发布：一键发布到多个平台

## 快速开始

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
uvicorn src.main:app --reload
```

### Docker部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 项目结构

```
src/
├── main.py          # 应用入口
├── config.py        # 配置管理
├── database.py      # 数据库连接
├── api/             # API路由
├── models/          # 数据模型
├── core/            # 核心业务逻辑
├── hotspot/         # 热点监控模块
├── content/         # 内容生产模块
└── publish/         # 发布模块
```

## 配置

配置通过环境变量或`.env`文件管理：

```bash
cp .env.example .env
# 编辑.env文件配置API密钥等
```

## 开发

```bash
# 运行测试
pytest tests/ -v

# 代码检查
flake8 src/
```

## 许可证

MIT