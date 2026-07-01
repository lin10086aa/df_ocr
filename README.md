# df_ocr — PDF 转 Markdown

基于 **PP-StructureV3** 的 PDF OCR 工具。上传 PDF 文件，自动识别文字、表格、版面结构，输出结构化 Markdown。

## 快速开始

```bash
# 本地开发（需要 poppler）
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker 部署（推荐，环境完整）
docker build -t df-ocr .
docker run -p 8000:8000 df-ocr
```

打开 http://localhost:8000 即可使用。

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | Python 3.11 + FastAPI |
| 前端 | Vanilla HTML/CSS/JS |
| OCR | PP-StructureV3 (PaddleOCR) |
| 部署 | Docker |
| CI | GitHub Actions (ruff + pytest + docker build) |

## API

| 端点 | 说明 |
|---|---|
| `GET /api/health` | 健康检查 |
| `POST /api/upload` | 上传 PDF，返回 Markdown |
| `POST /api/download/zip` | 批量下载 .zip |

## 项目结构

```
df_ocr/
├── app/            # FastAPI 源码
├── tests/          # pytest (24项, 85% 覆盖)
├── standards/      # 项目规范与需求文档
├── Dockerfile
├── .github/workflows/ci.yml
└── requirements.txt
```
