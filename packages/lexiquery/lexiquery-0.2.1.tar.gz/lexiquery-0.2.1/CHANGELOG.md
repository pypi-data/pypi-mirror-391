# LexiQuery Changelog / 更新日志

## v0.2.1

- Added comma-separated expression chains and adjusted boolean precedence so `AND`/`OR`/`XOR` evaluate left-to-right after `NOT`, matching the latest PRD.
- Updated tokenizer/parser/evaluator, docs, and regression tests to cover the new behavior; bumped package version to `0.2.1`.

---

- 新增逗号分隔的多段表达式，并调整布尔优先级：`NOT` 之后 `AND`/`OR`/`XOR` 按从左到右顺序计算，符合最新 PRD。
- 同步更新 tokenizer / parser / evaluator、文档与回归测试，并将版本号提升到 `0.2.1`。
