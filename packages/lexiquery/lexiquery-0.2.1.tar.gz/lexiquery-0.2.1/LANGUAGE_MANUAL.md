# LexiQuery Language Manual / 语法手册

🌐 **Language / 语言** · [English](#english-guide) | [中文](#中文指南)

---

## English Guide

### 📌 Version Info
- Version: **v2025.11.11**

### 1️⃣ Foundations
- **Expressions**: sequences of minimal expressions + operators evaluated to `True/False`.
- **Parentheses**: override default precedence, especially when mixing booleans with positional clauses.
- **Comma chains**: separate full expressions with `,` to implicitly require every segment (`alpha, foo BEF/1 bar`).

#### 🔤 Lowercase Rule
- Reserved words stay uppercase (`AND`, `OR`, `NOT`, `XOR`, `NEAR`, `BEF`, `AFT`, `ONLY`, `LIKE`, `STR`, `END`, `LEN`, `SIZE`, `IN`, `INOF`).
- All other literals must be lowercase: search for “Apple” using `apple`.

#### ⛔ Omission Rule
- Only `/` (distance) and `*` (suffix wildcard) are allowed; drop every other symbol (`!@#$…`).

#### 🪙 Minimal vs Wildcard Expressions
- Minimal: `apple`
- Wildcard: `app*` → matches `apple`, `application`, `approve`.

### 2️⃣ Operator Reference

#### 🔀 Boolean
| Operator | Description | Example |
|----------|-------------|---------|
| `AND` | both operands true | `apple AND orange` |
| `OR` | at least one true | `apple OR orange` |
| `NOT` | negates following expression | `NOT orange` |
| `XOR` | exactly one true | `foo XOR bar` |

Rules: `AND`/`OR` must sit between expressions; `NOT` always prefixes the subexpression it negates.

#### 📍 Positional
| Operator | Meaning | Example |
|----------|---------|---------|
| `NEAR/n` | tokens within `n` positions (default 1) | `apple NEAR/5 orange` |
| `BEF/n`  | left token before right token | `apple BEF/4 orange` |
| `AFT/n`  | left token after right token | `apple AFT/3 orange` |

- Supports ranges: `foo BEF/2-4 bar`.
- `/*` means unlimited window: `foo AFT/* bar`.
- Chain **set operators**: `foo BEF/2 IN(bar baz)` (all targets) or `foo BEF/* INOF(alpha beta)` (any target).

#### 🎯 Match Operators
| Operator | Description | Example |
|----------|-------------|---------|
| `ONLY` | document equals listed tokens | `ONLY apple` |
| `LIKE` | document contains all listed tokens | `LIKE app orang` |
| `STR` | document starts with sequence | `STR apple` |
| `END` | document ends with sequence | `END apple` |

#### 📏 Length Operators
- `LEN/3` → ≤3 tokens.
- `LEN/5-10` → token count between 5 and 10.
- `SIZE/32-64` → byte-length window.
- Combine freely: `LEN/5-10 AND foo BEF/2 bar`, `NOT SIZE/100`.

### 3️⃣ Usage Examples
- Exact vs wildcard: `apple`, `app* AND NOT apple`.
- Boolean combos: `(foo OR bar) AND NOT baz`, `(foo XOR bar) OR (baz AND qux)`.
- Positional: `foo NEAR/* bar`, `(foo BEF/3 baz) XOR (alpha NEAR/2 beta)`.
- Length + positional: `LEN/5-20 AND foo BEF/2 IN(bar baz)`.
- Match chaining: `STR hello world AND END goodbye`, `LIKE foo bar baz`.

### 4️⃣ Operator Precedence
1. Parentheses
2. Unary `NOT`
3. Binary boolean chains (`AND`/`OR`/`XOR`) evaluated strictly left-to-right
4. Positional + match operators (already self-contained expressions)

Examples:
- `apple OR orange AND banana` → `(apple OR orange) AND banana`
- `apple NEAR orange AND LIKE bana` → `AND` first, then evaluate positional/match clauses.
- `(foo XOR bar) AND LEN/3-10, foo BEF/2 IN(bar baz)` shows commas chaining full expressions.

### 5️⃣ Best Practices
1. ✅ Normalize text (lowercase + strip punctuation) before indexing.
2. 🧠 Favor parentheses to highlight intent.
3. 🧪 Validate via `LexiQueryExpression(expr)` before deploying.
4. 🎯 Limit wildcards; pair with positional ranges for precision.
5. 🧾 Keep expressions positive when possible; reserve `NOT` for unavoidable exclusions.

---

## 中文指南

### 📌 版本信息
- 版本：**v2025.11.11**


### 1️⃣ 基础概念
- **表达式**：由最小表达式和运算符组成，结果为 `True/False`。
- **括号**：可改变默认优先级，尤其在布尔与位置操作混合时更清晰。
- **多段逗号**：用 `,` 串联完整表达式，等价于逐个 `AND` 约束，如 `alpha, foo BEF/1 bar`。

#### 🔤 小写规则
- 保留字使用大写（`AND`、`OR`、`NOT`、`XOR`、`NEAR`、`BEF`、`AFT`、`ONLY`、`LIKE`、`STR`、`END`、`LEN`、`SIZE`、`IN`、`INOF`）。
- 其他字面量全部使用小写，例如 “Apple” 写作 `apple`。

#### ⛔ 省略规则
- 表达式中仅允许 `/`（距离）与 `*`（后缀通配），其余符号 `!@#$…` 全部省略，避免解析歧义。

#### 🪙 最小表达式与通配表达式
- 最小表达式：`apple`
- 通配表达式：`app*`，可匹配 `apple`、`application`、`approve` 等。

### 2️⃣ 运算符速览

#### 🔀 布尔运算
| 运算符 | 说明 | 示例 |
|--------|------|------|
| `AND` | 两侧表达式都需满足 | `apple AND orange` |
| `OR`  | 至少一侧满足 | `apple OR orange` |
| `NOT` | 否定紧随其后的表达式 | `NOT orange` |
| `XOR` | 仅允许一边为真 | `foo XOR bar` |

#### 📍 位置运算
| 运算符 | 含义 | 示例 |
|--------|------|------|
| `NEAR/n` | 两词在 `n` 个位置内（默认 1） | `apple NEAR/5 orange` |
| `BEF/n`  | 左词在右词之前 | `apple BEF/4 orange` |
| `AFT/n`  | 左词在右词之后 | `apple AFT/3 orange` |

- 支持范围：`foo BEF/2-4 bar`。
- `/*` 表示不限距离：`foo AFT/* bar`。
- 可追加集合：`foo BEF/2 IN(bar baz)`（全部满足）、`foo BEF/* INOF(alpha beta)`（任一满足）。

#### 🎯 匹配运算
| 运算符 | 说明 | 示例 |
|--------|------|------|
| `ONLY` | 文档仅包含指定词 | `ONLY apple` |
| `LIKE` | 文档包含全部指定词 | `LIKE app orang` |
| `STR` | 文档以指定序列开头 | `STR apple` |
| `END` | 文档以指定序列结尾 | `END apple` |

#### 📏 长度运算
- `LEN/3`：词数 ≤ 3。
- `LEN/5-10`：词数位于 5~10。
- `SIZE/32-64`：字节长度范围。
- 可与其他运算结合，如 `LEN/5-10 AND foo BEF/2 bar`、`NOT SIZE/100`。

### 3️⃣ 示例集
- 精确与通配：`apple`、`app* AND NOT apple`。
-,布尔组合：`(foo OR bar) AND NOT baz`、`(foo XOR bar) OR (baz AND qux)`。
- 位置模式：`foo NEAR/* bar`、`(foo BEF/3 baz) XOR (alpha NEAR/2 beta)`。
- 长度 + 位置：`LEN/5-20 AND foo BEF/2 IN(bar baz)`。
- 匹配链：`STR hello world AND END goodbye`、`LIKE foo bar baz`。

### 4️⃣ 运算优先级
1. 括号
2. 一元 `NOT`
3. `AND`/`OR`/`XOR` 等二元布尔运算，从左到右依次计算
4. 位置与匹配运算（`NEAR`、`BEF`、`AFT`、`ONLY`、`LIKE`、`STR`、`END` 等）

示例：
- `apple OR orange AND banana` → `(apple OR orange) AND banana`
- `apple NEAR orange AND LIKE bana` → 先算 `AND`，再处理位置/匹配。
- `(foo XOR bar) AND LEN/3-10, foo BEF/2 IN(bar baz)` 展示了逗号分段的组合。

### 5️⃣ 最佳实践
1. ✅ 预处理文本，统一小写并去除多余符号。
2. 🧠 善用括号明确意图。
3. 🧪 通过 `LexiQueryExpression(expr)` 预验证语法。
4. 🎯 控制通配符范围，配合位置限制提高精准度。
5. 📘 优先使用正向表达，必要时再引入 `NOT`。

---

Enjoy crafting expressive queries! | 祝你编写出优雅的查询表达式！ ✨
