# Skill 创建与自定义指南

## 一、如何创建自定义 Skill

### 1. 安装 skill-creator

首先需要安装官方的 Skill 生成工具：

```bash
npm install -g @skill-creator/cli
# 或通过其他官方推荐的方式安装
```

### 2. 完整创建流程

#### 步骤 1：让 Claude Code 完成任务
- 先使用 Claude Code 完成你的任务一次
- 确保整个流程可以正常运行
- 记录所有步骤和交互过程

#### 步骤 2：基于上下文创建 Skill
- 完成任务后，让 Claude Code 参考 skill-creator 的格式和结构
- 根据刚才的执行过程，创建一个新的 Skill

**示例场景**：
```
任务：查询北京今日天气并保存到文档

执行流程：
1. 打开浏览器
2. 搜索"北京今日天气"
3. 获取当前页面结构
4. 提取今天的天气信息
5. 创建一个 md 文档，命名为今日日期
6. 写入天气内容到文档
```

#### 步骤 3：生成 Skill
- 告诉 Claude Code："请参考 skill-creator 的格式，创建一个流程 Skill，用于查询天气并保存到文档"
- Claude Code 会将整个流程封装成一个可复用的 Skill

### 3. 支持 MCP 查询结果

Skill 可以包含：
- MCP 查询到的结果
- MCP 本身的调用过程
- 任何通过工具获得的数据

**能力范围**：
- ✅ 浏览器操作（打开、搜索、导航）
- ✅ 页面结构分析
- ✅ 数据提取和处理
- ✅ 文件创建和编辑
- ✅ API 调用和响应处理
- ✅ 多步骤流程编排

### 4. 修改现有 Skill

如果需要对现有的 Skill 进行修改：

**修改方法**：
1. 将 Skill 文件夹拖到 Claude Code 对话框中
2. 告诉 Claude Code："请参考 skill-creator 进行修改，我需要修改的内容是：[具体需求]"

**可以修改的内容**：
- ✅ 触发条件（keywords, patterns）
- ✅ 执行流程（steps）
- ✅ 参数配置（parameters）
- ✅ 输出格式（output format）
- ✅ 依赖关系（dependencies）
- ✅ 任何其他内容

---

## 二、如何创建自定义 Hooks

### 学习来源

