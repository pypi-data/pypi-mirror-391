#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Proxy Parser - Parse various proxy subscription formats
Supports: SS, SSR, VMess, Trojan, Hysteria, Hysteria2, etc.
"""

import base64
import json
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ProxyType(Enum):
    UNKNOWN = "unknown"
    SHADOWSOCKS = "ss"
    SHADOWSOCKSR = "ssr"
    VMESS = "vmess"
    TROJAN = "trojan"
    SNELL = "snell"
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"
    WIREGUARD = "wireguard"
    HYSTERIA = "hysteria"
    HYSTERIA2 = "hysteria2"


@dataclass
class Proxy:
    """Universal proxy node structure"""
    type: ProxyType = ProxyType.UNKNOWN
    name: str = ""
    server: str = ""
    port: int = 0

    # Common fields
    udp: Optional[bool] = None
    tfo: Optional[bool] = None  # TCP Fast Open
    skip_cert_verify: Optional[bool] = None

    # SS/SSR
    password: Optional[str] = None
    cipher: Optional[str] = None
    plugin: Optional[str] = None
    plugin_opts: Optional[Dict[str, str]] = None

    # SSR specific
    protocol: Optional[str] = None
    protocol_param: Optional[str] = None
    obfs: Optional[str] = None
    obfs_param: Optional[str] = None

    # VMess
    uuid: Optional[str] = None
    alter_id: int = 0
    security: str = "auto"
    network: str = "tcp"
    ws_path: Optional[str] = None
    ws_headers: Optional[Dict[str, str]] = None
    h2_path: Optional[str] = None
    h2_host: Optional[List[str]] = None
    grpc_service_name: Optional[str] = None
    tls: bool = False
    sni: Optional[str] = None
    alpn: Optional[List[str]] = None
    fingerprint: Optional[str] = None

    # Trojan
    # Uses password, sni, alpn, skip_cert_verify from above

    # Hysteria
    auth: Optional[str] = None
    auth_str: Optional[str] = None
    up: Optional[str] = None
    down: Optional[str] = None
    obfs_protocol: Optional[str] = None
    hop_interval: Optional[int] = None

    # HTTP/SOCKS5
    username: Optional[str] = None

    # Raw data for debugging
    raw: Optional[str] = None


def safe_base64_decode(s: str) -> str:
    """Safely decode base64 with padding fix"""
    try:
        # Add padding if needed
        missing_padding = len(s) % 4
        if missing_padding:
            s += '=' * (4 - missing_padding)
        # Try URL-safe decoding first
        try:
            return base64.urlsafe_b64decode(s).decode('utf-8')
        except:
            # Fall back to standard base64
            return base64.b64decode(s).decode('utf-8')
    except Exception as e:
        print(f"Base64 decode error: {e}")
        return ""


def parse_ss(url: str) -> Optional[Proxy]:
    """Parse Shadowsocks URL
    Format: ss://base64(method:password)@server:port#remark
    or: ss://base64(method:password@server:port)#remark
    or: ss://method:password@server:port#remark (SIP002)
    or: ss://base64@server:port/?params#remark (SIP008)
    """
    try:
        url = url.replace("ss://", "")

        # Extract remark
        name = ""
        if "#" in url:
            url, name = url.split("#", 1)
            name = urllib.parse.unquote(name)

        # Extract params (including plugin)
        plugin = None
        plugin_opts = {}
        udp = None
        if "?" in url or "/?udp" in url:
            url, query = url.split("?", 1)
            params = urllib.parse.parse_qs(query)

            # Handle plugin
            if "plugin" in params:
                plugin_str = params["plugin"][0]
                if ";" in plugin_str:
                    plugin, opts_str = plugin_str.split(";", 1)
                    for opt in opts_str.split(";"):
                        if "=" in opt:
                            k, v = opt.split("=", 1)
                            plugin_opts[k] = v
                else:
                    plugin = plugin_str

            # Handle UDP
            if "udp" in params:
                udp = params["udp"][0] == "1"

        # Remove trailing slash if present
        url = url.rstrip('/')

        # Check if it's SIP002 format (plain text with @)
        if "@" in url and not url.startswith("base64,"):
            # Could be either plain text or base64@server:port format
            parts = url.split("@")
            if len(parts) == 2:
                userinfo_part = parts[0]
                server_part = parts[1]

                # Try to parse as plain text first
                if ":" in userinfo_part and ":" in server_part:
                    try:
                        method, password = userinfo_part.split(":", 1)
                        server, port = server_part.rsplit(":", 1)

                        return Proxy(
                            type=ProxyType.SHADOWSOCKS,
                            name=name or f"{server}:{port}",
                            server=server,
                            port=int(port),
                            password=password,
                            cipher=method,
                            plugin=plugin,
                            plugin_opts=plugin_opts if plugin_opts else None,
                            udp=udp,
                            raw=url
                        )
                    except:
                        pass

                # Try as base64@server:port (SIP008 format)
                try:
                    decoded = safe_base64_decode(userinfo_part)
                    if decoded and ":" in decoded:
                        method, password = decoded.split(":", 1)
                        server, port = server_part.rsplit(":", 1)

                        return Proxy(
                            type=ProxyType.SHADOWSOCKS,
                            name=name or f"{server}:{port}",
                            server=server,
                            port=int(port),
                            password=password,
                            cipher=method,
                            plugin=plugin,
                            plugin_opts=plugin_opts if plugin_opts else None,
                            udp=udp,
                            raw=url
                        )
                except:
                    pass

        # Try full base64 decoding (legacy format)
        decoded = safe_base64_decode(url)
        if not decoded:
            return None

        # Parse decoded content
        if "@" in decoded:
            # Format: method:password@server:port
            userinfo, server_info = decoded.split("@", 1)
            method, password = userinfo.split(":", 1)
            server, port = server_info.split(":")

            return Proxy(
                type=ProxyType.SHADOWSOCKS,
                name=name or f"{server}:{port}",
                server=server,
                port=int(port),
                password=password,
                cipher=method,
                plugin=plugin,
                plugin_opts=plugin_opts if plugin_opts else None,
                udp=udp,
                raw=decoded
            )

        return None
    except Exception as e:
        print(f"Failed to parse SS URL: {e}")
        return None


def parse_ssr(url: str) -> Optional[Proxy]:
    """Parse ShadowsocksR URL
    Format: ssr://base64(server:port:protocol:method:obfs:base64(password)/?params)
    """
    try:
        url = url.replace("ssr://", "")
        decoded = safe_base64_decode(url)
        if not decoded:
            return None

        # Split main part and params
        main_part = decoded
        params = {}
        if "/?" in decoded:
            main_part, param_str = decoded.split("/?", 1)
            param_pairs = param_str.split("&")
            for pair in param_pairs:
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = safe_base64_decode(v) if v else ""

        # Parse main part: server:port:protocol:method:obfs:password_base64
        parts = main_part.split(":")
        if len(parts) < 6:
            return None

        server = parts[0]
        port = int(parts[1])
        protocol = parts[2]
        method = parts[3]
        obfs = parts[4]
        password = safe_base64_decode(parts[5])

        name = params.get("remarks", f"{server}:{port}")
        obfs_param = params.get("obfsparam", "")
        protocol_param = params.get("protoparam", "")

        return Proxy(
            type=ProxyType.SHADOWSOCKSR,
            name=name,
            server=server,
            port=port,
            password=password,
            cipher=method,
            protocol=protocol,
            protocol_param=protocol_param,
            obfs=obfs,
            obfs_param=obfs_param,
            raw=decoded
        )
    except Exception as e:
        print(f"Failed to parse SSR URL: {e}")
        return None


def parse_vmess(url: str) -> Optional[Proxy]:
    """Parse VMess URL
    Format: vmess://base64(json)
    """
    try:
        url = url.replace("vmess://", "")
        decoded = safe_base64_decode(url)
        if not decoded:
            return None

        data = json.loads(decoded)

        # Extract fields
        name = data.get("ps", "") or data.get("remark", "")
        server = data.get("add", "")
        port = int(data.get("port", 0))
        uuid = data.get("id", "")
        alter_id = int(data.get("aid", 0))
        security = data.get("scy", "auto")
        network = data.get("net", "tcp")
        tls_str = data.get("tls", "")
        tls = tls_str == "tls"

        # Network specific settings
        ws_path = None
        ws_headers = None
        h2_path = None
        h2_host = None
        grpc_service = None

        if network == "ws":
            ws_path = data.get("path", "/")
            host = data.get("host", "")
            if host:
                ws_headers = {"Host": host}
        elif network == "h2":
            h2_path = data.get("path", "/")
            host = data.get("host", "")
            if host:
                h2_host = [host]
        elif network == "grpc":
            grpc_service = data.get("path", "") or data.get("serviceName", "")

        sni = data.get("sni", "") or data.get("host", "")

        if not name:
            name = f"{server}:{port}"

        return Proxy(
            type=ProxyType.VMESS,
            name=name,
            server=server,
            port=port,
            uuid=uuid,
            alter_id=alter_id,
            security=security,
            network=network,
            ws_path=ws_path,
            ws_headers=ws_headers,
            h2_path=h2_path,
            h2_host=h2_host,
            grpc_service_name=grpc_service,
            tls=tls,
            sni=sni if sni else None,
            raw=decoded
        )
    except Exception as e:
        print(f"Failed to parse VMess URL: {e}")
        return None


def parse_trojan(url: str) -> Optional[Proxy]:
    """Parse Trojan URL
    Format: trojan://password@server:port?params#remark
    """
    try:
        url = url.replace("trojan://", "")

        # Extract remark
        name = ""
        if "#" in url:
            url, name = url.split("#", 1)
            name = urllib.parse.unquote(name)

        # Extract params
        params = {}
        if "?" in url:
            url, query = url.split("?", 1)
            params = urllib.parse.parse_qs(query)
            # Convert lists to single values
            params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

        # Parse password@server:port
        if "@" not in url:
            return None

        password, server_port = url.split("@", 1)
        if ":" not in server_port:
            return None

        server, port = server_port.rsplit(":", 1)

        # Extract network settings
        network = params.get("type", "tcp")
        ws_path = params.get("path")
        sni = params.get("sni") or params.get("peer")
        alpn_str = params.get("alpn")
        alpn = alpn_str.split(",") if alpn_str else None
        skip_cert = params.get("allowInsecure") == "1"

        ws_headers = None
        if params.get("host"):
            ws_headers = {"Host": params["host"]}

        if not name:
            name = f"{server}:{port}"

        return Proxy(
            type=ProxyType.TROJAN,
            name=name,
            server=server,
            port=int(port),
            password=password,
            network=network,
            ws_path=ws_path,
            ws_headers=ws_headers,
            tls=True,  # Trojan always uses TLS
            sni=sni,
            alpn=alpn,
            skip_cert_verify=skip_cert if skip_cert else None,
            raw=url
        )
    except Exception as e:
        print(f"Failed to parse Trojan URL: {e}")
        return None


def parse_hysteria2(url: str) -> Optional[Proxy]:
    """Parse Hysteria2 URL
    Format: hysteria2://password@server:port?params#remark
    or: hy2://password@server:port?params#remark
    """
    try:
        url = url.replace("hysteria2://", "").replace("hy2://", "")

        # Extract remark
        name = ""
        if "#" in url:
            url, name = url.split("#", 1)
            name = urllib.parse.unquote(name)

        # Extract params
        params = {}
        if "?" in url:
            url, query = url.split("?", 1)
            params = urllib.parse.parse_qs(query)
            params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

        # Parse password@server:port
        password, server_port = url.split("@", 1)
        server, port = server_port.rsplit(":", 1)

        sni = params.get("sni")
        obfs = params.get("obfs")
        obfs_password = params.get("obfs-password")
        up = params.get("up")
        down = params.get("down")

        if not name:
            name = f"{server}:{port}"

        return Proxy(
            type=ProxyType.HYSTERIA2,
            name=name,
            server=server,
            port=int(port),
            password=password,
            sni=sni,
            obfs=obfs,
            obfs_param=obfs_password,
            up=up,
            down=down,
            raw=url
        )
    except Exception as e:
        print(f"Failed to parse Hysteria2 URL: {e}")
        return None


def parse_proxy_url(url: str) -> Optional[Proxy]:
    """Parse a single proxy URL and return Proxy object"""
    url = url.strip()
    if not url:
        return None

    if url.startswith("ss://"):
        return parse_ss(url)
    elif url.startswith("ssr://"):
        return parse_ssr(url)
    elif url.startswith("vmess://"):
        return parse_vmess(url)
    elif url.startswith("trojan://"):
        return parse_trojan(url)
    elif url.startswith("hysteria2://") or url.startswith("hy2://"):
        return parse_hysteria2(url)
    else:
        print(f"Unsupported proxy type: {url[:20]}...")
        return None


def parse_clash_yaml(content: str) -> List[Proxy]:
    """Parse Clash YAML format subscription"""
    try:
        import yaml
        config = yaml.safe_load(content)

        if not config or 'proxies' not in config:
            return []

        proxies = []
        for item in config.get('proxies', []):
            if not isinstance(item, dict):
                continue

            ptype = item.get('type', '').lower()

            # Convert Clash format to our Proxy format
            if ptype == 'ss':
                proxy = Proxy(
                    type=ProxyType.SHADOWSOCKS,
                    name=item.get('name', ''),
                    server=item.get('server', ''),
                    port=item.get('port', 0),
                    password=item.get('password', ''),
                    cipher=item.get('cipher', ''),
                    plugin=item.get('plugin'),
                    plugin_opts=item.get('plugin-opts'),
                    udp=item.get('udp')
                )
                proxies.append(proxy)

            elif ptype == 'ssr':
                proxy = Proxy(
                    type=ProxyType.SHADOWSOCKSR,
                    name=item.get('name', ''),
                    server=item.get('server', ''),
                    port=item.get('port', 0),
                    password=item.get('password', ''),
                    cipher=item.get('cipher', ''),
                    protocol=item.get('protocol', ''),
                    protocol_param=item.get('protocol-param'),
                    obfs=item.get('obfs', ''),
                    obfs_param=item.get('obfs-param'),
                    udp=item.get('udp')
                )
                proxies.append(proxy)

            elif ptype == 'vmess':
                proxy = Proxy(
                    type=ProxyType.VMESS,
                    name=item.get('name', ''),
                    server=item.get('server', ''),
                    port=item.get('port', 0),
                    uuid=item.get('uuid', ''),
                    alter_id=item.get('alterId', 0),
                    security=item.get('cipher', 'auto'),
                    network=item.get('network', 'tcp'),
                    tls=item.get('tls', False),
                    sni=item.get('servername') or item.get('sni'),
                    skip_cert_verify=item.get('skip-cert-verify'),
                    udp=item.get('udp')
                )

                # Handle network specific options
                if proxy.network == 'ws':
                    ws_opts = item.get('ws-opts', {}) or item.get('ws-path')
                    if isinstance(ws_opts, dict):
                        proxy.ws_path = ws_opts.get('path')
                        proxy.ws_headers = ws_opts.get('headers')

                elif proxy.network == 'h2':
                    h2_opts = item.get('h2-opts', {})
                    if isinstance(h2_opts, dict):
                        proxy.h2_path = h2_opts.get('path')
                        proxy.h2_host = h2_opts.get('host')

                elif proxy.network == 'grpc':
                    grpc_opts = item.get('grpc-opts', {})
                    if isinstance(grpc_opts, dict):
                        proxy.grpc_service_name = grpc_opts.get('grpc-service-name')

                proxies.append(proxy)

            elif ptype == 'trojan':
                proxy = Proxy(
                    type=ProxyType.TROJAN,
                    name=item.get('name', ''),
                    server=item.get('server', ''),
                    port=item.get('port', 0),
                    password=item.get('password', ''),
                    sni=item.get('sni'),
                    skip_cert_verify=item.get('skip-cert-verify'),
                    alpn=item.get('alpn'),
                    udp=item.get('udp'),
                    network=item.get('network', 'tcp')
                )

                # Handle network options
                if proxy.network == 'ws':
                    ws_opts = item.get('ws-opts', {})
                    if isinstance(ws_opts, dict):
                        proxy.ws_path = ws_opts.get('path')
                        proxy.ws_headers = ws_opts.get('headers')

                proxies.append(proxy)

        return proxies

    except Exception as e:
        print(f"Failed to parse Clash YAML: {e}")
        return []


def parse_subscription(content: str) -> List[Proxy]:
    """Parse subscription content and return list of proxies"""
    proxies = []

    # First, try to parse as Clash YAML
    if 'proxies:' in content or 'Proxy:' in content:
        proxies = parse_clash_yaml(content)
        if proxies:
            return proxies

    # Try to decode if it's base64
    try:
        decoded = safe_base64_decode(content)
        if decoded and decoded != content:
            content = decoded
    except:
        pass

    # Split by lines and parse each
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip comments and metadata lines
        if line.startswith('#') or line.startswith('REMARKS=') or line.startswith('STATUS='):
            continue

        proxy = parse_proxy_url(line)
        if proxy:
            proxies.append(proxy)

    return proxies


if __name__ == "__main__":
    # Test with sample URLs
    test_ss = "ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@example.com:8388#Test%20SS"
    test_vmess = "vmess://eyJ2IjogIjIiLCAicHMiOiAiVGVzdCBWTWVzcyIsICJhZGQiOiAiZXhhbXBsZS5jb20iLCAicG9ydCI6ICI0NDMiLCAiaWQiOiAiMTIzNDU2NzgtMTIzNC0xMjM0LTEyMzQtMTIzNDU2Nzg5MDEyIiwgImFpZCI6ICIwIiwgIm5ldCI6ICJ3cyIsICJ0eXBlIjogIm5vbmUiLCAiaG9zdCI6ICJleGFtcGxlLmNvbSIsICJwYXRoIjogIi92bWVzcyIsICJ0bHMiOiAidGxzIn0="

    print("Testing SS parser:")
    proxy = parse_ss(test_ss)
    if proxy:
        print(f"  Name: {proxy.name}")
        print(f"  Server: {proxy.server}:{proxy.port}")
        print(f"  Cipher: {proxy.cipher}")

    print("\nTesting VMess parser:")
    proxy = parse_vmess(test_vmess)
    if proxy:
        print(f"  Name: {proxy.name}")
        print(f"  Server: {proxy.server}:{proxy.port}")
        print(f"  Network: {proxy.network}")
        print(f"  TLS: {proxy.tls}")
