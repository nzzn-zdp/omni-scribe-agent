### 任务9：部署配置

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `config/settings.yaml`
- Create: `config/platforms.yaml`
- Create: `.env.example`
- Create: `README.md`

**Interfaces:**
- Consumes: 所有模块
- Produces: 可部署的Docker镜像

- [ ] **步骤1：完善Docker配置**

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/db/omniscribe.db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  redis_data:
```

- [ ] **步骤2：创建环境变量示例**

```bash
# .env.example
# 应用配置
APP_NAME=OmniScribeAgent
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/db/omniscribe.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# LLM配置
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key

# 微信公众号配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# 微博配置
WEIBO_ACCESS_TOKEN=your_weibo_access_token

# 知乎配置
ZHIHU_CLIENT_ID=your_zhihu_client_id
ZHIHU_CLIENT_SECRET=your_zhihu_client_secret
```

- [ ] **步骤3：创建配置文件示例**

```yaml
# config/settings.yaml
app:
  name: OmniScribeAgent
  version: 1.0.0
  debug: false

database:
  url: sqlite+aiosqlite:///./data/db/omniscribe.db

redis:
  url: redis://localhost:6379/0

llm:
  providers:
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4
      max_tokens: 4096
    claude:
      api_key: ${CLAUDE_API_KEY}
      model: claude-3-opus-20240229
      max_tokens: 4096

hotspot:
  check_interval: 300
  min_score: 0.6

publish:
  retry_count: 3
  retry_delay: 60
```

```yaml
# config/platforms.yaml
wechat:
  app_id: ${WECHAT_APP_ID}
  app_secret: ${WECHAT_APP_SECRET}
  thumb_media_id: ""

weibo:
  access_token: ${WEIBO_ACCESS_TOKEN}

zhihu:
  client_id: ${ZHIHU_CLIENT_ID}
  client_secret: ${ZHIHU_CLIENT_SECRET}

xiaohongshu:
  # 小红书配置
  cookie: ""

wordpress:
  url: ""
  username: ""
  password: ""
```

- [ ] **步骤4：创建部署文档**

```markdown
# 部署指南

## 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+

## 部署步骤

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

## 配置说明

### 热点源配置
在管理界面的"热点监控"页面添加热点源。

### 平台配置
在管理界面的"系统设置"页面配置各平台账号信息。

### LLM配置
在 .env 文件中配置各LLM服务的API密钥。
```

- [ ] **步骤5：提交部署配置代码**

```bash
git add docker-compose.yml Dockerfile config/ .env.example README.md
git commit -m "feat: 添加部署配置"
```