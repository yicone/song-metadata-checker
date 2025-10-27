# 文档防重复指南

> **目标**: 防止 AI agents 创建大量标题相近的重复文档  
> **受众**: [documentation-agent] 和所有文档贡献者  
> **日期**: 2025-10-27

## 🚨 问题说明

### 发现的问题

在 2025-10-27 的文档更新中，发现了重复内容：

1. **故障排除内容重复**:
   - 已存在: `docs/guides/DIFY_CLOUD_TROUBLESHOOTING.md` (542 行)
   - 新创建: `docs/guides/DIFY_CLOUD_MANUAL_SETUP.md` 中的故障排除章节 (116 行)
   - **结果**: 内容重复，维护成本增加

2. **总结文档过多**:
   - `DIFY_WORKFLOW_SETUP_UPDATE_SUMMARY.md`
   - `DIFY_CLOUD_MANUAL_SETUP_UPDATE_SUMMARY.md`
   - `GEMINI_NODE_ADDITION_SUMMARY.md`
   - `QQMUSIC_API_FIX_SUMMARY.md`
   - **问题**: 4 个 summary 文档，标题相近，难以区分

### 根本原因

1. **AI agent 未检查现有文档**: 在创建新内容前没有搜索类似文档
2. **缺乏明确的决策树**: 何时创建新文档 vs 更新现有文档
3. **命名规范不够严格**: 允许 `*_SUMMARY.md` 等相似命名

---

## ✅ 解决方案

### 1. 更新文档管理指南

**文件**: `docs/DOCUMENTATION_MANAGEMENT.md`

**新增章节**: "Document Creation Decision Tree"

**内容**:

- 创建文档前的检查清单
- 决策矩阵（何时创建 vs 更新）
- 常见重复模式及避免方法
- AI agent 专用指南

### 2. 更新 AGENTS.md

**文件**: `AGENTS.md`

**新增**: "Document Creation Rules (CRITICAL)"

**关键规则**:

1. 创建前必须搜索: `find docs/ -name "*KEYWORD*"`
2. 决策树: 存在相似文档 → 更新，不存在 → 创建
3. 常见错误示例
4. 链接到完整指南

### 3. 修复当前重复

**已完成**:

- ✅ 从 `DIFY_CLOUD_MANUAL_SETUP.md` 删除重复的故障排除内容
- ✅ 添加链接指向 `DIFY_CLOUD_TROUBLESHOOTING.md`
- ✅ 在 `DIFY_CLOUD_TROUBLESHOOTING.md` 添加问题 6（双重 JSON 编码）

---

## 📋 AI Agent 检查清单

### 在创建任何文档之前

```bash
# 1. 搜索相似主题
grep -ri "troubleshooting" docs/
grep -ri "setup" docs/
grep -ri "summary" docs/

# 2. 列出相关目录
ls -la docs/guides/
ls -la docs/

# 3. 检查命名模式
find docs/ -name "*KEYWORD*"
```

### 决策流程

```
┌─────────────────────────────┐
│ 需要添加文档内容？           │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 搜索现有文档                 │
│ grep -ri "topic" docs/      │
└─────────────┬───────────────┘
              │
              ▼
      ┌───────┴───────┐
      │ 找到相似文档？  │
      └───┬───────┬───┘
          │       │
        是│       │否
          │       │
          ▼       ▼
    ┌─────────┐ ┌──────────┐
    │ 更新现有 │ │ 创建新文档 │
    │ 文档    │ │          │
    └─────────┘ └──────────┘
          │            │
          ▼            ▼
    ┌─────────────────────┐
    │ 更新索引文件         │
    │ 检查链接            │
    │ 验证 SSOT           │
    └─────────────────────┘
```

### 常见场景

| 场景 | 现有文档 | 操作 |
|------|---------|------|
| 添加故障排除 | `TROUBLESHOOTING.md` 存在 | ✅ 添加新问题到现有文档 ❌ 不创建新文档 |
| 添加设置步骤 | `SETUP.md` 存在 | ✅ 添加新步骤到现有文档 ❌ 不创建 `SETUP_GUIDE.md` |
| 记录修复 | `FIXES_INDEX.md` 存在 | ✅ 添加条目到索引 ✅ 创建详细文档在 `fixes/` ❌ 不创建 `FIXES_SUMMARY.md` |
| 全新主题 | 无相关文档 | ✅ 创建新文档 ✅ 更新 `docs/README.md` |

---

## 🎯 命名规范

### 避免的命名模式

❌ **不要创建**:

- `*_SUMMARY.md` (除非是索引文件)
- `*_GUIDE.md` (如果已有 `*.md`)
- `*_TROUBLESHOOTING.md` (如果已有通用 `TROUBLESHOOTING.md`)
- `*_UPDATE_*.md` (临时文档，应整合到主文档)

✅ **推荐**:

- `TOPIC.md` (主文档)
- `TOPIC_INDEX.md` (索引文件)
- `guides/TOPIC.md` (指南)
- `fixes/YYYY-MM-DD-description.md` (修复记录)

