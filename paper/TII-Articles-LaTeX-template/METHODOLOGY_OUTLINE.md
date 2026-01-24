# III. 方法（Methodology）写作提纲（对齐 Fig.2）

> 目标：围绕 Fig.2 的闭环工作流，形成可复现的 Methodology，并与第三章开头“四阶段”表述一致。  
> 主线：`workflow orchestration → offline templates/KG → online reasoning & interaction → synthesis → 3-level verification → visual feedback → refinement`。  
> 约定：图中 P1/P2/P3 为三阶段计划（工具调用/提示组装/最终推理），在正文定义，不在图内写长句。

---

## III. Methodology（组织方式：四阶段方法论，对齐开头总览）

> 说明：第三章开头总览已采用“四阶段”描述（工作流组织与任务分解 / 工艺知识与模板建模 / 在线推理与交互补参 / 代码生成与验证反馈）。本章结构按四阶段依次展开；其中第 2–4 阶段与 Fig.2 的三大功能块（offline / agent reasoning / synthesis & verification）一一对应，第 1 阶段用于补足闭环工作流与计划调度的定义。

### Fig.2 放置位置（写进大纲，避免后续返工）
- 放在 `\section{Methodology}` 开头总览段之后、进入第一个小节（III-A/III-B）之前；作用是给出全链路“离线构建→在线推理→合成验证→反馈闭环”的总览，再分小节展开。

### Fig.2 标题建议（保持示例那种简短风格）
- 你已确定：`Fig. 2. Overall workflow of the LLM-KG CNC programming system.`

### 开场段落模板（模仿范例的写法）
- 句 1：引用 Fig.2，说明本文方法围绕一个可执行的工作流闭环组织。
- 句 2：用“四阶段”概括本章组织方式：工作流组织与任务分解 → Offline Template Construction → LLM Agent \& Reasoning → Synthesis \& Verification。
- 句 3：用 1 句点明目标：将自然语言形式的加工需求转化为安全可靠的可执行程序，并强调多阶段协同推理与迭代校验逻辑。
- 句 4：收束句：正文写作顺序可先给出“工作流组织与任务分解”（III-A），再展开离线构建、在线推理与合成验证三块；同时给出关键输入/输出与实现要点，便于复现。（P1/P2/P3 与“闭环组织”视角放到 III-A 末段简要引出即可。）

### 本章结构（四阶段，对齐第三章开头总览）
- III-A：Closed-loop Workflow Overview（工作流组织与任务分解：闭环与计划调度定义，必要时再引出 P1/P2/P3）
- III-B：Offline Template Construction（工艺知识与模板建模：离线固化与入库）
- III-C：LLM Agent \& Reasoning（在线推理与交互补参：意图解析、槽位补全、工具调用）
- III-D：Synthesis \& Verification（代码生成与验证反馈：模板执行/后处理/三层验证/回流修正）

### 与第一章“四点创新”的处理策略（先不强行改结构）
- 本章先按 Fig.2 的自然模块边界写清“可复现的方法论”，再回到引言对四点贡献的表述做匹配性调整（例如把“闭环工作流”作为第 1 点贡献的落脚，或将验证/纠错单列为第 4 点贡献）。

> 备注：第三章用 Fig.2 讲“流程与接口”，第四章/实验章节再用指标与消融支撑每个模块的作用，避免在 Methodology 里堆太多实现细节。

---

## A. Closed-loop Workflow Overview（工作流组织与任务分解）

### 目的与写作目标（段落结构）
- 用 1 段把 Fig.2 的输入→中间表示→输出→反馈闭环讲清楚：自然语言指令 $u$、上下文 $c$ → 意图与参数（$p,f,P$）→ 模板检索与执行 → G-code $y$ → 验证报告 $R$ → 回流迭代。
- 明确 P1/P2/P3 的职责：P1（工具与 KG 检索）、P2（提示组装）、P3（最终推理/选择/输出）。
- （可选，弱化写法）用 1 句承接“闭环组织”视角：以“感知—交互—决策—反馈”概括模块分工（不额外画到 Fig.2，不展开具身细节）。

---

## B. Offline Template Construction（工艺知识与模板建模）

### 目的与输入输出（段落结构）
- 输入：结构化数据（工艺大类/子工艺、参数规则、控制器规范）+ 非结构化资料（手册/PDF）+ 专家经验（模板整理与审阅）。
- 输出：Neo4j 图数据库（`Process/SubProcess/INCLUDES`）+ 模板库（`SubProcess.code`）+（可选）GraphRAG 参考。
- 写作重点：强调模板“可执行、可审计、可回溯”，为在线阶段提供稳定的受控生成边界。

### 1) Graph Schema in Neo4j（图谱结构）
- 节点：`Process`、`SubProcess`（含 `name` 与 `code`），必要时扩展为 `GCode`、`Parameter`。
- 关系：`INCLUDES`（`Process → SubProcess`），用于工艺树检索与候选模板召回。
- 关键字段：模板以代码字符串形式存储在 `SubProcess.code`，运行时检索并执行生成 G-code。

### 2) Offline Template Authoring (Expert + GraphRAG)（离线模板整理）
- 专家讨论：将工艺经验整理为可复用模板，并进行人工审阅与版本管理。
- GraphRAG 参考：用于检索/对齐说明书条目与规则表述（可写为辅助，不作为在线核心链路）。
- 入库：通过 Cypher 更新图谱结构与 `SubProcess.code`（正文简述，示例可放附录）。

---

