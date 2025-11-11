#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
py-subconverter - Python Subscription Converter
将代理订阅转换为 Clash 配置
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from .proxy_parser import Proxy, ProxyType, parse_subscription
from .clash_generator import ClashGenerator
from .subscription_converter import SubscriptionConverter
from .dler_api_client import DlerAPIClient
from .ini_parser import INIConfigParser, parse_ini_config

__all__ = [
    "Proxy",
    "ProxyType",
    "parse_subscription",
    "ClashGenerator",
    "SubscriptionConverter",
    "DlerAPIClient",
    "INIConfigParser",
    "parse_ini_config",
    "__version__",
]
