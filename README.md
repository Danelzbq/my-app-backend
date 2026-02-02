# Blog API

FastAPI 后端服务 - 博客管理系统

## 快速开始

### 1. 环境设置
双击运行 `setup.bat` 自动配置环境

或手动执行：
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 启动服务
双击运行 `start.bat` 启动服务器

或手动执行：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问 API
- API 文档: http://localhost:8000/docs
- 备用文档: http://localhost:8000/redoc

## 核心功能

- ✅ 用户注册/登录（bcrypt 加密）
- ✅ 帖子管理（增删改查）
- ✅ 收藏功能
- ✅ 浏览历史

## 技术栈

- FastAPI + SQLAlchemy + SQLite
- Pydantic 数据验证
- Passlib 密码加密

## 项目结构

```
backend/
├── main.py          # API 路由
├── database.py      # 数据库配置
├── models.py        # 数据模型
├── schemas.py       # 数据验证
├── auth.py          # 认证工具
├── requirements.txt # 依赖列表
├── start.bat        # 启动脚本
├── setup.bat        # 环境设置
├── check_database.py  # 数据库结构检查
└── reset_database.py  # 数据库重置脚本
```

## 数据库管理

### 检查数据库结构
如果发布功能失败，首先检查数据库结构是否正确：
```bash
python check_database.py
```

### 重置数据库（谨慎使用）
当数据库结构与模型不匹配时，需要重置数据库：
```bash
python reset_database.py
```
⚠️ **警告**：此操作会删除所有数据！脚本会自动创建备份。

### 常见问题
- **发布失败（500错误）**：通常是数据库表结构过期，运行 `check_database.py` 诊断
- **缺少字段**：运行 `reset_database.py` 重建数据库表

## 部署注意事项

### 部署到服务器步骤
1. 拉取最新代码：`git pull`
2. 安装/更新依赖：`pip install -r requirements.txt`
3. **检查数据库结构**：`python check_database.py`
4. **如需重置**：`python reset_database.py`（会自动备份）
5. 重启服务

### 生产环境建议
1. 使用 PostgreSQL/MySQL（通过 DATABASE_URL 环境变量配置）
2. 修改 CORS 配置限制访问源
3. 使用环境变量管理敏感配置
4. 使用 Gunicorn/Nginx 反向代理
