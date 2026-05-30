# AI 互动学习闯关小程序

将学习文本自动转化为「上传 → AI 出题 → 闯关答题 → 学习报告」的完整闭环。

## 项目结构

```
w-ai-learn/
├── backend/     # FastAPI + LangChain + DeepSeek
├── frontend/    # Taro 4 + React + TypeScript 微信小程序
├── docs/        # 需求与设计文档
└── prototypes/  # UI 原型
```

## 环境要求

- Node.js >= 16.20（推荐 18+）
- Python 3.11+
- 微信开发者工具

## 后端启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # 填入 DEEPSEEK_API_KEY，勿提交 .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

运行测试（TDD）：

```bash
cd backend
pytest -v
```

API 文档：http://127.0.0.1:8000/docs

## 前端启动

参考 [Taro 安装及使用](https://docs.taro.zone/docs/GETTING-STARTED)：

```bash
cd frontend
npm install          # 推荐 npm，与文档一致
npm run dev:weapp
```

若使用 **pnpm** 且出现 `ERR_PNPM_IGNORED_BUILDS`，需允许 Taro 相关包执行安装脚本：

```bash
cd frontend
pnpm install
# 已在 package.json 配置 pnpm.onlyBuiltDependencies；若仍报错则执行：
pnpm approve-builds
pnpm run dev:weapp
```

用微信开发者工具打开 `frontend` 目录（编译产物在 `dist/`）。

漫画风字体已打包在 `frontend/src/assets/fonts/`（构建后位于 `dist/assets/fonts/`）。微信开发者工具请打开 **`frontend` 目录**（`miniprogramRoot` 指向 `dist/`），并在 `project.config.json` 的 `packOptions.include` 中包含字体目录。字体加载失败时会自动回退到 PingFang，不影响页面显示。

开发者工具设置建议：

- 关闭「ES6 转 ES5」
- 关闭「上传时样式自动补全」
- 开发阶段勾选「不校验合法域名」，以便访问 `http://127.0.0.1:8000`

## V1 功能范围

- 欢迎闪屏 → 文本输入 → AI 生成题目 → 逐题闯关 → 学习报告
- 单选题 + 判断题
- 匿名会话（内存存储，无登录/无持久化历史）
- TabBar：闯关 / 题库(P1 占位) / 我的(P1 占位)

## 安全说明

**切勿将 `backend/.env` 或 API Key 提交到 Git。** 仓库已通过 `.gitignore` 忽略 `.env` 文件。

## 数据库初始化（用户系统）

用户系统使用 **MySQL 8**。首次初始化：

```bash
# 方式一：Docker 启动 MySQL（项目根目录）
docker compose up -d mysql

# 安装依赖并初始化（backend 目录）
cd backend
pip install -r requirements.txt
cp .env.example .env   # 按需修改 DATABASE_URL / MYSQL_*
python scripts/init_database.py
```

也可手动执行纯 SQL：`mysql -u root -p < backend/scripts/schema.sql`（不含 Alembic 版本记录）。

迁移管理：

```bash
cd backend
alembic upgrade head    # 升级到最新
alembic downgrade -1    # 回退一步
```
