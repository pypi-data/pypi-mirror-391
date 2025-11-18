import os
import sys

import pytest

try:
    from cpp_module import cpp_extension

    CPP_EXTENSION_AVAILABLE = True
except ImportError:
    CPP_EXTENSION_AVAILABLE = False
    pytest.skip("C++ extension not available", allow_module_level=True)


def test_add_function_basic():
    """测试基本加法功能"""
    result = cpp_extension.add(5, 3)
    assert result == 8
    assert isinstance(result, int)


def test_text_processor_to_upper():
    """测试大写转换功能"""
    processor = cpp_extension.TextProcessor("TestProcessor")

    # 测试基本转换
    result = processor.to_upper("hello world")
    assert result == "HELLO WORLD"
    assert isinstance(result, str)

    # 测试空字符串
    result = processor.to_upper("")
    assert result == ""

    # 测试已大写的字符串
    result = processor.to_upper("ALREADY UPPER")
    assert result == "ALREADY UPPER"

    # 测试特殊字符
    result = processor.to_upper("hello123!@#")
    assert result == "HELLO123!@#"
