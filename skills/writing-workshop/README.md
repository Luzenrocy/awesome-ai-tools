# writing-workshop

`writing-workshop` 是一个面向 Codex 的多角色写作与审查技能。它把一次写作任务组织成可追踪的工作流：主写者负责产出，reviewer 负责独立找问题，checker/approver 负责判断是否可以发布。

这个技能适用于规格说明、需求文档、设计说明、学习笔记、博客、指南、运行手册、RFC、ADR、报告、政策、清单以及用户指定的其他文档类型。它不要求所有文档使用同一套固定模板，而是先根据读者任务、文档类型、风险和证据要求生成自适应文档契约。

## 原理

技能的核心是“用户意图可追踪 + 角色隔离 + 过程记录完整”。一次运行会保存用户原始请求、需求台账、来源、文档契约、规则快照、每轮和每次迭代的草稿与审查结果，最后才发布干净的目标文档。

流程有两个层级：

1. 一个 `round` 是一批迭代，默认从第 1 轮开始。
2. 一个 `iteration` 是一次 writer → reviewer → checker 循环，每轮默认最多 10 次。

如果 checker 在当前轮的迭代预算耗尽后仍发现问题，技能会汇总剩余问题并向用户询问是否开始下一轮。只有用户明确选择继续，才会创建下一轮；不会自动无限迭代。checker 返回 `approve` 后，才会把干净文档发布到用户指定的目标路径。

过程文件按职责分开：审查结果写入 `review.md`，进度写入 `progress.md`，长期有效的决定和约束写入 `memory.md`，用户继续或停止下一轮的决定写入 `user-decision.md`。

## 用途

- 将自然语言请求整理为带稳定 ID 的需求台账。
- 根据文档用途生成适配的结构、读者、语气和质量检查。
- 使用独立 reviewer 检查遗漏、矛盾、越界内容、无依据声明和风险。
- 使用 checker 判断审查结果是否已处理，以及是否允许发布。
- 保留每次迭代的输入、草稿、审查、修订、覆盖矩阵和决策证据。
- 将过程文件放在目标位置下独立的 `council/` 子目录；例如 `ai-docs/report.md` 使用 `ai-docs/council/`，`ai-docs/report` 使用 `ai-docs/report/council/`。
- 在不依赖外部服务时直接运行；如果用户指定其他 skill，可把其格式或验证器作为可选契约覆盖。

## 当前源码结构

```text
writing-workshop/
├── SKILL.md                         # 技能入口：工作流、角色边界、状态机和执行规则
├── README.md                        # 使用者/维护者说明：原理、用途、结构和安装
├── agents/
│   └── openai.yaml                  # Codex 展示元数据，不承载运行时 agent 逻辑
├── references/                      # 可按任务读取的细粒度规则和契约
│   ├── approval-protocol.md         # checker 判定、批准/修订/阻塞及跨轮次门控
│   ├── document-contracts.md        # 文档契约字段、结构和质量检查的通用定义
│   ├── integration.md               # 外部 skill 契约的发现、优先级和交接规则
│   ├── process-artifacts.md         # 过程路径、过程文件分类和文件职责
│   ├── public-foundations.md        # 写作/需求工程参考资料及其适用范围
│   ├── requirements-ledger.md      # 用户需求台账、约束、验收条件和覆盖矩阵
│   ├── review-rubric.md             # reviewer 的检查维度、问题级别和发现格式
│   ├── role-profiles.md             # writer、reviewer、checker 的职责和调用边界
│   ├── skill-reload.md              # 规则快照、哈希、重载和旧草稿失效处理
│   └── type-adaptation.md           # 文档类型、读者任务与最小质量契约的适配方法
└── scripts/                         # 过程目录初始化、校验和规则指纹工具
    ├── council_schema.py            # 脚本共享的文件名、状态、路径和轮次常量
    ├── fingerprint_skill.py         # 为技能源码生成 SHA-256 规则快照
    ├── init_council.py              # 创建 council、manifest、首轮和首个迭代骨架
    └── validate_council.py          # 校验路径、状态、轮次、迭代文件和发布证据
```

### 入口和元数据

| 文件 | 用途 |
| --- | --- |
| `SKILL.md` | 技能入口。定义触发条件、角色边界、轮次/迭代状态机、路径规则、发布要求和默认过程目录。 |
| `agents/openai.yaml` | Codex 对技能的展示名称、简介和默认提示词。它不是运行时 agent 实现。 |
| `README.md` | 面向维护者和使用者的原理、结构、安装和维护说明。 |

### 参考契约

| 文件 | 用途 |
| --- | --- |
| `references/approval-protocol.md` | checker 的批准、修订、阻塞和用户继续下一轮的状态机。 |
| `references/document-contracts.md` | 通用文档契约字段与常见文档结构。 |
| `references/integration.md` | 外部 skill 作为可选契约覆盖时的优先级、发现和交接规则。 |
| `references/process-artifacts.md` | 过程目录解析规则，以及 intake、draft、review、progress、memory、publication 等文件类型边界。 |
| `references/public-foundations.md` | 需求工程、技术写作和文档设计的公开参考资料，仅作为风格和质量依据。 |
| `references/requirements-ledger.md` | 用户意图台账、`U-*` 条目、修订记录和覆盖矩阵规则。 |
| `references/review-rubric.md` | reviewer 每次迭代必须检查的维度、问题分类、严重级别和发现格式。 |
| `references/role-profiles.md` | writer、reviewer、checker 的职责、角色路由和 fresh-context 调用边界。 |
| `references/skill-reload.md` | 规则快照、哈希、重新加载和草稿过期处理。 |
| `references/type-adaptation.md` | 根据读者任务和文档家族选择最小契约及质量检查的方法。 |

