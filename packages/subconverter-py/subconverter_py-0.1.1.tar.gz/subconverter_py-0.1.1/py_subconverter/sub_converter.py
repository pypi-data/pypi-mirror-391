#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import urllib.parse
import urllib.request
import argparse


def encode_url(url):
    """
    对URL进行编码
    """
    return urllib.parse.quote(url, safe='')


def decode_url(encoded_url):
    """
    对URL进行解码
    """
    return urllib.parse.unquote(encoded_url)


def download_config(subscription_url, output_file, verbose,
                    rule_url='https://raw.githubusercontent.com/JuneLegency/MyRule/master/ShellClash_Full_Block.ini'):
    """
    根据订阅地址下载配置文件
    """
    # config_url = 'https://https://github.com/juewuy/ShellCrash/raw/master/rules/ShellClash.ini'
    # config_url = 'https://https://github.com/juewuy/ShellCrash/raw/master/rules/rules/ShellClash_Full_Block.ini'
    # deploy with https://github.com/tindy2013/subconverter
    base_url = "http://127.0.0.1:25500/sub"
    params = {
        'target': 'clash',
        'insert': 'true',
        'new_name': 'true',
        'scv': 'true',
        'udp': 'true',
        'exclude': '',
        'include': '',
        'url': subscription_url,
        'config': rule_url
    }
    #
    final_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    if verbose:
        print(f"原始订阅地址: {subscription_url}")
        print(f"最终下载地址: {final_url}")

    try:
        print(f"正在从 {final_url} 下载...")
        with urllib.request.urlopen(final_url) as response, open(output_file, 'wb') as out_file:
            out_file.write(response.read())
        print(f"成功下载并保存为 {output_file}")
    except Exception as e:
        print(f"下载失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='URL编码/解码及下载工具')
    parser.add_argument('url', nargs='?', help='要处理的URL')
    parser.add_argument('-f', '--file', help='从文件读取URL进行处理')
    parser.add_argument('-d', '--decode', action='store_true', help='解码模式（默认为编码模式）')
    parser.add_argument('--download', help='从订阅地址下载配置文件')
    parser.add_argument('-o', '--output', default='config.yaml', help='输出文件名 (默认为 config.yaml)')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出模式')

    args = parser.parse_args()

    if args.download:
        download_config(args.download, args.output, args.verbose)
        return

    # 选择处理函数
    process_func = decode_url if args.decode else encode_url
    action_name = "解码" if args.decode else "编码"

    if args.url:
        # 直接从命令行参数获取URL
        result = process_func(args.url)
        if args.verbose:
            print(f"原始URL: {args.url}")
            print(f"{action_name}后: {result}")
        else:
            print(result)
    elif args.file:
        # 从文件读取URL
        try:
            with open(args.file, 'r') as f:
                urls = f.readlines()
            for url in urls:
                url = url.strip()
                if url:
                    result = process_func(url)
                    if args.verbose:
                        print(f"{url} -> {result}")
                    else:
                        print(result)
        except FileNotFoundError:
            print(f"错误: 文件 '{args.file}' 未找到", file=sys.stderr)
            sys.exit(1)
    else:
        # 从stdin读取
        if not sys.stdin.isatty():
            urls = sys.stdin.readlines()
            for url in urls:
                url = url.strip()
                if url:
                    result = process_func(url)
                    if args.verbose:
                        print(f"{url} -> {result}")
                    else:
                        print(result)
        else:
            parser.print_help()


if __name__ == '__main__':
    main()
