#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SearchAPI Agent with A2A protocol support
"""

import sys
import os
import logging
from pathlib import Path
import click
from dotenv import load_dotenv

# 设置logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 删除旧的导入路径设置
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../samples/python")))

# 从当前项目导入mcp_server（作为MCP服务器运行）
try:
    from .mcp_server import mcp
    logger.info("Successfully imported MCP server")
except ImportError as e:
    logger.error(f"Failed to import MCP server: {e}")
    raise e


def main():
    """启动 SearchAPI MCP 服务器"""

    # 检查所需的API密钥
    searchapi_api_key = os.getenv("SEARCHAPI_API_KEY")

    if not searchapi_api_key:
        logger.warning("缺少SEARCHAPI_API_KEY环境变量，SearchAPI工具将无法正常工作")

    logger.info("Starting SearchAPI MCP server")

    # 启动MCP服务器
    mcp.run()


if __name__ == "__main__":
    main() 
