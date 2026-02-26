# CalEE - 饮食热量追踪应用

一款功能完整、设计精美的饮食热量追踪应用，支持食物图片上传和 AI 图像识别分析卡路里。

## 功能特点

- 📊 **仪表板** - 圆形进度条显示每日热量摄入，宏量营养素统计
- 🔍 **食物搜索** - 实时搜索，支持分类筛选
- 📸 **图像识别** - 拍照上传，AI 自动识别食物和卡路里
- 🍽️ **餐食记录** - 支持早餐、午餐、晚餐、零食分类记录
- 📈 **进度统计** - 查看历史记录和趋势分析
- 📱 **响应式设计** - 兼容手机和电脑端

## 技术栈

- **后端**: Python + FastAPI (Async)
- **前端**: HTMX + Alpine.js + Tailwind CSS
- **数据库**: SQLite (可升级为 PostgreSQL)
- **图像识别**: 阿里云 Qwen3-VL-Plus API
- **部署**: Vercel / 阿里云函数计算

## 快速开始

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd calee
```

2. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

3. **配置环境变量**

创建 `.env` 文件：
```env
DATABASE_URL=sqlite+aiosqlite:///./calee.db
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DAILY_CALORIE_GOAL=1200
ALLOW_ORIGINS=*
MAX_UPLOAD_SIZE=5242880
UPLOAD_DIR=./uploads
```

4. **运行应用**
```bash
cd backend
python -m app.main
```

访问 http://localhost:8000

### Vercel 部署

1. **Fork 项目到 GitHub**

2. **连接 Vercel**
   - 登录 [Vercel](https://vercel.com)
   - 点击 "New Project"
   - 导入 GitHub 仓库

3. **配置环境变量**
   在 Vercel 项目设置中添加：
   - `DATABASE_URL`: 数据库连接字符串（可使用 Vercel Postgres）
   - `DASHSCOPE_API_KEY`: 阿里云 API Key
   - `DASHSCOPE_API_URL`: https://dashscope.aliyuncs.com/compatible-mode/v1

4. **部署**
   - 点击 "Deploy"
   - 等待部署完成

## 项目结构

```
calee/
├── backend/
│   └── app/
│       ├── main.py           # FastAPI 应用入口
│       ├── config.py         # 配置管理
│       ├── database.py       # 数据库连接
│       ├── models/           # SQLAlchemy 模型
│       ├── schemas/          # Pydantic Schema
│       ├── api/              # API 路由
│       ├── services/         # 业务逻辑服务
│       └── seeds/            # 数据库种子数据
├── frontend/
│   ├── templates/            # Jinja2 模板
│   └── static/               # 静态文件
├── uploads/                  # 上传的图片
├── .env                      # 环境变量
├── vercel.json              # Vercel 配置
└── README.md                # 项目说明
```

## API 端点

### 食物
- `GET /api/v1/foods` - 获取食物列表
- `GET /api/v1/foods/:id` - 获取食物详情
- `POST /api/v1/foods` - 创建自定义食物

### 餐食记录
- `GET /api/v1/meals` - 获取餐食记录
- `POST /api/v1/meals` - 添加餐食记录
- `DELETE /api/v1/meals/:id` - 删除餐食记录

### 仪表板
- `GET /api/v1/dashboard/summary` - 获取每日摘要
- `POST /api/v1/dashboard/goals/update` - 更新热量目标

### 图片上传
- `POST /api/v1/upload/recognize` - 上传图片并识别食物

## 开发指南

### 添加新的食物分类

在 `backend/app/seeds/__init__.py` 的 `CHINESE_FOODS` 列表中添加食物数据。

### 自定义样式

编辑 `frontend/templates/base.html` 中的 Tailwind 配置或 `frontend/static/css/styles.css`。

### 数据库迁移

当前使用 SQLite，如需升级到 PostgreSQL：

1. 修改 `.env` 中的 `DATABASE_URL`
2. 无需修改代码，SQLAlchemy 自动适配

## 许可证

MIT License
