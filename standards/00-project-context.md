# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`df_ocr`
- **一句话目标**:用户在前端页面提交 PDF 文件,后端通过 PP-StructureV3 OCR 引擎将图片型 PDF 转换为结构化 Markdown 文本并返回下载。
- **使用者/受益者**:任何需要从扫描件、图片型 PDF 中提取结构化文本的用户(学生、办公人员、开发者)。
- **核心功能**:
  - 前端页面支持一次提交一个或多个 PDF 文件
  - 后端调用 PP-StructureV3 进行 OCR 识别与版面分析
  - 输出结构化 Markdown(保留标题、段落、表格、列表等结构)
  - 支持结果在线预览与下载
- **输入/数据**:用户上传的 PDF 文件(以图片型为主);文件不进 Git,不持久化存储(处理后定时清理)。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | PP-StructureV3 / PaddleOCR 生态成熟,Python 首选 |
| Web/API 框架 | FastAPI | 异步支持、文件上传便捷、自动生成 API 文档、生态好 |
| 前端 | 内嵌于 FastAPI 的静态 HTML/JS (Vanilla JS) | 轻量、零构建、单容器部署,功能聚焦无需重型框架 |
| OCR 引擎 | PP-StructureV3 (PaddleOCR) | 需求指定;支持版面分析+表格识别+公式识别 |
| 测试 | pytest + httpx (async) | FastAPI 官方推荐 async 测试客户端 |
| 格式/静态检查 | ruff (format + check) | 快速、Python 生态标准 |
| 打包/运行 | Docker (单容器) | 依赖重(PaddlePaddle GPU/CPU),容器化保证环境一致性 |
| CI | GitHub Actions | 通用、可视化,PR 触发自动检查 |

## 3. 目录地图

```text
df_ocr/
├── standards/                  # AI 项目记忆与通用规范
├── app/                        # FastAPI 应用源码
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py           # 上传 API
│   │   └── health.py           # 健康检查
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py      # PP-StructureV3 调用封装
│   │   └── file_service.py     # 文件管理(保存/清理)
│   ├── static/                 # 前端静态文件
│   │   ├── index.html          # 主页面
│   │   ├── style.css           # 样式
│   │   └── app.js              # 上传交互逻辑
│   └── templates/
├── tests/                      # 测试目录
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_upload.py
│   └── test_ocr_service.py
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖
├── Dockerfile                  # 容器镜像构建
├── .github/workflows/
│   └── ci.yml                  # PR 触发 CI (暂无 CD)
├── .gitignore
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` (不含 OCR 模型调用的集成测试) |
| 覆盖率 | ≥ 80% (核心业务逻辑) |
| 构建 | `docker build` 成功 (CI 执行) |
| 业务/模型指标 | OCR 结果格式校验(Markdown 有效、表格正确);上传/下载端到端可用 |

> 注意:OCR 模型推理是集成测试范畴,本地单元测试可 mock OCR 服务。

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进环境变量。
- 大文件(PDF 上传、模型权重)不进 Git;模型在 Docker build 时通过 pip 安装。
- OCR 模型文件(PaddleOCR 模型)通过 pip 包自动下载,不手动管理。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 上传文件存储在容器内临时目录(`/tmp/df_ocr/uploads`),定期清理。

## 6. 部署/运行占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `df-ocr` | 应用名/镜像名/容器名 |
| `<PORT>` | `8000` | 服务端口 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/api/health` | 健康检查地址 |
