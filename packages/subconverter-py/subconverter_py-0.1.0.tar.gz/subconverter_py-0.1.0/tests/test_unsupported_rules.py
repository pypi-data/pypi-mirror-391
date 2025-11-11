#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试不支持的规则类型是否被正确过滤
"""

from py_subconverter.ini_parser import INIConfigParser


def test_unsupported_rule_filtering():
    """测试不支持的规则类型过滤"""

    # 模拟规则文件内容（包含不支持的类型）
    test_rules_content = """
# Supported rules
DOMAIN-SUFFIX,google.com
DOMAIN,example.com
DOMAIN-KEYWORD,ads
IP-CIDR,1.1.1.1/32,no-resolve
IP-CIDR6,2001:db8::/32,no-resolve
GEOIP,CN
PROCESS-NAME,telegram

# Unsupported rules (should be filtered)
USER-AGENT,Argo*
USER-AGENT,Disney*
URL-REGEX,^https?://test
FINAL
""".strip()

    parser = INIConfigParser()

    # 手动解析规则（模拟 download_rulesets）
    rules = []
    for line in test_rules_content.split('\n'):
        line = line.strip()

        # 跳过注释和空行
        if not line or line.startswith('#'):
            continue

        parts = line.split(',')
        if not parts:
            continue

        rule_type = parts[0].strip().upper()

        # 转换 FINAL → MATCH
        if rule_type == 'FINAL':
            rule_type = 'MATCH'
            parts[0] = 'MATCH'
            line = ','.join(parts)

        # 过滤不支持的类型
        if rule_type not in parser.SUPPORTED_RULE_TYPES:
            print(f"  Skipped: {line}")
            continue

        # 添加策略组
        rules.append(f"{line},TEST-GROUP")

    print(f"\n总规则数: {len(rules)}")
    print("\n保留的规则:")
    for rule in rules:
        print(f"  ✓ {rule}")

    # 验证
    assert len(rules) == 8, f"Expected 8 rules, got {len(rules)}"
    assert not any('USER-AGENT' in r for r in rules), "USER-AGENT rules should be filtered"
    assert not any('URL-REGEX' in r for r in rules), "URL-REGEX rules should be filtered"
    assert not any('FINAL,' in r for r in rules), "FINAL should be converted to MATCH"
    assert any('MATCH,' in r for r in rules), "MATCH rule should exist"

    print("\n✅ 所有测试通过！")


def test_inline_final_conversion():
    """测试内联 FINAL 规则转换"""
    test_ini = '''
[custom]
ruleset=🐟 漏网之鱼,[]FINAL
'''

    parser = INIConfigParser()
    parser.parse_ini_file(test_ini)
    results = parser.download_rulesets(verbose=False)

    assert len(results) == 1, "Should have 1 ruleset"
    group, rules = results[0]
    assert group == '🐟 漏网之鱼'
    assert len(rules) == 1
    assert rules[0] == 'MATCH,🐟 漏网之鱼', f"Expected 'MATCH,🐟 漏网之鱼', got '{rules[0]}'"

    print("✅ 内联 FINAL 转换测试通过！")


if __name__ == "__main__":
    print("=" * 70)
    print("测试 1: 不支持的规则类型过滤")
    print("=" * 70)
    test_unsupported_rule_filtering()

    print("\n" + "=" * 70)
    print("测试 2: 内联 FINAL 规则转换")
    print("=" * 70)
    test_inline_final_conversion()

    print("\n" + "=" * 70)
    print("🎉 所有测试完成！")
    print("=" * 70)
