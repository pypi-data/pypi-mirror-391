# -- coding: utf-8 --
# Project: utils
# Created Date: 2025 11 Fr
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

# 全角符号，括号，横线，标点符号等
FULL_WIDTH_CHARACTERS = {
    "！": "!",
    "？": "?",
    "；": ";",
    "，": ",",
    "。": ".",
    "、": ",",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "《": "<",
    "》": ">",
    "：": ":",
    "“": "\"",
    "”": "\"",
    "‘": "'",
    "’": "'",
    "-": "-",
}




def safe_string_name(name: str) -> str:
    """
    清理文本中的特殊字符, 用于公司名称、银行名称等文本标准化
    """
    for char, full_width_char in FULL_WIDTH_CHARACTERS.items():
        name = name.replace(char, full_width_char)
    return name