参考文档：[25% → 90%！别让 Skills 吃灰：Hooks + Commands + Agents 协同激活 AI 全部能力](https://blog.csdn.net/xxx)

### 1. 创建 Hooks 文件

在项目根目录下创建：
```
.claude/hooks/skill-forced-eval.js
```

### 2. 编辑 Hooks 内容

```javascript
// skill-forced-eval.js 核心逻辑
const instructions = `## 指令：强制技能激活流程（必须执行）

### 步骤 1 - 评估
针对以下每个技能，陈述：[技能名] - 是/否 - [理由]

可用技能列表：
- crud-development: CRUD/业务模块开发
- api-development: API设计/RESTful规范
- database-ops: 数据库/SQL/建表
- ui-pc: 前端组件/AForm/AModal
- ui-mobile: 移动端/WD UI组件
- skill-creator: Skill创建和生成
- webapp-testing: Web应用测试
- plan-agent: 规划和分析
- explore-agent: 代码库探索
- frontend-tester: 前端测试验证
- prompt-engineer: 提示词工程优化
- quant-analyst: 量化分析
- ui-ux-designer: UI/UX设计
...（根据你的项目自定义）

### 步骤 2 - 激活
如果任何技能为"是" → 立即使用 Skill() 工具激活
如果所有技能为"否" → 说明"不需要技能"并继续

### 步骤 3 - 实现
只有在步骤 2 完成后，才能开始实现。
`;

console.log(instructions);
```

### 3. Hooks 作用说明

这个 Hooks 的核心功能：
- **强制评估**：在每次任务开始前，强制评估是否需要使用 Skill
- **自动激活**：如果任务匹配某个 Skill，自动激活该 Skill
- **流程控制**：确保在开始实现前，先完成 Skill 评估和激活

### 4. Hooks 高级用法

#### 命名规范
- `skill-forced-eval.js` - 强制 Skill 评估
- `skill-context-inject.js` - Skill 上下文注入
- `skill-post-validate.js` - Skill 执行后验证

#### 执行时机
Hooks 会在以下时机触发：
- **Before**: 用户发送消息前
- **After**: AI 响应后
- **On**: 特定事件触发时

#### 配置示例

```javascript
// .claude/hooks/skill-context-inject.js
const injectSkillContext = (context) => {
  // 注入 Skill 相关的上下文信息
  return {
    ...context,
    availableSkills: [
      {
        name: 'skill-creator',
        description: '创建和生成自定义 Skill',
        keywords: ['创建skill', '生成skill', '新建skill']
      },
      {
        name: 'webapp-testing',
        description: '测试 Web 应用功能',
        keywords: ['测试', '验证', 'playwright']
      }
    ]
  };
};
```

### 5. Hooks 编写最佳实践

1. **明确的指令格式**：使用 Markdown 格式，结构清晰
2. **分步骤执行**：将复杂流程拆分为多个步骤
3. **明确的条件判断**：清楚说明何时触发，如何判断
4. **详细的技能列表**：列出所有可用的 Skill 及其用途
5. **错误处理**：考虑失败情况和回退机制

### 6. Hooks 调试技巧

```javascript
// 添加调试日志
console.log('[Hook Debug] 当前任务:', userTask);
console.log('[Hook Debug] 可用技能:', availableSkills);
console.log('[Hook Debug] 匹配结果:', matchResult);
```

---

## 三、Skill + Hooks + Agents 协同工作流程

### 完整工作流

```
用户请求
    ↓
[Hook: skill-forced-eval.js] - 评估是否需要 Skill
    ↓ (匹配)
[Skill] - 执行预定义流程
    ↓
[Agent] - 处理复杂任务
    ↓
[Result] - 返回结果
```

### 实际应用场景

#### 场景 1：创建新功能
1. 用户请求："创建一个用户评论功能"
2. Hook 评估：匹配到 `crud-development` 和 `api-development` Skill
3. 激活 Skill：使用这些 Skill 生成基础代码
4. Agent 补充：完善细节，处理边缘情况
5. 最终结果：完整的功能实现

#### 场景 2：测试功能
1. 用户请求："测试文章创建功能"
2. Hook 评估：匹配到 `webapp-testing` Skill
3. 激活 Skill：运行自动化测试
4. Agent 验证：分析测试结果，生成报告
5. 最终结果：测试报告和优化建议

---

## 四、项目中的 Skill 示例

### 当前项目可用 Skill

根据 `.iflow/` 目录结构，本项目包含以下 Skill：

1. **sequential-thinking** - 深度思考和分析
2. **task-manager** - 任务管理和拆分
3. **quality-reviewer** - 代码质量审查

### 自定义 Skill 创建建议

基于本项目特点，可以创建以下 Skill：

1. **wechat-publisher** - 微信公众号文章发布
2. **news-fetcher** - 热点新闻抓取
3. **article-generator** - AI 文章生成
4. **image-optimizer** - 图片处理和优化

---

## 五、常见问题

### Q1: Skill 创建失败怎么办？
A: 检查以下几点：
- 确保 skill-creator 正确安装
- 提供足够的上下文信息
- 确保流程可以手动执行成功
- 检查 Skill 语法是否符合规范

### Q2: Hooks 不生效？
A: 检查：
- 文件路径是否正确（`.claude/hooks/`）
- 文件名是否正确
- 语法是否有错误
- 重启 Claude Code

### Q3: 如何调试 Skill？
A: 使用以下方法：
- 在 Skill 中添加日志输出
- 逐步执行，查看中间结果
- 使用 Claude Code 的调试模式
- 检查 MCP 调用日志

---

## 六、最佳实践

### Skill 设计原则
1. **单一职责**：每个 Skill 只做一件事
2. **可复用**：设计为通用组件，可在多处使用
3. **文档完善**：提供清晰的说明和示例
4. **错误处理**：考虑异常情况
5. **版本管理**：维护 Skill 版本历史

### Hooks 设计原则
1. **轻量级**：保持逻辑简单，不拖慢性能
2. **可配置**：支持通过配置调整行为
3. **幂等性**：多次执行结果一致
4. **可测试**：易于测试和验证
5. **日志完善**：提供足够的调试信息

---

## 七、参考资料

- [Skill 官方文档](https://example.com/skill-docs)
- [Hooks 使用指南](https://example.com/hooks-guide)
- [Agents 协同实践](https://blog.csdn.net/xxx)

---

## 八、总结

通过合理使用 Skill 和 Hooks，可以大幅提升 AI 开发效率：

- **Skill**：封装复杂流程，提高复用性
- **Hooks**：自动化评估和激活，提高使用率
- **Agents**：处理复杂任务，补充智能能力

三者协同，构建高效的 AI 开发工作流。