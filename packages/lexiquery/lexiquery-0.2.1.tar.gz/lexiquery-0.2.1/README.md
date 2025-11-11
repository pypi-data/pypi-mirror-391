# LexiQuery

🌐 **Language / 语言** · [English](#english-version) | [中文](#中文版本)

---

## English Version

### ✨ Highlights
- 🔀 **Boolean logic**: Parentheses > `NOT` > (`AND`/`OR`/`XOR` evaluated left-to-right) for predictable chains.
- ⛓️ **Comma chains**: `alpha, foo BEF/1 bar` evaluates each segment like implicit `AND`.
- 📍 **Positional windows**: `BEF`, `AFT`, `NEAR` accept `/n`, `/m-n`, or `/*`, and can chain `IN(...)` (all targets) / `INOF(...)` (any target).
- 📏 **Length guards**: `LEN/3-10` for token counts, `SIZE/32-128` for byte ranges.
- 🎯 **Match helpers**: `ONLY`, `LIKE`, `STR`, `END` cover set equality, fuzzy presence, and start/end checks.
- 🃏 **Wildcards**: `foo*` or `foo *` match every token sharing the prefix.
- 📚 **Docs**: Detailed syntax in `LANGUAGE_MANUAL.md`.

### 🚀 Quickstart
```python
from lexiquery import LexiQueryExpression

expr = LexiQueryExpression(
    "(foo XOR bar) AND LEN/3-10 AND foo BEF/2 IN(bar baz)"
)

expr.query("foo baz qux")      # True
expr.query("bar foo baz qux")  # False
```

```python
from lexiquery import LexiQuery

engine = LexiQuery("foo bar baz qux")
assert engine.query("foo BEF/2 bar")
```

### 📦 Install
```bash
python -m pip install lexiquery
```

### 🧪 Tests
```bash
PYTHONPATH=src pytest
```

### 🧩 Syntax Cheat Sheet
| Category | Example |
|----------|---------|
| Boolean  | `(foo OR bar) AND NOT baz` |
| Positional | `alpha BEF/2-4 beta`, `foo AFT/* bar`, `foo NEAR/3 beta` |
| Positional + Sets | `foo BEF/3 IN(bar baz)`, `foo BEF/* INOF(alpha beta)` |
| Length | `LEN/5-10 AND foo BEF/2 bar`, `NOT SIZE/32` |
| Match | `LIKE foo bar`, `ONLY foo bar`, `STR hello world`, `END goodbye` |
| Wildcard | `foo* NEAR/1 bar`, `NOT app*` |

More samples in `tests/test_core.py` & `tests/test_new_ops.py`.

### 📄 License
MIT License.

---

## 中文版本

### ✨ 功能亮点
- 🔀 **布尔优先级**：括号 > `NOT` > (`AND`/`OR`/`XOR` 左到右计算)，更贴近自然阅读。
- ⛓️ **多段表达式**：使用逗号分段，如 `alpha, foo BEF/1 bar`，效果等同连续 `AND`。
- 📍 **位置窗口**：`BEF`、`AFT`、`NEAR` 支持 `/n`、`/m-n`、`/*`，还能链式追加 `IN(...)`（全部满足）或 `INOF(...)`（任一满足）。
- 📏 **长度约束**：`LEN/3-10` 控制词数，`SIZE/32-128` 控制字节长度。
- 🎯 **匹配运算**：`ONLY`、`LIKE`、`STR`、`END` 覆盖集合判断与首尾匹配。
- 🃏 **通配符**：`foo*` / `foo *` 匹配所有以 `foo` 开头的 token。
- 📚 **文档**：详尽语法见 `LANGUAGE_MANUAL.md`。

### 🚀 快速体验
```python
from lexiquery import LexiQueryExpression

expr = LexiQueryExpression(
    "(foo XOR bar) AND LEN/3-10 AND foo BEF/2 IN(bar baz)"
)

expr.query("foo baz qux")      # True
expr.query("bar foo baz qux")  # False
```

```python
from lexiquery import LexiQuery

engine = LexiQuery("foo bar baz qux")
assert engine.query("foo BEF/2 bar")
```
### 📦 安装
```bash
python -m pip install lexiquery
```


### 🧪 运行测试
```bash
PYTHONPATH=. pytest
```

### 🧩 语法速查
| 分类 | 示例 |
|------|------|
| 布尔 | `(foo OR bar) AND NOT baz` |
| 位置 | `alpha BEF/2-4 beta`、`foo AFT/* bar`、`foo NEAR/3 beta` |
| 位置 + 集合 | `foo BEF/3 IN(bar baz)`、`foo BEF/* INOF(alpha beta)` |
| 长度 | `LEN/5-10 AND foo BEF/2 bar`、`NOT SIZE/32` |
| 匹配 | `LIKE foo bar`、`ONLY foo bar`、`STR hello world`、`END goodbye` |
| 通配 | `foo* NEAR/1 bar`、`NOT app*` |

更多示例请参考 `tests/test_core.py` 与 `tests/test_new_ops.py`。

### 📄 许可
MIT 许可证。
