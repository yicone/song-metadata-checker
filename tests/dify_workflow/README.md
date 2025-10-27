# Dify Workflow 节点单元测试

> **测试覆盖**: `dify-workflow/nodes/code-nodes/` 中的所有 Python 代码节点

---

## 📁 测试文件

| 测试文件 | 被测节点 | 测试数量 |
|---------|---------|---------|
| `test_parse_url.py` | `parse_url.py` | 7 |
| `test_find_qqmusic_match.py` | `find_qqmusic_match.py` | 7 |
| `test_parse_qqmusic_response.py` | `parse_qqmusic_response.py` | 8 |
| `test_parse_cover_url.py` | `parse_cover_url.py` | 6 |
| `test_parse_gemini_response.py` | `parse_gemini_response.py` | 7 |
| `test_consolidate.py` | `consolidate.py` | 11 |

**总计**: 46 个测试用例

---

## 🚀 运行测试

### 运行所有测试

```bash
# 使用 pytest
poetry run pytest tests/dify_workflow/ -v

# 或使用 python -m pytest
poetry run python -m pytest tests/dify_workflow/ -v
```

### 运行单个测试文件

```bash
# 测试 parse_url 节点
poetry run pytest tests/dify_workflow/test_parse_url.py -v

# 测试 consolidate 节点
poetry run pytest tests/dify_workflow/test_consolidate.py -v
```

### 运行特定测试

```bash
# 运行特定的测试方法
poetry run pytest tests/dify_workflow/test_parse_url.py::TestParseUrl::test_parse_url_with_hash -v
```

### 查看测试覆盖率

```bash
# 生成覆盖率报告
poetry run pytest tests/dify_workflow/ --cov=dify-workflow/nodes/code-nodes --cov-report=html

# 查看报告
open htmlcov/index.html
```

---

## 📊 测试覆盖说明

### 1. parse_url.py

**测试场景**:

- ✅ 带 `#` 的 URL
- ✅ 不带 `#` 的 URL
- ✅ 带 `#/` 的 URL
- ✅ 缺少 `id` 参数
- ✅ 无效的 URL 格式
- ✅ 空字符串

---

### 2. find_qqmusic_match.py

**测试场景**:

- ✅ 有搜索结果
- ✅ 无搜索结果
- ✅ 字典输入（已解析）
- ✅ 字符串输入（JSON）
- ✅ 无效的 JSON
- ✅ 缺少 `song` 键
- ✅ 多个结果（返回第一个）

---

### 3. parse_qqmusic_response.py

**测试场景**:

- ✅ 新版代理格式
- ✅ 旧版代理格式
- ✅ 字典输入
- ✅ 带 `body` 包装
- ✅ 无效的 JSON
- ✅ 空响应
- ✅ 缺少字段

---

### 4. parse_cover_url.py

**测试场景**:

- ✅ 有效的响应
- ✅ 字典输入
- ✅ 缺少 `imageUrl` 字段
- ✅ 空响应
- ✅ 无效的 JSON
- ✅ 空的 `imageUrl`

---

### 5. parse_gemini_response.py

**测试场景**:

- ✅ 带 markdown 代码块
- ✅ 不带 markdown 代码块
- ✅ 字典输入
- ✅ 缺少 `candidates` 字段
- ✅ 无效的 JSON
- ✅ 空响应
- ✅ 复杂的差异列表

---

### 6. consolidate.py

**测试场景**:

- ✅ 基本数据整合
- ✅ 标题匹配/不匹配
- ✅ 时长在容差内/外
- ✅ 歌词比较
- ✅ Gemini 封面图比较（相同/不同）
- ✅ 艺术家比较
- ✅ 摘要统计
- ✅ 错误处理

---

## 🎯 测试原则

### 1. 边界条件

每个测试都覆盖：

- ✅ 正常输入
- ✅ 空输入
- ✅ 无效输入
- ✅ 缺少字段

### 2. 数据格式

测试多种输入格式：

- ✅ JSON 字符串
- ✅ Python 字典
- ✅ 带包装的响应

### 3. 错误处理

验证错误情况：

- ✅ 返回 `success: False`
- ✅ 返回有意义的 `error` 消息
- ✅ 不抛出异常

---

## 🔧 添加新测试

### 模板

```python
"""
测试 your_node 节点
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dify-workflow" / "nodes" / "code-nodes"))

from your_node import main


class TestYourNode:
    """测试 Your Node 节点"""

    def test_basic_case(self):
        """测试基本情况"""
        result = main(input_data)
        
        assert result['success'] is True
        assert result['expected_field'] == expected_value

    def test_error_case(self):
        """测试错误情况"""
        result = main(invalid_input)
        
        assert result['success'] is False
        assert result['error'] != ""
```

---

## 📚 相关文档

- **[pytest 文档](https://docs.pytest.org/)** - 测试框架
- **[DIFY_CLOUD_MANUAL_SETUP.md](../../docs/guides/DIFY_CLOUD_MANUAL_SETUP.md)** - 节点功能说明
- **[SYNC_WITH_MANUAL_SETUP.md](../../dify-workflow/SYNC_WITH_MANUAL_SETUP.md)** - 节点同步说明

---

## ✅ 持续集成

### GitHub Actions 示例

```yaml
name: Test Dify Workflow Nodes

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pytest tests/dify_workflow/ -v
```

---

**创建时间**: 2025-10-27  
**维护者**: [documentation-agent]  
**测试框架**: pytest
