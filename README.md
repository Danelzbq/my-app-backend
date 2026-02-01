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
└── setup.bat        # 环境设置
```

## 部署注意事项

1. 生产环境建议使用 PostgreSQL/MySQL
2. 修改 CORS 配置限制访问源
3. 使用环境变量管理敏感配置
4. 考虑使用 Gunicorn/Nginx 反向代理