### 脚本

| 文件 | 用途 |
| --- | --- |
| `scripts/council_schema.py` | 供初始化和校验脚本共享的文件名、状态、轮次上限和迭代上限常量。 |
| `scripts/init_council.py` | 初始化过程目录、manifest、需求台账、规则快照、round-01 和 iteration-01 文件。支持文件目标与目录目标路径解析。 |
| `scripts/validate_council.py` | 检查 manifest、路径、状态、轮次、迭代文件、coverage、发布记录和未解决问题记录。 |
| `scripts/fingerprint_skill.py` | 为 `SKILL.md`、元数据、参考文档和 helper scripts 生成 SHA-256 规则快照，并过滤 Python 缓存文件。 |

## 过程目录

当目标路径是 `ai-docs/report.md` 时，过程文件位于 `ai-docs/council/`；当目标路径是 `ai-docs/report` 时，过程文件位于 `ai-docs/report/council/`。典型结构如下：

```text
{process-path}/
├── manifest.yaml                    # 运行元数据、状态、计数器、路径和角色路由
├── intake.md                       # 本次运行的结构化启动摘要和目标说明
├── user-brief.md                   # 用户原始请求及按日期追加的修订，保持不可变
├── requirements-ledger.yaml        # 带 U-* ID 的需求、约束、验收条件和用户决定
├── adaptive-contract.yaml          # 文档类型、读者、结构、格式和质量检查契约
├── source-index.md                 # 来源清单、版本/日期及各来源的使用目的
├── rules-snapshot.yaml             # 本次运行加载的技能文件、哈希和规则版本
├── reload-events.md                # 规则变更、重载时间及受影响记录
├── progress.md                     # 追加式进度时间线：轮次、迭代、角色和下一步
├── memory.md                       # 跨迭代/跨轮次可复用的决定、术语、约束和未决项
├── rounds/                         # 按轮次隔离的全部草稿、审查和决定证据
│   └── round-01/                  # 第 1 轮；用户同意后才会创建 round-02 等
│       ├── iterations/             # 本轮每次 writer→reviewer→checker 循环的历史
│       │   └── iteration-01/       # 第 1 次迭代，后续迭代不覆盖本目录
│       │       ├── draft.md        # 本次迭代的 writer 草稿
│       │       ├── review.md       # 本次迭代 reviewer 的逐条发现和证据
│       │       ├── revision.md     # 针对发现的修改映射、处理理由和证据
│       │       ├── decision.md     # checker 的 approve/revise/blocked 判定
│       │       ├── coverage.yaml   # 需求 ID 到草稿位置/证据的覆盖映射
│       │       └── input-snapshot.yaml # 本次角色调用实际读取的规则/契约快照
│       ├── draft.md                # 本轮当前/最新草稿索引，便于快速读取
│       ├── review.md               # 本轮当前/最新审查索引，不替代迭代历史
│       ├── revision.md             # 本轮当前/最新修改索引，不替代迭代历史
│       ├── decision.md             # 本轮当前/最新 checker 判定索引
│       ├── coverage.yaml           # 本轮当前/最新需求覆盖索引
│       ├── input-snapshot.yaml     # 本轮当前/最新输入快照索引
│       ├── round-summary.md         # 达到本轮迭代预算后的剩余问题汇总
│       └── user-decision.md         # 用户是否继续下一轮的明确决定
├── publish.md                      # checker 批准后实际发布的目标、版本和校验证据
├── completion-summary.md            # 完成后的文件清单、结果、验证和入口链接
└── unresolved.md                   # 仅阻塞、用户停止或达到轮次上限时记录未决问题
```

其中 `round-01/` 下的六个同名文件是“当前/最新索引”，真实历史以
`iterations/iteration-MM/` 下的文件为准；它们不能替代历史记录。`publish.md`、
`completion-summary.md` 和 `unresolved.md` 是结束阶段文件，未达到相应状态时不应
提前创建。最终文档不应包含角色讨论、隐藏推理或过程评论。

## 安装和使用

本仓库已经提供 Claude Code Marketplace 和 Codex Plugin 的根级 manifest。
从仓库安装时，宿主会发现 `skills/writing-workshop/SKILL.md`；不需要为
Claude Code 复制一份单独的 Skill。Claude Code 的提问交互由宿主提供，若宿主
没有结构化提问组件，技能会退回到普通文本提问。

Claude Code：

```text
/plugin marketplace add https://github.com/Luzenrocy/awesome-ai-tools
/plugin install awesome-ai-tools@awesome-ai-tools
```

Codex：

```bash
codex plugin marketplace add Luzenrocy/awesome-ai-tools
codex plugin add awesome-ai-tools@awesome-ai-tools
```

直接使用本地 skill 时，将此目录复制到 Codex 的用户技能目录：

```bash
cp -R skills/writing-workshop "${CODEX_HOME:-$HOME/.codex}/skills/writing-workshop"
```

安装后，在新的 Codex 对话中显式使用 `$writing-workshop`，或提出符合其描述的写作任务。若目标目录已有旧版本，应先比较版本，再同步更新；不要把 `__pycache__` 或 `.pyc` 文件打包进去。

