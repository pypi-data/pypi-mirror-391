#!/usr/bin/env python3
"""
构建前脚本：根据环境变量设置网关地址

环境变量：
- GATEWAY_ENVIRONMENT: production 或 test (默认 test)
"""

import os
import sys
from pathlib import Path

# 获取环境
environment = os.getenv("GATEWAY_ENVIRONMENT", "test")

# 网关地址映射
GATEWAY_URLS = {
    "production": "http://agent-builder-gateway.sensedeal.vip",
    "test": "http://agent-builder-gateway-test.sensedeal.vip",
}

if environment not in GATEWAY_URLS:
    print(f"Error: Invalid GATEWAY_ENVIRONMENT '{environment}'. Must be 'production' or 'test'.", file=sys.stderr)
    sys.exit(1)

gateway_url = GATEWAY_URLS[environment]
print(f"Setting gateway URL for {environment} environment: {gateway_url}")

# 查找并修改 client.py
client_file = Path(__file__).parent.parent / "src" / "gateway_sdk" / "client.py"

if not client_file.exists():
    print(f"Error: client.py not found at {client_file}", file=sys.stderr)
    sys.exit(1)

# 读取文件
content = client_file.read_text(encoding="utf-8")

# 替换 DEFAULT_GATEWAY_URL
lines = content.split("\n")
new_lines = []
replaced = False

for line in lines:
    if line.strip().startswith("DEFAULT_GATEWAY_URL"):
        new_lines.append(f'DEFAULT_GATEWAY_URL = "{gateway_url}"')
        replaced = True
        print(f"✓ Replaced DEFAULT_GATEWAY_URL with {gateway_url}")
    else:
        new_lines.append(line)

if not replaced:
    print("Warning: DEFAULT_GATEWAY_URL not found in client.py", file=sys.stderr)

# 写回文件
client_file.write_text("\n".join(new_lines), encoding="utf-8")
print(f"✓ Updated {client_file}")