## C. LLM Agent \& Reasoning（在线推理与交互补参）

### 目的与输入输出（段落结构）
- 输入：自然语言指令 `u` + 场景上下文 `c`。
- 输出：结构化任务 `T` 与完整参数集 `P`（包含来源：用户显式/知识推理/默认策略）。
- 写作重点：强调“从开放语义到可验证中间表示”，并为后续模板渲染与验证回溯提供锚点。

### 1) Unified Input Normalization（统一输入规范化）
- 单位/数值规范化：中文数字、口语表达、坐标写法（`X10Y10`/`X=10,Y=10`）、速度表达（`300 rpm`/“三百转每分”）。
- 上下文补充：从 `c` 注入控制器方言、坐标系、刀具配置、材料等关键字段。

### 2) Self-Reflective Intent Recognition（自反思意图识别）
- 目标：识别工艺类型 `p`、加工特征 `f`，输出 `conf` 与证据片段（支持可追溯）。
- 机制：当 `conf<τ` 触发 self-reflection，要求模型检查关键词遗漏、歧义边界与工艺可行性，并给出修正。
  - Fig.2 建议在正文明确：`τ = 0.7`（与实现一致）。

### 3) Slot Extraction and Completion Policy（槽位抽取与补全策略）
- 槽位集合：几何（起点/终点/尺寸）、工艺（深度/余量/进给/转速/进刀次数）、设备（刀具号/补偿/安全高度）。
- 补全策略（可写成“交互 + 推理”二选一）：  
  - 交互式批量收集：把强耦合参数分组一次提问，减少轮次；  
  - 知识约束推理：基于 `\mathcal{G}` 给出推荐区间/默认值，并做一致性校验（异常触发回问）。
- 产出：`T={p,f,S_known,S_miss,constraints}` 与 `P`。

### 4) P1/P2/P3 Plan Definition（分阶段计划的最小定义）
- P1：工具调用与 KG 检索（触发 Cypher 查询、候选模板召回、必要的参数抽取工具）。
- P2：提示组装（将 KG Result + session params + 规则约束组装为完整 prompt）。
- P3：最终推理与输出（驱动 LLM 做模板选择/生成决策，并将结果送入合成与验证模块）。

---

## D. Synthesis \& Verification（代码生成与验证反馈）

### 目的与输入输出（段落结构）
- 输入：`T, P` 与知识图谱 `\mathcal{G}`（以及模板库 `\mathcal{M}`）。
- 输出：候选代码 `y_0`（模板渲染结果）与生成依据（模板选择理由/参数注入记录）。
- 写作重点：突出“受控生成”——模板与规则负责结构正确性，LLM负责选择与解释，而不是直接凭空写代码。

### 1) KG Query and Controlled Synthesis（检索与受控合成）
- 查询：`KG Retriever & Template Selector → Neo4j`（Cypher）返回候选 `SubProcess.code`。
- 选择：多维度评分排序（LLM 语义评分 + 参数覆盖度 + 使用先验 +（可选）语义相似度）。
- 合成：执行 `exec(SubProcess.code)` 实例化工艺类并生成 G-code，随后进行必要的后处理/格式适配。

### 2) Three-level Verification and Auto-fix（验证与自动修复，突出贡献点）
- 三层：syntax rules → parameter range checks → LLM deep verification（输出 issues + suggestions）。
- 建议给出总分聚合公式（与实现一致）：`overall = 0.5·safety + 0.25·efficiency + 0.25·standard`。
- 失败回路：依据验证证据回流到 P1/P2/P3 触发重选模板/回问参数/自动修复再验证。

### 3) Unity Sim2Real Visual Feedback（轻量可视化反馈，非核心但闭环落点）
- 定位：外部 Unity UI 用于加工过程同步预览与人工确认。
- 作用：提供 visual feedback 作为补充证据，辅助触发二次修正（简写即可）。

---

## Algorithm 1（建议加一个总算法，模仿范例的 Algorithm 1）

### 建议算法名
- `Algorithm 1: Closed-loop Knowledge-Graph-Enhanced G-code Generation`

### 输入输出（保持 IEEE/TII 风格）
- Input: `u, c, KG \mathcal{G}, template library \mathcal{M}, thresholds τ`
- Output: `G-code y, report R`

### 伪代码的核心步骤（对应A/B/C/D + P1/P2/P3）
0) Offline: author templates and update Neo4j (`SubProcess.code`)
1) Normalize `u,c` → `u',c'`
2) Intent parse + self-reflect → `T`
3) Slot extraction + parameter completion (interactive/inference) → `P`
4) P1: tools + KG query → candidate templates
5) P2: prompt assembly with KG result + session state
6) P3: final reasoning & synthesis → `y_0`
7) Verify (syntax→range→LLM + visual feedback) → if fail: self-correct & loop
7) Return `y,R`

---

## 写作提醒（让第三章更像“已发表TII”的质感）
- 每个大节（A/B/C/D）开头 1 段写“目的+挑战+本节贡献”，结尾 1 句写“输出变量是什么，如何进入下一节”。
- 多用“输入/输出/中间表示”的术语（`T, P, \mathcal{M}, y, R`），减少纯叙述。
- 少说“我们借鉴具身智能”，多说“我们如何让生成受控/可验证/可追溯”。
- 你当前 LaTeX 第三章偏“框架介绍”，后续写第四章算法细节时，第三章也可以保留为“Methodology总览”，第四章再展开 A/B/C/D 的关键算法（避免第三章写太细导致第四章重复）。
