#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subscription Converter CLI
支持新旧两种转换方式的命令行工具
"""

import argparse
import sys
import os
import urllib.parse
import urllib.request
from typing import Optional

from dotenv import load_dotenv
from .dler_api_client import DlerAPIClient
from .subscription_converter import SubscriptionConverter


class ConverterCLI:
    """订阅转换器命令行接口"""

    def __init__(self):
        self.converter = SubscriptionConverter()

    def convert_via_http(
        self,
        subscription_url: str,
        output: str,
        host: str = "http://127.0.0.1:25500/sub",
        target: str = "clash",
        config_url: Optional[str] = None,
        insert: bool = True,
        new_name: bool = True,
        scv: bool = True,
        udp: bool = True,
        tfo: bool = False,
        emoji: bool = True,
        exclude: str = "",
        include: str = "",
        sort: bool = False,
        append_type: bool = False,
        verbose: bool = False
    ) -> bool:
        """
        通过 HTTP 服务转换订阅（旧方法）

        Args:
            subscription_url: 订阅地址
            output: 输出文件路径
            host: subconverter 服务地址
            target: 目标格式 (clash, surge, v2ray 等)
            config_url: 外部配置文件地址
            insert: 是否插入节点
            new_name: 是否使用新的节点名称
            scv: 是否跳过证书验证
            udp: 是否启用 UDP
            tfo: 是否启用 TCP Fast Open
            emoji: 是否添加 emoji
            exclude: 排除的节点（正则）
            include: 包含的节点（正则）
            sort: 是否排序节点
            append_type: 是否在节点名称后添加类型
            verbose: 详细输出
        """
        print("="*70)
        print("使用 HTTP 服务转换 (旧方法)")
        print("="*70)

        # 构建参数
        params = {
            'target': target,
            'url': subscription_url,
        }

        # 可选参数
        if config_url:
            params['config'] = config_url

        # 布尔参数
        if insert:
            params['insert'] = 'true'
        if new_name:
            params['new_name'] = 'true'
        if scv:
            params['scv'] = 'true'
        if udp:
            params['udp'] = 'true'
        if tfo:
            params['tfo'] = 'true'
        if emoji:
            params['emoji'] = 'true'
        if sort:
            params['sort'] = 'true'
        if append_type:
            params['append_type'] = 'true'

        # 字符串参数
        if exclude:
            params['exclude'] = exclude
        if include:
            params['include'] = include

        # 构建最终 URL
        final_url = f"{host}?{urllib.parse.urlencode(params)}"

        if verbose:
            print(f"\n订阅地址: {subscription_url}")
            print(f"服务地址: {host}")
            print(f"最终 URL: {final_url}")
            print(f"\n参数:")
            for key, value in params.items():
                print(f"  {key}: {value}")

        try:
            print(f"\n正在从 {host} 下载...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(final_url, headers=headers)

            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()

                # 保存到文件
                with open(output, 'wb') as f:
                    f.write(content)

                print(f"✓ 成功下载并保存为 {output}")
                print(f"✓ 文件大小: {len(content)} 字节")
                return True

        except Exception as e:
            print(f"✗ 下载失败: {e}", file=sys.stderr)
            return False

    def convert_local(
        self,
        subscription_url: str,
        output: str,
        config_url: Optional[str] = None,
        exclude: str = "",
        include: str = "",
        emoji: bool = True,
        sort: bool = False,
        udp: bool = True,
        tfo: bool = False,
        scv: bool = True,
        append_type: bool = False,
        verbose: bool = False
    ) -> bool:
        """
        本地转换订阅（新方法）

        Args:
            subscription_url: 订阅地址
            output: 输出文件路径
            config_url: 自定义规则地址
            exclude: 排除的节点（正则）
            include: 包含的节点（正则）
            emoji: 是否保留 emoji
            sort: 是否排序节点
            udp: 是否启用 UDP
            tfo: 是否启用 TCP Fast Open
            scv: 是否跳过证书验证
            append_type: 是否在节点名称后添加类型
            verbose: 详细输出
        """
        print("="*70)
        print("使用本地转换 (新方法)")
        print("="*70)

        if verbose:
            print(f"\n订阅地址: {subscription_url}")
            print(f"输出文件: {output}")
            if config_url:
                print(f"规则地址: {config_url}")
            print(f"\n参数:")
            print(f"  exclude: {exclude or '(无)'}")
            print(f"  include: {include or '(无)'}")
            print(f"  emoji: {emoji}")
            print(f"  sort: {sort}")
            print(f"  udp: {udp}")
            print(f"  tfo: {tfo}")
            print(f"  scv: {scv}")
            print(f"  append_type: {append_type}")

        try:
            # 获取订阅内容
            print(f"\n正在获取订阅...")
            content = self.converter.fetch_subscription(subscription_url)
            print(f"✓ 订阅大小: {len(content)} 字节")

            # 解析代理
            from .proxy_parser import parse_subscription
            print(f"\n正在解析代理节点...")
            proxies = parse_subscription(content)
            print(f"✓ 发现 {len(proxies)} 个节点")

            if not proxies:
                print("✗ 未找到有效的代理节点", file=sys.stderr)
                return False

            # 显示节点类型分布
            if verbose:
                type_count = {}
                for proxy in proxies:
                    ptype = proxy.type.value
                    type_count[ptype] = type_count.get(ptype, 0) + 1
                print(f"\n节点类型分布:")
                for ptype, count in type_count.items():
                    print(f"  {ptype}: {count}")

            # 应用过滤规则
            if exclude or include:
                original_count = len(proxies)
                proxies = self._filter_proxies(proxies, exclude, include, verbose)
                print(f"\n过滤后: {len(proxies)}/{original_count} 个节点")

            # 应用其他选项
            proxies = self._apply_options(
                proxies,
                emoji=emoji,
                sort=sort,
                udp=udp,
                tfo=tfo,
                scv=scv,
                append_type=append_type,
                verbose=verbose
            )

            # 生成配置
            print(f"\n正在生成 Clash 配置...")
            from .clash_generator import ClashGenerator
            generator = ClashGenerator()

            # 加载自定义规则
            rules = None
            custom_proxy_groups = None

            if config_url:
                print(f"正在加载自定义配置...")
                try:
                    rules_content = self.converter.fetch_subscription(config_url)
                    rules, custom_proxy_groups = self._parse_rules(rules_content, proxies, verbose)
                    if rules:
                        print(f"✓ 加载了 {len(rules)} 条规则")
                    if custom_proxy_groups:
                        print(f"✓ 生成了 {len(custom_proxy_groups)} 个自定义策略组")
                    if not rules and not custom_proxy_groups:
                        print(f"⚠ 使用默认配置")
                except Exception as e:
                    print(f"⚠ 加载配置失败: {e}")
                    print(f"⚠ 使用默认配置")

            config = generator.generate_config(
                proxies,
                rules=rules,
                proxy_groups=custom_proxy_groups
            )

            # 保存配置
            with open(output, 'w', encoding='utf-8') as f:
                f.write(config)

            print(f"\n✓ 配置已保存: {output}")
            print(f"✓ 配置大小: {len(config)} 字节")
            return True

        except Exception as e:
            print(f"\n✗ 转换失败: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()
            return False

    def _filter_proxies(self, proxies, exclude: str, include: str, verbose: bool):
        """过滤代理节点"""
        import re

        filtered = proxies

        # 排除规则
        if exclude:
            try:
                exclude_pattern = re.compile(exclude, re.IGNORECASE)
                before = len(filtered)
                filtered = [p for p in filtered if not exclude_pattern.search(p.name)]
                if verbose:
                    print(f"  排除规则匹配: {before - len(filtered)} 个节点")
            except re.error as e:
                print(f"⚠ 排除规则无效: {e}")

        # 包含规则
        if include:
            try:
                include_pattern = re.compile(include, re.IGNORECASE)
                before = len(filtered)
                filtered = [p for p in filtered if include_pattern.search(p.name)]
                if verbose:
                    print(f"  包含规则匹配: {len(filtered)}/{before} 个节点")
            except re.error as e:
                print(f"⚠ 包含规则无效: {e}")

        return filtered

    def _apply_options(self, proxies, emoji, sort, udp, tfo, scv, append_type, verbose):
        """应用配置选项"""
        # 移除 emoji（如果需要）
        if not emoji:
            for proxy in proxies:
                # 简单移除 emoji（移除所有 Unicode emoji）
                import re
                proxy.name = re.sub(r'[\U00010000-\U0010ffff]', '', proxy.name).strip()
                proxy.name = re.sub(r'[🇦-🇿]', '', proxy.name).strip()

        # 添加类型后缀
        if append_type:
            for proxy in proxies:
                ptype = proxy.type.value.upper()
                if not proxy.name.endswith(f" [{ptype}]"):
                    proxy.name = f"{proxy.name} [{ptype}]"

        # 设置 UDP/TFO/SCV
        for proxy in proxies:
            if udp is not None:
                proxy.udp = udp
            if tfo is not None:
                proxy.tfo = tfo
            if scv is not None:
                proxy.skip_cert_verify = scv

        # 排序
        if sort:
            proxies.sort(key=lambda p: p.name)
            if verbose:
                print(f"  已按名称排序")

        return proxies

    def _parse_rules(self, content: str, proxies, verbose: bool):
        """解析规则内容

        Returns:
            Tuple[Optional[List[str]], Optional[List[Dict]]]: (rules, custom_proxy_groups)
        """
        # Check if it's a subconverter INI file
        if '[custom]' in content or 'ruleset=' in content or 'custom_proxy_group=' in content:
            print("✓ 检测到 subconverter INI 配置文件")
            print("✓ 正在解析 INI 配置...")

            try:
                from .ini_parser import INIConfigParser

                # Parse INI config
                ini_parser = INIConfigParser()
                ini_parser.parse_ini_file(content)

                # Download all rulesets
                print("\n下载规则集...")
                ruleset_results = ini_parser.download_rulesets(verbose=verbose)

                # Flatten all rules from rulesets
                rules = []
                for group_name, group_rules in ruleset_results:
                    rules.extend(group_rules)

                if verbose:
                    print(f"✓ 从 {len(ruleset_results)} 个规则集加载了 {len(rules)} 条规则")

                # Get proxy names from parsed proxies
                proxy_names = [p.name for p in proxies]

                # Generate custom proxy groups
                print("\n生成自定义策略组...")
                custom_proxy_groups = ini_parser.to_clash_proxy_groups(proxy_names)

                if verbose:
                    print(f"✓ 生成了 {len(custom_proxy_groups)} 个自定义策略组")
                    for group in custom_proxy_groups[:5]:  # 显示前5个
                        print(f"  - {group['name']} ({group['type']})")
                    if len(custom_proxy_groups) > 5:
                        print(f"  ... 还有 {len(custom_proxy_groups) - 5} 个")

                return rules, custom_proxy_groups

            except Exception as e:
                print(f"⚠ INI 解析失败: {e}")
                if verbose:
                    import traceback
                    traceback.print_exc()
                return None, None

        # Plain rule list
        rules = []
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            # Basic validation - must contain commas (rule format)
            if ',' in line:
                rules.append(line)

        return (rules if rules else None), None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Subscription Converter CLI - 支持新旧两种转换方式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用场景:

  1. 只有订阅 URL（无需账户）★ 推荐
     %(prog)s --url https://example.com/subscription -o config.yaml

  2. 有 Dler Cloud 账户:
     %(prog)s --email user@example.com --password pass123 -o config.yaml

  3. 有 Dler Cloud Token:
     %(prog)s --token YOUR_TOKEN -o config.yaml

示例:

  # 最简单：只用订阅 URL
  %(prog)s --url https://example.com/subscription -o config.yaml

  # 过滤特定节点
  %(prog)s --url https://example.com/sub --include "香港|HK" -o hk.yaml

  # 使用外部规则
  %(prog)s --url https://example.com/sub \\
    --config https://example.com/rules.ini -o config.yaml

  # 使用 HTTP 服务转换
  %(prog)s --url https://example.com/sub --method http -o config.yaml

  # 使用 Dler Cloud 账户
  %(prog)s --email user@example.com --password pass -o config.yaml

参数说明:
  --method local  使用本地解析（新方法，无需服务器）
  --method http   使用 HTTP 服务（旧方法，需要 subconverter）

注意:
  认证参数（email/password/token）只在使用 Dler Cloud API 时需要
  如果提供了 --url 参数，则不需要认证
        """
    )

    # 认证参数（可选，仅 Dler Cloud 用户需要）
    auth_group = parser.add_argument_group('认证参数 (仅使用 Dler Cloud API 时需要)')
    auth_group.add_argument(
        '--email',
        help='Dler Cloud 邮箱'
    )
    auth_group.add_argument(
        '--password',
        help='Dler Cloud 密码'
    )
    auth_group.add_argument(
        '--token',
        help='Dler Cloud API Token（优先使用）'
    )

    # 订阅参数
    sub_group = parser.add_argument_group('订阅参数')
    sub_group.add_argument(
        '--url',
        help='订阅 URL（如果提供则不使用 Dler API）'
    )
    sub_group.add_argument(
        '--sub-type',
        choices=['ss2022', 'vmess', 'trojan'],
        default='ss2022',
        help='订阅类型（使用 Dler API 时）(默认: ss2022)'
    )

    # 输出参数
    parser.add_argument(
        '-o', '--output',
        default='config.yaml',
        help='输出文件路径 (默认: config.yaml)'
    )

    # 转换方法
    parser.add_argument(
        '--method',
        choices=['local', 'http'],
        default='local',
        help='转换方法: local=本地转换(新), http=HTTP服务(旧) (默认: local)'
    )

    # HTTP 服务参数
    http_group = parser.add_argument_group('HTTP 服务参数 (--method http 时使用)')
    http_group.add_argument(
        '--host',
        default='http://127.0.0.1:25500/sub',
        help='subconverter 服务地址 (默认: http://127.0.0.1:25500/sub)'
    )
    http_group.add_argument(
        '--target',
        default='clash',
        help='目标格式 (默认: clash)'
    )

    # 配置参数
    config_group = parser.add_argument_group('配置参数')
    config_group.add_argument(
        '--config',
        help='外部配置/规则文件 URL'
    )
    config_group.add_argument(
        '--exclude',
        default='',
        help='排除的节点（正则表达式）'
    )
    config_group.add_argument(
        '--include',
        default='',
        help='包含的节点（正则表达式）'
    )

    # 功能开关
    feature_group = parser.add_argument_group('功能开关')
    feature_group.add_argument(
        '--no-insert',
        action='store_true',
        help='不插入节点'
    )
    feature_group.add_argument(
        '--no-new-name',
        action='store_true',
        help='不使用新节点名称'
    )
    feature_group.add_argument(
        '--no-udp',
        action='store_true',
        help='禁用 UDP'
    )
    feature_group.add_argument(
        '--no-emoji',
        action='store_true',
        help='移除节点名称中的 emoji'
    )
    feature_group.add_argument(
        '--scv',
        action='store_true',
        default=True,
        help='跳过证书验证 (默认: 启用)'
    )
    feature_group.add_argument(
        '--tfo',
        action='store_true',
        help='启用 TCP Fast Open'
    )
    feature_group.add_argument(
        '--sort',
        action='store_true',
        help='排序节点'
    )
    feature_group.add_argument(
        '--append-type',
        action='store_true',
        help='在节点名称后添加类型'
    )

    # 其他参数
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )

    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()

    # 确定订阅 URL
    subscription_url = args.url

    if not subscription_url:
        # 从 Dler API 获取
        token = args.token or os.environ.get("DLER_API_TOKEN")
        email = args.email or os.environ.get("DLER_EMAIL")
        password = args.password or os.environ.get("DLER_PASSWORD")

        if not token and not (email and password):
            print("错误: 需要提供以下之一:", file=sys.stderr)
            print("  1. --url 参数指定订阅地址", file=sys.stderr)
            print("  2. --email 和 --password 登录 Dler Cloud", file=sys.stderr)
            print("  3. --token 使用 API Token", file=sys.stderr)
            print("  4. 在 .env 文件中配置凭据", file=sys.stderr)
            sys.exit(1)

        try:
            # 登录
            if not token:
                print("正在登录 Dler Cloud...")
                token = DlerAPIClient.login(email=email, password=password)
                print("✓ 登录成功")

            # 获取订阅
            client = DlerAPIClient(token=token)
            managed_config = client.get_managed_config()

            # 根据类型获取 URL
            subscription_url = managed_config.ss2022  # 默认使用 ss2022
            if args.sub_type == 'vmess':
                subscription_url = managed_config.vmess
            elif args.sub_type == 'trojan':
                subscription_url = getattr(managed_config, 'trojan', managed_config.ss2022)

            # 替换为订阅格式
            subscription_url = subscription_url.replace('clash', 'mu')

            print(f"✓ 获取到订阅地址")
            if args.verbose:
                print(f"  URL: {subscription_url}")

        except Exception as e:
            print(f"✗ 获取订阅失败: {e}", file=sys.stderr)
            sys.exit(1)

    # 执行转换
    cli = ConverterCLI()

    if args.method == 'http':
        # HTTP 服务转换
        success = cli.convert_via_http(
            subscription_url=subscription_url,
            output=args.output,
            host=args.host,
            target=args.target,
            config_url=args.config,
            insert=not args.no_insert,
            new_name=not args.no_new_name,
            scv=args.scv,
            udp=not args.no_udp,
            tfo=args.tfo,
            emoji=not args.no_emoji,
            exclude=args.exclude,
            include=args.include,
            sort=args.sort,
            append_type=args.append_type,
            verbose=args.verbose
        )
    else:
        # 本地转换
        success = cli.convert_local(
            subscription_url=subscription_url,
            output=args.output,
            config_url=args.config,
            exclude=args.exclude,
            include=args.include,
            emoji=not args.no_emoji,
            sort=args.sort,
            udp=not args.no_udp,
            tfo=args.tfo,
            scv=args.scv,
            append_type=args.append_type,
            verbose=args.verbose
        )

    if success:
        print("\n" + "="*70)
        print("✓ 转换完成!")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("✗ 转换失败")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
