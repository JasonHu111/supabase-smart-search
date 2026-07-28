# Supabase 语义搜索组件

基于 Supabase Edge Functions 和 pgvector 的语义搜索组件，使用内置 AI 模型 gte-small。

## 项目特点：

### 使用AI模型给数据进行向量赋予，在模糊搜索和同义词联想词方面表达良好

![演示](supabase-search/preview.gif)

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Supabase Edge Functions (TypeScript) |
| 数据库 | PostgreSQL + pgvector |
| AI 模型 | gte-small (Supabase 内置) |
| 前端 | Vue 3 + TypeScript + Vite |

## 项目结构

```text
supabase-search/
├── backend/
│ └── supabase/
│ ├── config.toml
│ ├── functions/
│ │ ├── search/
│ │ └── generate-embedding/
│ └── migrations/
├── frontend/
│ ├── src/
│ │ ├── App.vue
│ │ └── main.ts
│ ├── package.json
│ └── vite.config.ts
├── scripts/
├── .gitignore
└── README.md
```


## 快速开始

需要拥有supabase账号并登录，在supabase中创建项目

### 1. 配置 Supabase

修改 `backend/supabase/config.toml` 中的项目 ID


### 2.配置环境变量

## 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `VITE_SUPABASE_URL` | Supabase 项目 URL,项目id在project-setting/general | `https://项目id.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase 密钥，在project-setting/API-key | `sb_publishable_xxx` |
| `VITE_EXAMPLE_TAGS` | 快捷搜索标签（逗号分隔） | `内容1，内容2` |

创建 frontend/.env.local

```bash
VITE_SUPABASE_URL=https://你的项目id.supabase.co
VITE_SUPABASE_ANON_KEY=你的publish_key
```

（可选）在.env.local里配置快捷搜索词
```bash
VITE_EXAMPLE_TAGS=内容1,内容2,内容3,内容4,内容5
```



### 3. 创建数据库表

在 Supabase SQL Editor 中执行 `backend/supabase/migrations/001_initial.sql`


### 4. 部署 Edge Functions

```bash
cd backend
supabase login
supabase link --project-ref 你的项目ID
supabase functions deploy search --no-verify-jwt
supabase functions deploy generate-embedding --no-verify-jwt
```

### 5. 添加测试数据

```sql
insert into embeddings (content) values 
   ('内容1'),
   ('内容2'),
   ('内容3'),
   ('内容4'),
   ('内容5');
```

### 6. 生成向量

依赖
```bash 
pip install requests python-dotenv
```
运行脚本

```bash
python scripts/generate_vectors.py
```


### 7. 启动前端开发服务器

```bash
cd frontend
npm install
npm run dev
```

访问http://localhost:5137






