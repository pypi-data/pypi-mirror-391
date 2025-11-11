#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clash Config Generator - Generate Clash configuration from proxy list
"""

import yaml
from typing import List, Dict, Any, Optional
from .proxy_parser import Proxy, ProxyType


class ClashGenerator:
    """Generate Clash format configuration"""

    def __init__(self):
        self.base_config = {
            "port": 7890,
            "socks-port": 7891,
            "allow-lan": False,
            "mode": "rule",
            "log-level": "info",
            "external-controller": "127.0.0.1:9090",
        }

    def proxy_to_clash(self, proxy: Proxy) -> Optional[Dict[str, Any]]:
        """Convert a Proxy object to Clash proxy dict"""
        if proxy.type == ProxyType.SHADOWSOCKS:
            return self._ss_to_clash(proxy)
        elif proxy.type == ProxyType.SHADOWSOCKSR:
            return self._ssr_to_clash(proxy)
        elif proxy.type == ProxyType.VMESS:
            return self._vmess_to_clash(proxy)
        elif proxy.type == ProxyType.TROJAN:
            return self._trojan_to_clash(proxy)
        elif proxy.type == ProxyType.HYSTERIA2:
            return self._hysteria2_to_clash(proxy)
        else:
            print(f"Unsupported proxy type for Clash: {proxy.type}")
            return None

    def _ss_to_clash(self, proxy: Proxy) -> Dict[str, Any]:
        """Convert Shadowsocks to Clash format"""
        clash_proxy = {
            "name": proxy.name,
            "type": "ss",
            "server": proxy.server,
            "port": proxy.port,
            "cipher": proxy.cipher,
            "password": proxy.password,
        }

        if proxy.plugin:
            clash_proxy["plugin"] = proxy.plugin
            if proxy.plugin_opts:
                # Format plugin-opts
                opts_list = [f"{k}={v}" for k, v in proxy.plugin_opts.items()]
                clash_proxy["plugin-opts"] = {
                    "mode": proxy.plugin_opts.get("obfs", ""),
                    "host": proxy.plugin_opts.get("obfs-host", "")
                } if proxy.plugin == "obfs" else proxy.plugin_opts

        if proxy.udp is not None:
            clash_proxy["udp"] = proxy.udp

        return clash_proxy

    def _ssr_to_clash(self, proxy: Proxy) -> Dict[str, Any]:
        """Convert ShadowsocksR to Clash format"""
        clash_proxy = {
            "name": proxy.name,
            "type": "ssr",
            "server": proxy.server,
            "port": proxy.port,
            "cipher": proxy.cipher,
            "password": proxy.password,
            "protocol": proxy.protocol,
            "obfs": proxy.obfs,
        }

        if proxy.protocol_param:
            clash_proxy["protocol-param"] = proxy.protocol_param
        if proxy.obfs_param:
            clash_proxy["obfs-param"] = proxy.obfs_param
        if proxy.udp is not None:
            clash_proxy["udp"] = proxy.udp

        return clash_proxy

    def _vmess_to_clash(self, proxy: Proxy) -> Dict[str, Any]:
        """Convert VMess to Clash format"""
        clash_proxy = {
            "name": proxy.name,
            "type": "vmess",
            "server": proxy.server,
            "port": proxy.port,
            "uuid": proxy.uuid,
            "alterId": proxy.alter_id,
            "cipher": proxy.security,
        }

        if proxy.udp is not None:
            clash_proxy["udp"] = proxy.udp
        if proxy.tls:
            clash_proxy["tls"] = True
            if proxy.sni:
                clash_proxy["servername"] = proxy.sni
            if proxy.skip_cert_verify:
                clash_proxy["skip-cert-verify"] = True
            if proxy.alpn:
                clash_proxy["alpn"] = proxy.alpn

        # Network settings
        clash_proxy["network"] = proxy.network

        if proxy.network == "ws":
            ws_opts = {}
            if proxy.ws_path:
                ws_opts["path"] = proxy.ws_path
            if proxy.ws_headers:
                ws_opts["headers"] = proxy.ws_headers
            if ws_opts:
                clash_proxy["ws-opts"] = ws_opts

        elif proxy.network == "h2":
            h2_opts = {}
            if proxy.h2_path:
                h2_opts["path"] = proxy.h2_path
            if proxy.h2_host:
                h2_opts["host"] = proxy.h2_host
            if h2_opts:
                clash_proxy["h2-opts"] = h2_opts

        elif proxy.network == "grpc":
            grpc_opts = {}
            if proxy.grpc_service_name:
                grpc_opts["grpc-service-name"] = proxy.grpc_service_name
            if grpc_opts:
                clash_proxy["grpc-opts"] = grpc_opts

        return clash_proxy

    def _trojan_to_clash(self, proxy: Proxy) -> Dict[str, Any]:
        """Convert Trojan to Clash format"""
        clash_proxy = {
            "name": proxy.name,
            "type": "trojan",
            "server": proxy.server,
            "port": proxy.port,
            "password": proxy.password,
        }

        if proxy.sni:
            clash_proxy["sni"] = proxy.sni
        if proxy.alpn:
            clash_proxy["alpn"] = proxy.alpn
        if proxy.skip_cert_verify:
            clash_proxy["skip-cert-verify"] = True
        if proxy.udp is not None:
            clash_proxy["udp"] = proxy.udp

        # Network settings for trojan
        if proxy.network and proxy.network != "tcp":
            clash_proxy["network"] = proxy.network
            if proxy.network == "ws":
                ws_opts = {}
                if proxy.ws_path:
                    ws_opts["path"] = proxy.ws_path
                if proxy.ws_headers:
                    ws_opts["headers"] = proxy.ws_headers
                if ws_opts:
                    clash_proxy["ws-opts"] = ws_opts
            elif proxy.network == "grpc":
                grpc_opts = {}
                if proxy.grpc_service_name:
                    grpc_opts["grpc-service-name"] = proxy.grpc_service_name
                if grpc_opts:
                    clash_proxy["grpc-opts"] = grpc_opts

        return clash_proxy

    def _hysteria2_to_clash(self, proxy: Proxy) -> Dict[str, Any]:
        """Convert Hysteria2 to Clash format"""
        clash_proxy = {
            "name": proxy.name,
            "type": "hysteria2",
            "server": proxy.server,
            "port": proxy.port,
            "password": proxy.password,
        }

        if proxy.sni:
            clash_proxy["sni"] = proxy.sni
        if proxy.skip_cert_verify:
            clash_proxy["skip-cert-verify"] = True
        if proxy.obfs:
            clash_proxy["obfs"] = proxy.obfs
        if proxy.obfs_param:
            clash_proxy["obfs-password"] = proxy.obfs_param
        if proxy.up:
            clash_proxy["up"] = proxy.up
        if proxy.down:
            clash_proxy["down"] = proxy.down

        return clash_proxy

    def generate_proxy_groups(self, proxy_names: List[str]) -> List[Dict[str, Any]]:
        """Generate default proxy groups"""
        return [
            {
                "name": "PROXY",
                "type": "select",
                "proxies": ["Auto"] + proxy_names
            },
            {
                "name": "Auto",
                "type": "url-test",
                "proxies": proxy_names,
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300
            },
            {
                "name": "Fallback",
                "type": "fallback",
                "proxies": proxy_names,
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300
            }
        ]

    def generate_rules(self) -> List[str]:
        """Generate default rules"""
        return [
            "DOMAIN-SUFFIX,google.com,PROXY",
            "DOMAIN-SUFFIX,youtube.com,PROXY",
            "DOMAIN-SUFFIX,facebook.com,PROXY",
            "DOMAIN-SUFFIX,twitter.com,PROXY",
            "DOMAIN-SUFFIX,telegram.org,PROXY",
            "DOMAIN-KEYWORD,google,PROXY",
            "DOMAIN-SUFFIX,github.com,PROXY",
            "DOMAIN-SUFFIX,githubusercontent.com,PROXY",
            "GEOIP,CN,DIRECT",
            "MATCH,PROXY"
        ]

    def generate_config(
        self,
        proxies: List[Proxy],
        rules: Optional[List[str]] = None,
        proxy_groups: Optional[List[Dict[str, Any]]] = None,
        base_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate complete Clash configuration"""

        # Convert proxies to Clash format
        clash_proxies = []
        proxy_names = []
        for proxy in proxies:
            clash_proxy = self.proxy_to_clash(proxy)
            if clash_proxy:
                clash_proxies.append(clash_proxy)
                proxy_names.append(clash_proxy["name"])

        if not clash_proxies:
            raise ValueError("No valid proxies found")

        # Build final config
        config = base_config or self.base_config.copy()
        config["proxies"] = clash_proxies

        # Generate proxy groups
        if proxy_groups is None:
            proxy_groups = self.generate_proxy_groups(proxy_names)
        config["proxy-groups"] = proxy_groups

        # Generate rules
        if rules is None:
            rules = self.generate_rules()
        config["rules"] = rules

        # Convert to YAML with proper indentation
        # Use custom Dumper to ensure proper list indentation
        class CustomDumper(yaml.SafeDumper):
            def increase_indent(self, flow=False, indentless=False):
                return super(CustomDumper, self).increase_indent(flow, False)

        return yaml.dump(config, Dumper=CustomDumper, allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2)

    def load_external_rules(self, rule_url: str) -> List[str]:
        """Load rules from external source (for future implementation)"""
        # This would fetch and parse rules from URLs
        # For now, return default rules
        return self.generate_rules()


def generate_clash_config(proxies: List[Proxy], **kwargs) -> str:
    """Convenience function to generate Clash config"""
    generator = ClashGenerator()
    return generator.generate_config(proxies, **kwargs)


if __name__ == "__main__":
    from proxy_parser import parse_proxy_url

    # Test
    test_ss = "ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@example.com:8388#Test%20SS"
    proxy = parse_proxy_url(test_ss)

    if proxy:
        generator = ClashGenerator()
        config = generator.generate_config([proxy])
        print(config)
