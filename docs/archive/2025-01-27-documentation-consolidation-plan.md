# 文档整合执行计划

**日期**: 2025-01-27  
**执行者**: [documentation-agent]  
**预计完成时间**: 2-3 小时

## 🎯 目标

1. 将根目录文档从 9 个减少到 6 个
2. 消除 QQ Music API 文档的 SSOT 违规
3. 提升整体文档 SSOT 合规性从 70% 到 90%

---

## ✅ 阶段 1: 立即执行 (30 分钟)

### 任务 1.1: 标记归档文档 ✅ 已完成

- [x] 在 `QQ_MUSIC_API_SETUP_GUIDE.md` 顶部添加归档警告
- [x] 在 `NGINX_PROXY_SETUP.md` 顶部添加归档警告

### 任务 1.2: 移动文档到归档目录

```bash
# 执行命令
cd /Users/tr/Workspace/song-metadata-checker

# 移动到归档
git mv QQ_MUSIC_API_SETUP_GUIDE.md docs/archive/
git mv NGINX_PROXY_SETUP.md docs/archive/
```

### 任务 1.3: 更新文档索引

更新 `docs/archive/README.md`:

```markdown
## 2025-01-27 归档

### QQ_MUSIC_API_SETUP_GUIDE.md
- **归档原因**: 内容已整合到 services/qqmusic-api/CONTAINER_SETUP.md
- **替代文档**: [services/qqmusic-api/CONTAINER_SETUP.md](../../services/qqmusic-api/CONTAINER_SETUP.md)

### NGINX_PROXY_SETUP.md
- **归档原因**: 内容已整合到 docs/guides/DIFY_CLOUD_QUICK_START.md
- **替代文档**: [docs/guides/DIFY_CLOUD_QUICK_START.md](../guides/DIFY_CLOUD_QUICK_START.md)
```

---

## 📋 阶段 2: 删除重复文档 (15 分钟)

### 任务 2.1: 删除 services/qqmusic-api/QUICK_START.md

**原因**: 与 `CONTAINER_SETUP.md` 高度重复

```bash
# 检查文件是否被引用
grep -r "QUICK_START.md" docs/ services/ README.md

# 如果没有引用，直接删除
git rm services/qqmusic-api/QUICK_START.md
```

---

## 🔗 阶段 3: 更新引用链接 (30 分钟)

### 任务 3.1: 搜索所有引用

```bash
# 搜索 QQ_MUSIC_API_SETUP_GUIDE 的引用
grep -r "QQ_MUSIC_API_SETUP_GUIDE" docs/ services/ README.md

# 搜索 NGINX_PROXY_SETUP 的引用
grep -r "NGINX_PROXY_SETUP" docs/ services/ README.md
```

### 任务 3.2: 更新引用

需要更新的文件（预计）:

- `README.md` - 如果有引用
- `docs/README.md` - 如果有引用
- `docs/guides/DEPLOYMENT.md` - 可能引用 Nginx 设置
- `docs/guides/DIFY_CLOUD_TROUBLESHOOTING.md` - 可能引用 Nginx

**更新模式**:

```markdown
<!-- 旧链接 -->
[QQ Music API 设置](../QQ_MUSIC_API_SETUP_GUIDE.md)

<!-- 新链接 -->
[QQ Music API 设置](services/qqmusic-api/CONTAINER_SETUP.md)
```

---

## 📝 阶段 4: 更新 FIXES_INDEX.md (10 分钟)

添加新条目:

```markdown
### [Documentation Consolidation](archive/2025-01-27-documentation-consolidation-analysis.md)

**Date**: 2025-01-27  
**Impact**: High  
**Status**: ✅ 已完成  
**Summary**: Consolidated QQ Music API documentation from 6 files to 2 authoritative files. Moved root-level technical guides to appropriate locations.

**Key Actions**:
- Archived `QQ_MUSIC_API_SETUP_GUIDE.md` and `NGINX_PROXY_SETUP.md`
- Deleted duplicate `QUICK_START.md`
- Updated all references to point to authoritative documents

[Read detailed analysis →](archive/2025-01-27-documentation-consolidation-analysis.md)
```

---

## 🧪 阶段 5: 验证 (15 分钟)

### 任务 5.1: 检查断链

```bash
# 使用 markdown-link-check 或手动检查
find docs/ -name "*.md" -exec grep -l "QQ_MUSIC_API_SETUP_GUIDE\|NGINX_PROXY_SETUP" {} \;
```

### 任务 5.2: 验证根目录

```bash
# 确认根目录只有 6 个核心文档
ls -1 *.md
# 应该只看到:
# README.md
# AGENTS.md
# CHANGELOG.md
# CLAUDE.md
# GEMINI.md
# codex.md
```

### 任务 5.3: 运行文档审查

```bash
# 运行文档审查工作流
/doc-review
```

---

## 📊 预期结果

### 文档数量

| 位置 | 之前 | 之后 | 变化 |
|------|------|------|------|
| 根目录 | 9 | 6 | -3 |
| docs/guides/ | 8 | 7 | -1 |
| services/qqmusic-api/ | 3 | 2 | -1 |
| docs/archive/ | 15 | 17 | +2 |

### SSOT 合规性

| 主题 | 之前 | 之后 |
|------|------|------|
| QQ Music API | ❌ 6 个文档 | ✅ 2 个权威 |
| Nginx 代理 | ⚠️ 2 个文档 | ✅ 1 个权威 |
| 整体合规性 | 70% | 90% |

---

## 🔄 后续建议

### 下周执行

1. **精简 DIFY_CLOUD_QUICK_START.md**
   - 移除详细步骤
   - 保留概览 + 链接到 MANUAL_SETUP.md

2. **移动 PROJECT_STATUS.md**
   - 从根目录移至 `docs/`
   - 更新 README.md 中的链接

### 下月执行

3. **审查归档文档**
   - 确保所有归档文档有弃用警告
   - 考虑删除 2024 年之前的归档文档

4. **创建文档维护检查清单**
   - 添加到 `.windsurf/workflows/`
   - 每季度运行一次

---

## ✅ 完成检查清单

- [ ] 阶段 1: 标记和移动归档文档
- [ ] 阶段 2: 删除重复文档
- [ ] 阶段 3: 更新所有引用链接
- [ ] 阶段 4: 更新 FIXES_INDEX.md
- [ ] 阶段 5: 验证和测试
- [ ] Git 提交: `docs: consolidate QQ Music API and Nginx documentation`

---

**创建时间**: 2025-01-27  
**预计完成**: 2025-01-27  
**实际完成**: _待填写_
