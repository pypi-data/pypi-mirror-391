# Text Normalizer

## 基本使用

```python
from tts_text_norm import TextNormalizer

# 创建规范化器实例
normalizer = TextNormalizer()

# 中文文本规范化
text_zh = "这是123个测试文本"
result_zh = normalizer.text_normalize(text_zh, language="中文")
print(result_zh)  # 输出：这是一百二十三 test

# 日语文本规范化
text_jp = "これは123のテストです"
result_jp = normalizer.text_normalize(text_jp, language="日语")
print(result_jp)

# 英语文本规范化
text_en = "This is a test with 123 numbers"
result_en = normalizer.text_normalize(text_en, language="英语")
print(result_en)
```
