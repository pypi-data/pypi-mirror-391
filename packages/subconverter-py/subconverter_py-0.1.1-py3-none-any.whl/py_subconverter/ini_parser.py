#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
INI Configuration Parser for Subconverter
解析 subconverter 的 INI 配置文件
"""

import re
import urllib.request
import urllib.error
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RuleSet:
    """规则集"""
    group: str  # 策略组名称
    url: str    # 规则 URL 或规则内容


@dataclass
class ProxyGroup:
    """策略组"""
    name: str           # 组名称
    type: str           # 类型: select, url-test, fallback, load-balance
    proxies: List[str]  # 代理列表
    url: Optional[str] = None      # 健康检查 URL
    interval: Optional[int] = None # 检查间隔


class INIConfigParser:
    """INI 配置解析器"""

    # Clash 支持的规则类型
    # 参考: https://github.com/Dreamacro/clash/wiki/configuration
    SUPPORTED_RULE_TYPES = {
        'DOMAIN',
        'DOMAIN-SUFFIX',
        'DOMAIN-KEYWORD',
        'IP-CIDR',
        'IP-CIDR6',
        'GEOIP',
        'MATCH',
        'PROCESS-NAME',
        # 'SRC-IP-CIDR',  # 某些版本支持
        # 'SRC-PORT',
        # 'DST-PORT',
    }

    def __init__(self):
        self.rulesets: List[RuleSet] = []
        self.proxy_groups: List[ProxyGroup] = []
        self.custom_rules: List[str] = []

    def fetch_content(self, url: str) -> str:
        """获取 URL 内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {e}")

    def parse_ini_file(self, content: str) -> None:
        """解析 INI 文件内容"""
        current_section = None

        for line in content.split('\n'):
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith('#') or line.startswith(';'):
                continue

            # 检测段落
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].lower()
                continue

            # 解析 custom 段落
            if current_section == 'custom':
                self._parse_custom_line(line)

    def _parse_custom_line(self, line: str) -> None:
        """解析 custom 段落的一行"""
        # 解析 ruleset
        if line.startswith('ruleset='):
            self._parse_ruleset(line[8:])  # 移除 "ruleset="

        # 解析 custom_proxy_group
        elif line.startswith('custom_proxy_group='):
            self._parse_proxy_group(line[19:])  # 移除 "custom_proxy_group="

    def _parse_ruleset(self, content: str) -> None:
        """解析 ruleset 行

        格式: ruleset=策略组名,规则URL或内容
        示例:
          ruleset=🎯 全球直连,https://example.com/rules.list
          ruleset=🎯 全球直连,[]GEOIP,CN
        """
        parts = content.split(',', 1)
        if len(parts) != 2:
            return

        group = parts[0].strip()
        rule_content = parts[1].strip()

        self.rulesets.append(RuleSet(group=group, url=rule_content))

    def _parse_proxy_group(self, content: str) -> None:
        """解析 custom_proxy_group 行

        格式: 组名`类型`参数1`参数2...
        示例:
          🚀 节点选择`select`[]♻️ 自动选择`[]🇭🇰 香港节点`[]DIRECT
          ♻️ 自动选择`url-test`.*`http://www.gstatic.com/generate_204`300
        """
        # 使用反引号分割
        parts = content.split('`')
        if len(parts) < 2:
            return

        name = parts[0].strip()
        group_type = parts[1].strip()

        # 解析代理列表
        proxies = []
        url = None
        interval = None

        for i in range(2, len(parts)):
            part = parts[i].strip()

            # 跳过空部分
            if not part:
                continue

            # URL 健康检查地址
            if part.startswith('http://') or part.startswith('https://'):
                url = part
            # 间隔时间（数字）
            elif part.isdigit():
                interval = int(part)
            # 代理或代理组引用
            else:
                # 保持原样，包括 [] 前缀（用于后续识别策略组引用）
                proxies.append(part)

        group = ProxyGroup(
            name=name,
            type=group_type,
            proxies=proxies,
            url=url,
            interval=interval
        )

        self.proxy_groups.append(group)

    def download_rulesets(self, verbose: bool = False) -> List[Tuple[str, List[str]]]:
        """下载所有规则集

        Returns:
            List of (group_name, rules)
        """
        results = []

        for ruleset in self.rulesets:
            if verbose:
                print(f"  Downloading ruleset: {ruleset.group}")

            rules = []

            # 如果是内联规则（[]开头）
            if ruleset.url.startswith('[]'):
                # 格式: []GEOIP,CN 或 []FINAL
                inline_rule = ruleset.url[2:]  # 移除 []

                # 转换 FINAL → MATCH (Clash 兼容性)
                if inline_rule.upper() == 'FINAL' or inline_rule.upper().startswith('FINAL,'):
                    inline_rule = inline_rule.replace('FINAL', 'MATCH', 1)
                    inline_rule = inline_rule.replace('final', 'MATCH', 1)

                if ',' in inline_rule:
                    rules.append(f"{inline_rule},{ruleset.group}")
                else:
                    rules.append(f"{inline_rule},{ruleset.group}")

            # 如果是 URL
            elif ruleset.url.startswith('http://') or ruleset.url.startswith('https://'):
                try:
                    content = self.fetch_content(ruleset.url)
                    # 解析规则文件
                    for line in content.split('\n'):
                        line = line.strip()
                        # 跳过注释和空行
                        if not line or line.startswith('#') or line.startswith(';'):
                            continue

                        # 检查规则类型是否支持
                        parts = line.split(',')
                        if not parts:
                            continue

                        rule_type = parts[0].strip().upper()

                        # 处理规则类型转换
                        # FINAL -> MATCH (Clash 兼容性)
                        if rule_type == 'FINAL':
                            rule_type = 'MATCH'
                            parts[0] = 'MATCH'
                            line = ','.join(parts)

                        # 过滤不支持的规则类型
                        if rule_type not in self.SUPPORTED_RULE_TYPES:
                            if verbose:
                                print(f"    Skipped unsupported rule: {line[:60]}...")
                            continue

                        # 检查规则是否已经有策略组，并在正确位置插入
                        # Clash规则格式: TYPE,VALUE,GROUP[,OPTIONS]
                        # 例如: DOMAIN-SUFFIX,google.com,PROXY
                        #       IP-CIDR,1.1.1.1/32,PROXY,no-resolve
                        # parts 已经在上面 split 过了

                        # 常见的选项关键字（不是策略组名称）
                        known_options = {'no-resolve'}

                        # 判断是否已有策略组：
                        # - 至少3部分
                        # - 第3部分不是known_options中的选项
                        has_group = False
                        if len(parts) >= 3:
                            third_part = parts[2].strip()
                            if third_part not in known_options:
                                has_group = True

                        if has_group:
                            # 已经有策略组，保持原样
                            rules.append(line)
                        else:
                            # 没有策略组，需要在正确位置插入
                            # 格式：TYPE,VALUE,GROUP[,OPTIONS]
                            # 策略组应该在第3位（index 2），选项在第4位及之后
                            if len(parts) == 2:
                                # TYPE,VALUE → TYPE,VALUE,GROUP
                                rules.append(f"{line},{ruleset.group}")
                            elif len(parts) >= 3 and parts[2].strip() in known_options:
                                # TYPE,VALUE,no-resolve → TYPE,VALUE,GROUP,no-resolve
                                # 插入策略组在选项之前
                                new_parts = parts[:2] + [ruleset.group] + parts[2:]
                                rules.append(','.join(new_parts))
                            else:
                                # 其他情况，添加到末尾
                                rules.append(f"{line},{ruleset.group}")

                    if verbose:
                        print(f"    Loaded {len(rules)} rules")
                except Exception as e:
                    if verbose:
                        print(f"    Failed to load: {e}")

            if rules:
                results.append((ruleset.group, rules))

        return results

    def resolve_proxy_groups(self, proxy_names: List[str]) -> List[ProxyGroup]:
        """解析代理组，处理引用和正则匹配

        Args:
            proxy_names: 实际的代理节点名称列表

        Returns:
            解析后的代理组列表
        """
        resolved_groups = []

        for group in self.proxy_groups:
            resolved_proxies = []

            for proxy_ref in group.proxies:
                # 策略组引用（[]开头）
                if proxy_ref.startswith('[]'):
                    # 移除 [] 前缀，得到策略组名称
                    group_name = proxy_ref[2:]
                    resolved_proxies.append(group_name)
                # 特殊值（DIRECT, REJECT）
                elif proxy_ref in ['DIRECT', 'REJECT']:
                    resolved_proxies.append(proxy_ref)
                # 正则表达式匹配节点
                else:
                    # 尝试作为正则表达式匹配节点
                    try:
                        pattern = re.compile(proxy_ref)
                        matched = [name for name in proxy_names if pattern.search(name)]
                        resolved_proxies.extend(matched)
                    except re.error:
                        # 不是有效的正则，当作普通代理名
                        if proxy_ref in proxy_names:
                            resolved_proxies.append(proxy_ref)

            # 去重但保持顺序
            seen = set()
            unique_proxies = []
            for p in resolved_proxies:
                if p not in seen:
                    seen.add(p)
                    unique_proxies.append(p)

            # 如果没有匹配到任何代理，添加 DIRECT 作为默认值
            # Clash 要求每个策略组至少有一个 proxy
            if not unique_proxies:
                unique_proxies = ['DIRECT']

            resolved_group = ProxyGroup(
                name=group.name,
                type=group.type,
                proxies=unique_proxies,
                url=group.url,
                interval=group.interval
            )
            resolved_groups.append(resolved_group)

        return resolved_groups

    def to_clash_proxy_groups(self, proxy_names: List[str]) -> List[Dict]:
        """转换为 Clash proxy-groups 格式"""
        resolved_groups = self.resolve_proxy_groups(proxy_names)
        clash_groups = []

        for group in resolved_groups:
            clash_group = {
                'name': group.name,
                'type': group.type,
                'proxies': group.proxies
            }

            # 添加健康检查参数
            if group.type in ['url-test', 'fallback', 'load-balance']:
                if group.url:
                    clash_group['url'] = group.url
                else:
                    clash_group['url'] = 'http://www.gstatic.com/generate_204'

                if group.interval:
                    clash_group['interval'] = group.interval
                else:
                    clash_group['interval'] = 300

            clash_groups.append(clash_group)

        return clash_groups


