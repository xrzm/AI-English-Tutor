# AI English Tutor

基于 AI 的英语教学系统，支持**口语陪练**（语音对话 + 语法纠错 + 评分）和**作业批改**（OCR 识别 + AI 打分 + 错误分析），使用 FastAPI + DashScope（通义千问）构建。

## 功能特性

### 口语陪练
- 与 AI 老师进行实时英语对话
- 语音输入（浏览器录音 → 服务端语音转文字）
- AI 语音回复（浏览器内置 TTS 朗读）
- 每条消息自动语法分析（错误识别 + 改进建议 + 优化版本）
- 三个难度等级：初级 / 中级 / 高级
- 对话历史持久化存储
- 支持打字输入和语音输入两种方式

### 作业批改
- AI 批改英语作文，0~100 分评分
- 图片 OCR 识别（拍照上传，自动提取文字）
- 错误逐条定位 + 修正建议
- 优点分析 + 改进建议 + 参考范文
- 输入校验（防乱输入、字数检测、非英文字符拦截）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.12+ / FastAPI |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| AI 模型 | 阿里云 DashScope（Qwen-Plus / Qwen-Audio-Turbo） |
| 语音 | ffmpeg 音频转码 + 浏览器 SpeechSynthesis TTS |
| 前端 | 原生 HTML/CSS/JS，单页应用 |
| 部署 | Gunicorn + Uvicorn + Nginx + systemd |

## 项目结构

```
AI-English-Tutor/
├── app/
│   ├── main.py                  # FastAPI 应用入口，根路径返回前端页面
│   ├── api/v1/
│   │   ├── router.py            # API 路由汇总
│   │   └── endpoints/
│   │       ├── health.py        # 健康检查 GET /api/v1/health
│   │       ├── homework.py      # 作业批改：OCR + 评分
│   │       └── speaking.py      # 口语陪练：STT + TTS + 对话 + 分析
│   ├── core/
│   │   ├── config.py            # 配置管理（从 .env 读取）
│   │   ├── exceptions.py        # 自定义异常
│   │   └── logging.py           # 日志配置
│   ├── db/
│   │   ├── session.py           # SQLAlchemy 引擎 & 会话
│   │   ├── dependencies.py      # FastAPI 依赖注入
│   │   └── base.py              # 模型导入
│   ├── models/
│   │   ├── homework_record.py   # 作业批改记录表
│   │   └── speaking_session.py  # 口语对话会话表
│   ├── schemas/
│   │   ├── common.py            # 通用 ApiResponse 包装
│   │   ├── homework.py          # 作业相关请求/响应模型
│   │   └── speaking.py          # 口语相关请求/响应模型
│   ├── services/
│   │   ├── homework_service.py  # 作业批改业务逻辑
│   │   ├── qwen_clients.py      # DashScope API 封装
│   │   └── speaking_service.py  # 口语陪练业务逻辑
│   ├── utils/
│   │   ├── audio.py             # ffmpeg 音频格式转换
│   │   ├── homework_grader.py   # AI 作业批改链
│   │   └── speaking_partner.py  # AI 口语对话 & 语法分析
│   └── static/
│       └── index.html           # 前端单页应用
├── scripts/
│   └── init_db.py               # 数据库初始化脚本
├── gunicorn.conf.py             # Gunicorn 生产配置
├── nginx.6666.example           # Nginx 反向代理配置示例
├── systemd.service.example      # systemd 服务配置示例
├── deploy.sh                    # 一键部署脚本
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量模板
├── .gitignore
└── README.md
```

## 快速开始

### 环境要求

- Python 3.12+
- ffmpeg（音频转码）
- [DashScope API Key](https://dashscope.console.aliyun.com/)（阿里云百炼）

### 1. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env
```

必填项：

```ini
DASHSCOPE_API_KEY=sk-你的API密钥
DATABASE_URL=sqlite:///./app.db          # 本地开发
FFMPEG_PATH=/usr/bin/ffmpeg              # ffmpeg 路径
```

### 3. 启动

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

浏览器打开 `http://127.0.0.1:8001` 即可使用。

## API 接口

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 服务健康检查 |

### 口语陪练

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/speaking/chat` | 发送消息，返回 AI 回复 + 语法分析 |
| POST | `/api/v1/speaking/speech-to-text` | 上传音频，返回转写文字 |
| POST | `/api/v1/speaking/text-to-speech` | 文字转语音 |
| POST | `/api/v1/speaking/analyze` | 单独分析英语文本 |
| POST | `/api/v1/speaking/reset/{user_id}` | 重置对话历史 |

对话请求示例：

```json
POST /api/v1/speaking/chat
{
  "user_id": "u_abc123",
  "message": "I have went to the store yesterday",
  "level": "intermediate"
}
```

响应：

```json
{
  "success": true,
  "data": {
    "response": "Oh, you went shopping! What did you buy? (Note: 'have went' → 'went')",
    "user_id": "u_abc123",
    "level": "intermediate",
    "analysis": {
      "grammar_errors": ["'have went' should be 'went' (simple past)"],
      "suggestions": ["Use simple past for completed actions with time reference"],
      "improved_version": "I went to the store yesterday."
    }
  }
}
```

### 作业批改

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/homework/grade` | 批改作业 |
| POST | `/api/v1/homework/ocr` | 图片 OCR 识别 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_NAME` | 应用名称 | 教育服务系统 |
| `APP_ENV` | 运行环境 | development |
| `HOST` | 监听地址 | 127.0.0.1 |
| `PORT` | 监听端口 | 8001 |
| `DATABASE_URL` | 数据库连接 | sqlite:///./app.db |
| `DASHSCOPE_API_KEY` | 百炼 API 密钥 | 必填 |
| `QWEN_CHAT_MODEL` | 对话模型 | qwen-plus |
| `QWEN_OCR_MODEL` | OCR 模型 | qwen-vl-plus |
| `QWEN_AUDIO_MODEL` | 语音识别模型 | qwen-audio-turbo |
| `FFMPEG_PATH` | ffmpeg 路径 | /usr/bin/ffmpeg |
| `MAX_UPLOAD_MB` | 上传大小限制 | 20 |

## 生产部署

```bash
# 一键部署
bash deploy.sh

# 或手动：Gunicorn + systemd + Nginx
sudo cp systemd.service.example /etc/systemd/system/english-teaching.service
sudo systemctl enable --now english-teaching

# Nginx 反向代理（宝塔面板直接配置）
# 目标 URL: http://127.0.0.1:8001
```

详见 `nginx.6666.example` 和 `systemd.service.example`。
