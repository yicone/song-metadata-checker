---
description: 文档审查检查清单 - 确保文档一致性和准确性
---

# 文档审查检查清单

本工作流程用于审查文档更新，确保符合项目文档管理规范。

## 何时使用

- 更新 API 端点或配置
- 修改架构或部署方式
- 添加或修改功能
- 发现文档不一致时

## 审查步骤

### 1. 技术细节一致性检查

#### 端口号检查

```bash
# 搜索所有端口引用
grep -r "3200\|3300\|3001" docs/ services/ --exclude-dir=node_modules --exclude-dir=archive

# 验证：
# - 3200: Rain120 容器内端口
# - 3300: Rain120 主机映射端口
# - 3001: 代理层端口（推荐使用）
```

#### API 端点检查

```bash
# 搜索 QQ Music API 端点
grep -r "/search\|/song\|getSearchByKey\|getSongInfo" docs/ services/ --exclude-dir=node_modules --exclude-dir=archive

# 验证：
# Rain120 端点: /getSearchByKey, /getSongInfo
# 代理层端点: /search, /song
```

#### 环境变量检查

```bash
# 搜索 QQ Music API 配置
grep -r "QQ_MUSIC_API_HOST\|QQMUSIC_API_BASE" docs/ services/ --exclude-dir=node_modules --exclude-dir=archive

# 验证：
# 应用层: QQ_MUSIC_API_HOST=http://localhost:3001
# 代理层: QQMUSIC_API_BASE=http://qqmusic-upstream:3200
```

### 2. SSoT (单一事实来源) 检查

#### 确认权威文档

- **QQ Music API 设置**: `services/qqmusic-api/CONTAINER_SETUP.md`
- **QQ Music API 概述**: `services/qqmusic-api/README.md`
- **项目部署**: `docs/guides/DEPLOYMENT.md`
- **功能规范**: `docs/FUNCTIONAL_SPEC.md`

#### 检查重复内容

```bash
# 搜索可能重复的配置说明
grep -r "QQ.*Music.*API.*Setup\|QQ.*音乐.*配置" docs/ --include="*.md"

# 如果发现重复：
# 1. 保留权威文档的完整内容
# 2. 其他文档改为链接到权威文档
# 3. 或添加简短摘要 + 链接
```

### 3. 链接有效性检查

```bash
# 检查内部链接
# 使用 markdown-link-check 或手动验证

# 验证所有相对路径链接
grep -r "\[.*\](\.\./" docs/ --include="*.md"

# 确保：
# - 路径正确
# - 目标文件存在
# - 锚点（如果有）存在
```

### 4. 归档文档检查

```bash
# 检查归档文档是否有弃用警告
for file in docs/archive/*.md; do
  if ! head -20 "$file" | grep -q "ARCHIVED\|已归档\|DEPRECATED\|已过时"; then
    echo "⚠️  Missing deprecation warning: $file"
  fi
done
```

### 5. 文档元数据检查

每个主要文档应包含：

- [ ] 标题清晰
- [ ] 目的/概述说明
- [ ] 最后更新日期（如适用）
- [ ] 相关文档链接
- [ ] 适当的章节结构

### 6. 代码示例验证

对于包含代码示例的文档：

- [ ] 端口号正确
- [ ] 端点路径正确
- [ ] 环境变量名称正确
- [ ] 命令可以实际运行（或标注为示例）

## 常见问题模式

### 端口号混淆

**问题**: 文档中混用 3200, 3300, 3001 而不说明

**解决**:
- 明确说明每个端口的用途
- 使用表格展示端口映射
- 推荐使用代理层 (3001)

### 端点路径过时

**问题**: 使用旧的端点路径 `/search/song` 而不是 `/getSearchByKey`

**解决**:
- 更新为正确的端点
- 如果是权威文档，添加端点对照表
- 如果是归档文档，添加弃用警告

### 环境变量不一致

**问题**: 不同文档推荐不同的环境变量值

**解决**:
- 确认正确的配置
- 更新所有文档使用一致的推荐值
- 说明为什么推荐该值

## 修复流程

发现问题后：

1. **评估影响范围**
   ```bash
   # 搜索所有受影响的文件
   grep -r "错误的内容" docs/ services/
   ```

2. **创建修复文档**
   - 在 `docs/fixes/` 创建详细的修复文档
   - 使用格式: `YYYY-MM-DD-description.md`

3. **更新 FIXES_INDEX.md**
   - 添加修复摘要
   - 链接到详细文档

4. **执行修复**
   - 按优先级修复文档
   - 高优先级: 用户直接使用的文档
   - 中优先级: 开发者参考文档
   - 低优先级: 归档文档

5. **验证修复**
   - 重新运行检查命令
   - 确认所有问题已解决

## 预防措施

### 代码变更时

- [ ] 更新相关文档
- [ ] 运行本检查清单
- [ ] 提交时包含文档更新

### 定期审查

- [ ] 每月运行完整检查
- [ ] 更新过时的截图/示例
- [ ] 验证所有链接有效

### 新文档创建时

- [ ] 确认是否与现有文档重复
- [ ] 如果重复，考虑合并或链接
- [ ] 遵循命名约定
- [ ] 添加到适当的索引

## 工具和资源

- **Markdown Linter**: 检查 Markdown 格式
- **Link Checker**: 验证链接有效性
- **Grep/Ripgrep**: 搜索文档内容
- **Diff Tools**: 比较文档版本

## 相关文档

- [文档管理规范](../../docs/DOCUMENTATION_MANAGEMENT.md)
- [命名约定](../../docs/NAMING_CONVENTIONS.md)
- [修复索引](../../docs/FIXES_INDEX.md)
