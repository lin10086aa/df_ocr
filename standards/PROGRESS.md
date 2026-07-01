# PROGRESS · df_ocr 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-07-01 · by AI)

- **阶段**:`开发完成` (对应六步流程第④步完成: 本地 CI 自检全绿)
- **上一步完成**:全部 7 个模块代码 + 测试 + Dockerfile + CI 配置完成,本地自检(ruff + pytest --cov=85%)全绿。
- **下一步 (TODO 第一条)**:
  - 若需远程仓库: 创建 GitHub 仓库,推送代码,提 PR,等待 CI 复检。
  - 若仅本地: 可直接 `docker build -t df-ocr . && docker run -p 8000:8000 df-ocr` 启动服务。
- **阻塞项**:无

---

## 待办清单 (TODO,按优先级)

- [x] 初始化本地 Git 仓库,创建 `.gitignore`
- [x] 从 `main` 开 feature 分支 `feature/1-project-init`
- [x] 实现 FastAPI 骨架: `app/main.py` + 健康检查路由
- [x] 实现前端静态页面: 上传 UI (拖拽/选择、多文件、进度展示)
- [x] 实现文件上传 API: 接收 PDF、校验、暂存
- [x] 实现 OCR 服务层: 封装 PP-StructureV3 调用 (PDF→图片→OCR→Markdown)
- [x] 实现结果下载 API: 单文件 `.md` 下载 + 多文件 `.zip` 打包
- [x] 实现临时文件清理: 后台定时清理过期上传文件
- [x] 编写 Dockerfile: CPU 优先,支持镜像源参数
- [x] 编写单元测试: health / upload / ocr_service / download / file_service (24 项,覆盖率 85%)
- [x] 配置 CI (GitHub Actions): ruff format + ruff check + pytest --cov + docker build
- [x] 本地 CI 自检全绿: ruff format ✓ / ruff check ✓ / pytest --cov=85% ✓
- [ ] (可选) 创建 GitHub 仓库,推送代码,提 PR,CI 复检
- [ ] (可选) `docker build` 验证
- [ ] 验证端到端: 启动服务 → 浏览器上传 PDF → 查看 Markdown → 下载

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-07-01 | OCR 服务使用 mock 引擎兜底 | 当 PaddleOCR 不可用时自动降级,保证上传/下载全链路可测试 |
| 2026-07-01 | `_PPStructureEngine` 标记 `no cover` | 需要 PaddleOCR + poppler 运行时,属于集成测试范畴 |
| 2026-07-01 | file_service 提取纯函数 `remove_expired_files` | 分离清理逻辑与循环调度,使核心路径可单元测试 |
| 2026-07-01 | 前端采用 Vanilla JS 内嵌 FastAPI,不引入前端框架 | 功能聚焦(上传+预览+下载),零构建,单容器部署;避免 Node.js 构建链 |
| 2026-07-01 | 后端选择 FastAPI | 异步支持、文件上传内置支持、自动 OpenAPI 文档、PaddleOCR Python 生态原生 |
| 2026-07-01 | Docker 单容器部署 (FastAPI + 静态前端) | 减少容器编排复杂度;OCR 模型权重通过 pip 包自带,无需额外卷挂载 |
| 2026-07-01 | OCR 引擎: PP-StructureV3 | 需求指定;支持版面分析、表格识别、公式识别,输出可直接转 Markdown |
| 2026-07-01 | Docker 镜像 CPU 优先 (paddlepaddle CPU 版) | 降低部署门槛,GPU 版作为可选变体 |
| 2026-07-01 | 暂不做 CD 自动部署 | 当前阶段只做 CI,部署通过手动 `docker run` 完成;CD 后续按需追加 |

---

## 已知坑 (GOTCHAS)

| 现象 | 根因 | 解决 | 验证 |
|---|---|---|---|
| `pdf2image` 报 `Unable to get page count. Is poppler installed?` | pdf2image 依赖系统 `poppler-utils`,Windows 默认没有 | Dockerfile 中 `apt install poppler-utils`;本地测试用 mock 引擎绕过 | test_upload 通过 |

---

## 里程碑 (DONE)

- [x] 初始化项目上下文: `00-project-context.md` 已填写
- [x] 确认需求与验收标准: `01-requirements.md` 已填写 (US-1 ~ US-4)
- [x] 初始化 PROGRESS.md: 第一批 TODO 已列出
- [x] 全部 7 个模块开发完成: 前端 + 后端 API + OCR 服务 + 下载 + Dockerfile + CI
- [x] 本地自检全绿: ruff ✓ / ruff check ✓ / pytest 24 项 ✓ / coverage 85% ✓