def parse_ini_config(ini_url: str, verbose: bool = False) -> INIConfigParser:
    """解析 INI 配置文件

    Args:
        ini_url: INI 配置文件的 URL
        verbose: 是否显示详细信息

    Returns:
        INIConfigParser 实例
    """
    parser = INIConfigParser()

    if verbose:
        print(f"Fetching INI config from: {ini_url}")

    # 下载 INI 文件
    content = parser.fetch_content(ini_url)

    if verbose:
        print(f"INI config size: {len(content)} bytes")

    # 解析 INI 文件
    parser.parse_ini_file(content)

    if verbose:
        print(f"Parsed {len(parser.rulesets)} rulesets")
        print(f"Parsed {len(parser.proxy_groups)} proxy groups")

    return parser


if __name__ == "__main__":
    # 测试
    test_ini = """
[custom]
ruleset=🎯 全球直连,https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/LocalAreaNetwork.list
ruleset=🛑 广告拦截,https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/BanAD.list
ruleset=🎯 全球直连,[]GEOIP,CN
ruleset=🐟 漏网之鱼,[]FINAL

custom_proxy_group=🚀 节点选择`select`[]♻️ 自动选择`[]🇭🇰 香港节点`[]DIRECT
custom_proxy_group=♻️ 自动选择`url-test`.*`http://www.gstatic.com/generate_204`300
custom_proxy_group=🇭🇰 香港节点`url-test`香港|HK`http://www.gstatic.com/generate_204`300
custom_proxy_group=🎯 全球直连`select`[]DIRECT
custom_proxy_group=🛑 广告拦截`select`[]REJECT
custom_proxy_group=🐟 漏网之鱼`select`[]🚀 节点选择`[]DIRECT
"""

    parser = INIConfigParser()
    parser.parse_ini_file(test_ini)

    print(f"\nParsed {len(parser.rulesets)} rulesets:")
    for rs in parser.rulesets:
        print(f"  {rs.group}: {rs.url[:50]}...")

    print(f"\nParsed {len(parser.proxy_groups)} proxy groups:")
    for pg in parser.proxy_groups:
        print(f"  {pg.name} ({pg.type}): {len(pg.proxies)} proxies")

    # 测试节点匹配
    test_proxies = ["香港 01", "香港 02", "美国 01", "日本 01"]
    resolved = parser.resolve_proxy_groups(test_proxies)

    print(f"\nResolved proxy groups with test proxies:")
    for pg in resolved:
        print(f"  {pg.name}: {pg.proxies}")
