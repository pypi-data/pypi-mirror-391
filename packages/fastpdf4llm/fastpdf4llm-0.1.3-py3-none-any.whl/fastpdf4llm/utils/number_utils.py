import re


# 识别开头的序号
def is_hierarchical_number(s: str) -> bool:
    """
    Returns True if `s` is a hierarchical number in various formats:

    Supported formats:
      - Arabic numerals: '1', '1.', '1.1', '2.10.3', '1.2.3.'
      - With Chinese punctuation: '1、', '1.1、'
      - Chinese numerals: '一、', '二、', '三、', '十、'
      - Parentheses with Arabic: '(1)', '（1）', '(1.1)', '（1.1）'
      - Parentheses with Chinese: '（一）', '（二）'
      - Parentheses with punctuation: '（1)、', '(1)、'
      - Square brackets with Arabic: '[1]', '【1】', '[1.1]', '【1.1】'
      - Square brackets with Chinese: '【一】', '【二】', '[一]', '[二]'

    Rules:
      - Strips surrounding whitespace
      - Supports both full-width and half-width parentheses, brackets, and punctuation
      - Chinese numerals: 一、二、三、四、五、六、七、八、九、十
    """
    if not s:
        return False

    # Strip surrounding whitespace
    s = s.lstrip()
    if not s:
        return False

    # Pattern 1: Arabic numerals with dots: 1, 1., 1.1, 1.1.1, etc.
    # Optional trailing dot or Chinese punctuation (、)
    pattern1 = r"^\d+(?:\.\d+)*(\.|、|\s)+"

    # Pattern 2: Chinese numer[一二三als with optional punctuation: 一、, 二、, 十、, etc.
    # Chinese numerals: 一、二、三、四、五、六、七、八、九、十
    pattern2 = r"^[一二三四五六七八九十]+[、|\s|\.]+"

    # Pattern 3: Parentheses with Arabic numerals: (1), （1）, (1.1), （1.1）, （1)、, (1)、
    # Supports both full-width （） and half-width ()
    # Optional trailing punctuation: 、
    pattern3 = r"^[（(]\d+(?:\.\d+)*[）)][、|\.|\s]*"

    # Pattern 4: Parentheses with Chinese numerals: （一）, （二）, （一）、, etc.
    # Supports both full-width and half-width parentheses
    # Optional trailing punctuation: 、
    pattern4 = r"^[（(][一二三四五六七八九十]+[）)](、|\.|\s)*"

    # Pattern 5: Square brackets with Arabic numerals: [1], 【1】, [1.1], 【1.1】, etc.
    # Supports both full-width 【】 and half-width []
    # Optional trailing punctuation: 、
    pattern5 = r"^[【\[]\d+(?:\.\d+)*[】\]](、|\.|\s)*"

    # Pattern 6: Square brackets with Chinese numerals: 【一】, 【二】, [一], [二], etc.
    # Supports both full-width and half-width square brackets
    # Optional trailing punctuation: 、
    pattern6 = r"^[【\[][一二三四五六七八九十]+[】\]](、|\.|\s)*"

    # Check all patterns
    patterns = [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6]
    return any(re.match(pattern, s) for pattern in patterns)
