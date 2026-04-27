# 血压记录系统

一个简单的血压记录和统计分析 Web 应用，使用 FastAPI + Supabase 构建。

## 功能

- 每日三次血压记录（早晨、中午、晚上）
- 记录收缩压、舒张压、脉搏
- 历史记录查看、编辑、删除
- 统计分析（平均值、最大最小值、时段统计）
- 趋势图表展示

## 技术栈

- **后端**: FastAPI (Python)
- **数据库**: Supabase (PostgreSQL)
- **前端**: Bootstrap 5 + Chart.js
- **部署**: Render

## 本地开发

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入 Supabase 配置：

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. 初始化数据库

在 Supabase 控制台的 SQL Editor 中执行 `init_db.sql` 中的 SQL 语句。

### 4. 运行应用

```bash
uvicorn main:app --reload
```

访问 http://localhost:8000

## 部署到 Render

### 方法一：使用 render.yaml

1. 将代码推送到 GitHub
2. 在 Render 中创建新的 Blueprint，连接 GitHub 仓库
3. 在 Render 环境变量中设置 `SUPABASE_URL` 和 `SUPABASE_KEY`

### 方法二：手动创建

1. 在 Render 创建新的 Web Service
2. 连接 GitHub 仓库
3. 设置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 添加环境变量 `SUPABASE_URL` 和 `SUPABASE_KEY`

## 获取 Supabase 配置

1. 登录 https://supabase.com/
2. 创建新项目或选择已有项目
3. 进入 Settings > API
4. 复制：
   - Project URL → `SUPABASE_URL`
   - anon public key → `SUPABASE_KEY`

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/records | 获取记录列表 |
| POST | /api/records | 创建记录 |
| GET | /api/records/{id} | 获取单条记录 |
| PUT | /api/records/{id} | 更新记录 |
| DELETE | /api/records/{id} | 删除记录 |
| GET | /api/statistics | 获取统计数据 |
| GET | /api/trend | 获取趋势数据 |
