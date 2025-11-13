# snakemake_without_snakefile

基于 [snakemake/snakemake](https://github.com/snakemake/snakemake) ，支持通过字符串直接定义和运行工作流，无需创建 Snakefile 文件。

## 相对原版的改动

### ✨ 新增功能

1. **StringSourceFile 类** (sourcecache.py:105-142)
   - 实现了在内存中存储 Snakefile 内容的 SourceFile 对象
   - 支持将字符串作为工作流定义的来源

2. **Workflow.include_string() 方法** (workflow.py:1667-1710)
   - 允许直接从字符串加载 Snakefile 内容
   - 支持完整的 Snakefile 语法和功能
   - 可选的调试模式（打印编译后的代码）

3. **Bug 修复** (api.py:610-612)
   - 修复了直接使用 `scheduler='greedy'` 时 `scheduler_settings` 未初始化的问题

### ❌ 移除的内容

为了专注于核心库功能，移除了以下内容：

- 文档目录 (docs/, apidocs/)
- 测试套件 (tests/)
- 示例项目 (examples/)
- CI/CD 配置 (.github/)
- 部分开发工具配置

**注意**：保留了 `unit_tests/` 模块，用于支持 Snakemake 的内置测试功能。

### ✅ 保留的功能

- 完整的 Snakemake 工作流引擎
- 所有调度器（greedy, MILP）
- 16 种远程存储协议支持
- Conda 和 Singularity 环境管理
- 报告生成和 GUI 界面
- 命令行工具

## 许可证

MIT License - 与原版 Snakemake 相同