### 文档类型与命名

| 类型 | 命名模式 | 示例 | 数量限制 |
|------|---------|------|---------|
| 主文档 | `TOPIC.md` | `DEPLOYMENT.md` | 每主题 1 个 |
| 索引 | `TOPIC_INDEX.md` | `FIXES_INDEX.md` | 每类别 1 个 |
| 指南 | `guides/TOPIC.md` | `guides/SETUP.md` | 按需 |
| 修复 | `fixes/YYYY-MM-DD-*.md` | `fixes/2025-01-27-fix.md` | 无限制 |
| 总结 | ❌ 避免 | - | 0 |

---

## 🔧 重复文档处理流程

### 发现重复时

1. **识别权威文档**:
   - 最完整
   - 最新
   - 最有组织

2. **合并内容**:
   - 将独特内容合并到权威文档
   - 保留所有有价值的信息

3. **更新链接**:

   ```bash
   # 查找所有引用
   grep -r "duplicate-doc.md" docs/
   
   # 更新为权威文档
   ```

4. **删除或归档**:
   - 删除重复文档
   - 或移动到 `docs/archive/` 并添加重定向说明

5. **更新索引**:
   - 更新 `docs/README.md`
   - 更新相关索引文件

### 示例：处理故障排除重复

**发现**:

- `DIFY_CLOUD_MANUAL_SETUP.md` 包含故障排除章节
- `DIFY_CLOUD_TROUBLESHOOTING.md` 已存在

**处理**:

1. ✅ 识别 `DIFY_CLOUD_TROUBLESHOOTING.md` 为权威
2. ✅ 从 `MANUAL_SETUP.md` 删除重复内容
3. ✅ 添加链接指向 `TROUBLESHOOTING.md`
4. ✅ 在 `TROUBLESHOOTING.md` 添加新问题

---

## 📊 文档结构最佳实践

### 推荐结构

```
docs/
├── README.md                          # 文档导航
├── FIXES_INDEX.md                     # 修复索引（唯一）
├── DOCUMENTATION_MANAGEMENT.md        # 文档管理指南（唯一）
│
├── guides/                            # 指南目录
│   ├── DIFY_CLOUD_MANUAL_SETUP.md    # 设置指南
│   └── DIFY_CLOUD_TROUBLESHOOTING.md # 故障排除（唯一）
│
└── fixes/                             # 详细修复记录
    └── YYYY-MM-DD-*.md
```

### 避免的结构

```
docs/
├── TROUBLESHOOTING.md                 # ❌
├── COMMON_ISSUES.md                   # ❌ 重复
├── PROBLEM_SOLVING.md                 # ❌ 重复
│
├── FIXES_INDEX.md                     # ✅
├── FIXES_SUMMARY.md                   # ❌ 重复
├── BUG_FIXES_LIST.md                  # ❌ 重复
│
└── guides/
    ├── SETUP.md                       # ✅
    ├── SETUP_GUIDE.md                 # ❌ 重复
    └── MANUAL_SETUP.md                # ❌ 重复
```

---

## 🎓 学习案例

### 案例 1: 故障排除重复

**错误做法**:

```
# 在 MANUAL_SETUP.md 中添加 116 行故障排除内容
# 而 TROUBLESHOOTING.md 已经存在 542 行
```

**正确做法**:

```
# 在 MANUAL_SETUP.md 中：
## 故障排除
请查看 [完整故障排除指南](TROUBLESHOOTING.md)

# 在 TROUBLESHOOTING.md 中：
添加新问题到现有列表
```

### 案例 2: 总结文档过多

**错误做法**:

```
创建 4 个 *_SUMMARY.md 文档
```

**正确做法**:

```
# 选项 A: 整合到主文档
在 DIFY_CLOUD_MANUAL_SETUP.md 顶部添加"更新说明"章节

# 选项 B: 使用 CHANGELOG.md
在 CHANGELOG.md 中记录所有更新

# 选项 C: 临时文档
创建后及时整合到主文档，然后删除
```

---

## 📚 相关文档

- [DOCUMENTATION_MANAGEMENT.md](DOCUMENTATION_MANAGEMENT.md) - 完整文档管理指南
- [AGENTS.md](../AGENTS.md) - AI agent 协作指南
- [NAMING_CONVENTIONS.md](NAMING_CONVENTIONS.md) - 命名规范

---

## ✅ 验收标准

**文档创建前**:

- [ ] 已搜索现有相似文档
- [ ] 已检查命名冲突
- [ ] 已确认需要新文档（不是更新现有）

**文档创建后**:

- [ ] 已更新索引文件
- [ ] 已更新 `docs/README.md`
- [ ] 已验证无重复内容
- [ ] 已检查所有链接

**定期审查**:

- [ ] 每月检查重复文档
- [ ] 每季度整合临时文档
- [ ] 持续维护 SSOT 原则

---

**创建时间**: 2025-10-27  
**维护者**: [documentation-agent]  
**状态**: ✅ 活跃使用
