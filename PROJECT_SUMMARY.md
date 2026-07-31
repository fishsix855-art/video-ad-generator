# MoneyPrinterTurbo 改造总结

> 项目路径：D:\github项目\ai视频\MoneyPrinterTurbo-main
> 改造时间：2026-07-22 ~ 2026-07-27
> 改造范围：13个文件，共2876行

---

## 一、改造目标

将 MoneyPrinterTurbo 从「调一次 API 就返回」的 demo 升级为「Agent 多步推理 + 模板化提示词 + SQLite 持久化 + 可评测」的完整系统。

**用户操作流程不变**（7步：输入描述 -> 选创意 -> 选风格 -> 参考图 -> 设时长 -> 编辑提示词 -> 生成视频），所有改动在后台架构层面。

---

## 二、修改文件清单

### 新增文件（6个）

| 文件 | 行数 | 作用 |
|---|---|---|
| pp/services/agent.py | 150 | 手写 while-loop Agent，支持 Function Calling，不依赖 LangChain |
| pp/services/database.py | 190 | SQLite 持久化：任务记录 + 历史创意案例增删查 |
| pp/services/evaluator.py | 139 | 评测器：evaluate_prompt_quality（视频提示词评测）和 evaluate_creative_ideas（创意方案评测）分离 |
| pp/services/tools.py | 172 | Agent 工具集：search_relevant_cases / save_creative_case / evaluate_creative_ideas / evaluate_prompt_quality |
| pp/services/skill_manager.py | 62 | Prompt 模板管理器：从 prompts/skills/*.txt 加载、渲染、热更新 |
| config/app.yaml | 21 | 功能开关：agent_enabled / sqlite_enabled / skill_system_enabled |

### 新增模板文件（4个）

| 文件 | 作用 |
|---|---|
| prompts/skills/creative_ideas.txt | 普通创意生成模板（含 ${activity_theme} ${extra_context} 变量） |
| prompts/skills/creative_ideas_agent.txt | Agent 系统提示词模板（含 ${extra_context} 变量） |
| prompts/skills/creative_ideas_telecom.txt | 电信场景专用模板（含 ${product_context} 变量，可接产品知识库） |
| prompts/skills/video_prompt.txt | 分镜视频提示词模板（含风格/时长/参考图等变量） |

### 修改文件（3个）

| 文件 | 改动内容 |
|---|---|
| pp/services/llm.py | 三个生成函数（generate_creative_ideas / generate_video_prompt / generate_creative_ideas_with_agent）全部改为优先从模板加载，失败回退硬编码 |
| webui/quick_app.py | 新增 Agent RAG 推理面板展示；新增 _features 配置读取；新增 Agent 开关控制 |
| 	est/test_quick_app.py | 15个 pytest 测试覆盖 Database/Evaluator/Tools/SkillManager/Agent |

---

## 三、改动前后对比

| 维度 | 改造前 | 改造后 |
|---|---|---|
| **Agent 创意评测** | 用 evaluate_prompt_quality 评测创意方案（该函数检查时间切片），导致创意方案被错误写成视频分镜 | 用专门 evaluate_creative_ideas 评测（检查数量/字段完整/风格多样性/描述长度），创意方案保持简短 |
| **Agent 稳定性** | ChromaDB RAG（search_product_kb）首次运行需下载 BAAI/bge-small-zh 嵌入模型，导致 3 分钟+ 卡死 | 移除重依赖，Agent 25-57 秒完成 |
| **Agent 可视化** | 无推理过程展示 | WebUI 折叠面板展示每步工具调用和结果 |
| **提示词管理** | llm.py 中硬编码上百行中文提示词，修改需改代码 | 提示词在 prompts/skills/*.txt 文件中，改 txt 即可热更新，Gitable |
| **评测体系** | 只有一个评测函数，创意和提示词混用 | 两个评测函数分离：evaluate_creative_ideas（查多样性）和 evaluate_prompt_quality（查时间切片） |
| **工具集** | 无独立工具模块 | 	ools.py 统一管理 4 个工具，Agent 通过 Function Calling 调用 |
| **数据持久化** | 任务数据在内存中 | SQLite 持久化，历史记录可查看 |
| **可测试性** | 无测试 | 15 个 pytest 全部通过 |

---

## 四、架构决策说明

### 1. 为什么用 SQLite 而不是 MySQL？
单机部署、零配置、数据量小（每天几十条），SQLite 最适合。SQL 语法与 MySQL 通用，未来切换只需改连接字符串。

### 2. 为什么 Agent 用 Function Calling 而不是 LangChain？
减少框架依赖，自己写 while 循环更轻量、更可控、面试更讲得清。

### 3. 为什么 Prompt 模板用 .txt 而不是数据库存储？
模板和代码一起 Git 版本管理，产品/运营可以直接改 txt 调 prompt。

### 4. 为什么 Agent 步数上限是 5？
防止 LLM 无限循环消耗 API 费用，5 步足够覆盖「分析 -> 检索 -> 生成 -> 评测 -> 重试」全链路。

---

## 五、测试结果

`
pytest test/test_quick_app.py -v

TestDatabase::test_init_db              PASSED
TestDatabase::test_save_and_get_task    PASSED
TestDatabase::test_list_tasks           PASSED
TestDatabase::test_creative_cases       PASSED
TestEvaluator::test_bad_prompt          PASSED
TestEvaluator::test_good_prompt         PASSED
TestEvaluator::test_bad_creative_ideas  PASSED
TestEvaluator::test_good_creative_ideas PASSED
TestTools::test_search_cases            PASSED
TestTools::test_evaluate_prompt         PASSED
TestTools::test_tool_definitions        PASSED
TestSkillManager::test_list_skills      PASSED
TestSkillManager::test_render_skill     PASSED
TestAgent::test_agent_no_tools          PASSED
TestAgent::test_agent_with_tools        PASSED

15 passed in 6.87s
`

---

## 六、改造的实际意义

### 对用户（一线员工）
7 步操作流程没变，但：
- Agent 推理让创意方案更精准、风格更多样
- 模板系统让提示词质量可控、可进化

### 对开发者（项目维护者）
- 提示词改 txt 文件即可，不需要懂 Python 代码
- 评测器自动检查输出质量，减少人工审核
- SQLite 历史记录支持数据分析（哪个方案效果好）

### 对求职（面试亮点）
- 「手写 Agent」体现工程能力，不是套壳
- 「评测体系分离」体现架构设计思维
- 「模板系统」体现工程化实践
- 「15 个 pytest」体现测试意识
