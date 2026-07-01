# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试与 CI,
以便 后续每次 PR 都能自动检查代码质量。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: PR 触发 CI,至少包含格式检查、静态检查、单元测试、Docker 构建检查。
- AC3: CI 全绿后合并 main。
- AC4: 完成后更新 `standards/PROGRESS.md`。

---

### US-2 PDF 文件上传与 OCR 转换 · 状态: Backlog

作为 **普通用户**,
我想要 在网页上提交一个或多个 PDF 文件并获得 OCR 识别后的 Markdown 文本,
以便 快速从扫描件/图片型 PDF 中提取可编辑的结构化文字。

验收标准:
- AC1: Given 用户打开前端页面,When 页面加载完成,Then 看到文件上传区域(支持拖拽或点击选择),支持同时选择多个 PDF 文件。
- AC2: Given 用户已选择 1~N 个 PDF 文件,When 点击"开始转换",Then 文件上传至后端,后端调用 PP-StructureV3 进行 OCR,前端显示处理进度。
- AC3: Given OCR 处理完成,When 前端收到结果,Then 每个 PDF 显示对应的 Markdown 预览,支持查看/复制。
- AC4: Given 用户上传了包含表格的 PDF,When OCR 完成,Then Markdown 中以表格语法呈现表格内容。
- AC5: Given 用户上传了非 PDF 文件或损坏的 PDF,When 提交,Then 后端返回明确的错误提示(文件类型/损坏原因),前端友好展示。

技术备注:
- PP-StructureV3 处理较慢(单页可能数秒),需考虑异步任务与超时。
- 大 PDF(>50 页)需限制或分页处理。
- 单文件上限暂定 50MB,单次最多 10 个文件。

---

### US-3 转换结果下载 · 状态: Backlog

作为 **普通用户**,
我想要 将 OCR 转换结果下载为 `.md` 文件,
以便 在本地编辑、存档或导入其他工具。

验收标准:
- AC1: Given 单个 PDF 转换完成,When 用户点击"下载",Then 浏览器下载一个同名的 `.md` 文件(如 `report.pdf` → `report.md`)。
- AC2: Given 多个 PDF 转换完成,When 用户点击"全部下载",Then 浏览器下载一个 `.zip` 包,内含所有 `.md` 文件。
- AC3: Given 下载请求发出,When 文件已清理(过期),Then 返回友好提示"结果已过期,请重新上传"。

---

### US-4 Docker 容器化部署 · 状态: Backlog

作为 **运维人员 / 开发者**,
我想要 通过一条 `docker run` 命令就能启动整个服务(前端+后端+OCR),
以便 在任何有 Docker 的机器上快速部署。

验收标准:
- AC1: Given 已构建 Docker 镜像,When 执行 `docker run -p 8000:8000 df-ocr`,Then 服务在 `http://localhost:8000` 可访问,前端页面上传功能可用。
- AC2: Given 服务运行中,When 访问 `/api/health`,Then 返回 `{"status": "ok"}`。
- AC3: Given Docker 环境无 GPU,When 运行容器,Then 服务以 CPU 模式启动 OCR(性能下降但功能正常)。
- AC4: Dockerfile 构建成功(CI 门禁之一)。

技术备注:
- PaddleOCR 依赖较大,Docker 镜像预计 3~6 GB。
- 可考虑使用 `paddlepaddle` CPU 版缩小体积。

---

## 5. 非功能需求

- **安全**:上传文件不持久化(处理完保留 30 分钟后清理);密钥只进环境变量,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交;模块化分层(router / service / static)。
- **可测试**:核心逻辑必须有单元测试;OCR 调用层可 mock;上传/下载端到端可用 curl 验证。
- **可部署**:Dockerfile 构建成功即可手动 `docker run` 部署;健康检查内置。
- **性能**:单页 OCR 预期 < 10 秒(CPU);大 PDF 需分页流式处理。
- **兼容**:支持主流 PDF 格式(扫描件、文字型 PDF 均需渲染为图片后 OCR)。
