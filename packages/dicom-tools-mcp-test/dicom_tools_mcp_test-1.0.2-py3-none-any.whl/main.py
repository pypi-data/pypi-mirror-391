#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM 工具 MCP 服务器主文件

基于 MCP (Model Context Protocol) 的 DICOM 医学影像文件分析工具的Python实现。
"""

import os
import asyncio
import json
import logging
import sys
from typing import Any, Dict

# 设置标准输出编码为 UTF-8 (Windows 兼容性)
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置MCP服务器所需的导入
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    from pydantic import BaseModel
except ImportError as e:
    print(f"错误: 缺少必要的MCP依赖库: {e}", file=sys.stderr)
    print("请运行: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# 导入DICOM工具
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dicom_tools.scanner import scan_dicom_directory_tool
from dicom_tools.parser import parse_dicom_file_tool
from dicom_tools.mapping import series_mapping_tool, file_mapping_tool
from dicom_tools.exporter import export_dicom_json_tool
from upload import Analysis_dicom_directory_tool, separate_series_by_patient_tool
from smart_analyzer import smart_analyze_directory_tool, check_and_split_if_needed_tool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
server = Server("dicom-tools-python")


# 工具参数模型
class DirectoryPathArgs(BaseModel):
    directory_path: str


class DirectoryPathWithSeriesArgs(BaseModel):
    directory_path: str
    series_type: str


class FilePathArgs(BaseModel):
    file_path: str

class fileforsep(BaseModel):
    fileforsep: str

class SmartAnalyzeArgs(BaseModel):
    directory_path: str
    series_threshold: int = 5
    patient_threshold: int = 2

class CheckAndSplitArgs(BaseModel):
    directory_path: str
    series_threshold: int = 5
    auto_split: bool = True

@server.list_tools()
async def list_tools() -> list[Tool]:
    """注册所有可用的DICOM工具"""
    return [
        Tool(
            name="scan-dicom-directory",
            description="扫描指定目录下所有可读的 .dcm 文件，汇总患者数、序列数、文件数和总字节数，返回 JSON 文本；目录需存在并可访问。",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "待扫描的本地目录路径，绝对路径，必须存在且可读"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="get-dicom-series-mapping",
            description="扫描目录并生成患者到序列的详细映射，包含每个序列的文件列表，结果以 JSON 数组返回，帮助定位同一患者的各序列文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "扫描的本地目录路径，绝对路径，必须存在且可读"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="export-dicom-json",
            description="导出目录内 DICOM 扫描结果的完整 JSON 文本，包含患者、序列及文件明细，适合持久化存储或后续分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "扫描的本地目录路径，绝对路径，必须存在且可读"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="parse-dicom-file",
            description="解析单个 DICOM 文件，提取 PatientID、PatientName、SeriesInstanceUID、SeriesDescription 等元数据，返回结构化 JSON；无效文件会返回错误说明。",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "待解析的本地 DICOM 文件路径，需指向实际存在的 .dcm 文件"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="Analysis_dicom_directory",
            description="扫描目录中的 DICOM 序列，按 series_type 选择分析流程并上传到预配置的远端分析服务，返回上传结果及访问 URL。",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "包含待分析 DICOM 序列的本地目录路径，必须存在且具备读取权限"
                    },
                    "series_type": {
                        "type": "string",
                        "description": "分析流程类型：`1`=主动脉分析，`9`=二尖瓣分析，其他值将被拒绝"
                    }
                },
                "required": ["directory_path", "series_type"]
            }
        ),
        Tool(
            name="fileforsep",
            description="按患者和序列拆分目录下的 DICOM 文件，生成新的子目录结构，并以 JSON 返回整理后的统计结果。",
            inputSchema={
                "type": "object",
                "properties": {
                    "fileforsep": {
                        "type": "string",
                        "description": "待整理的顶层目录路径，执行过程中会在同级创建输出目录"
                    }
                }, 
                "required": ["fileforsep"]
            }
        ),
        Tool(
            name="smart_analyze_directory",
            description="【智能分析工具】扫描目录并进行智能决策：检测序列数量，评估上传风险，提供拆分建议。结合思维链展示决策过程，包括患者详情、序列统计和下一步操作建议。适用于上传前的预检和决策。",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "待分析的本地目录路径，必须存在且可读"
                    },
                    "series_threshold": {
                        "type": "integer",
                        "description": "序列数阈值（默认2），超过此值建议拆分",
                        "default": 2
                    },
                    "patient_threshold": {
                        "type": "integer",
                        "description": "患者数阈值（默认1），超过此值建议按患者拆分",
                        "default": 1
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="check_and_split_if_needed",
            description="【一键智能处理】检测目录并根据需要自动拆分。先进行智能分析，如果序列过多且包含多患者，可自动执行按患者拆分。返回分析结果和拆分结果（如已执行）。推荐用于大型数据集的自动化处理。",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "待处理的本地目录路径，必须存在且可读"
                    },
                    "series_threshold": {
                        "type": "integer",
                        "description": "序列数阈值（默认5），超过此值触发拆分判断",
                        "default": 5
                    },
                    "auto_split": {
                        "type": "boolean",
                        "description": "是否自动执行拆分（默认true），false则仅返回建议",
                        "default": True
                    }
                },
                "required": ["directory_path"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """处理工具调用请求"""
    try:
        logger.info(f"调用工具: {name}, 参数: {arguments}")

        if name == "scan-dicom-directory":
            args = DirectoryPathArgs(**arguments)
            result = await scan_dicom_directory_tool(args.directory_path)

        elif name == "get-dicom-series-mapping":
            args = DirectoryPathArgs(**arguments)
            result = await series_mapping_tool(args.directory_path)

        elif name == "get-dicom-file-mapping":
            args = DirectoryPathArgs(**arguments)
            result = await file_mapping_tool(args.directory_path)

        elif name == "export-dicom-json":
            args = DirectoryPathArgs(**arguments)
            result = await export_dicom_json_tool(args.directory_path)

        elif name == "parse-dicom-file":
            args = FilePathArgs(**arguments)
            result = await parse_dicom_file_tool(args.file)

        elif name == "Analysis_dicom_directory":
            args = DirectoryPathWithSeriesArgs(**arguments)
            result = await Analysis_dicom_directory_tool(args.directory_path, args.series_type)
        elif name == "fileforsep":
            args = fileforsep(**arguments)
            result = await separate_series_by_patient_tool(args.fileforsep)
        elif name == "smart_analyze_directory":
            args = SmartAnalyzeArgs(**arguments)
            result = await smart_analyze_directory_tool(
                args.directory_path, 
                args.series_threshold, 
                args.patient_threshold
            )
        elif name == "check_and_split_if_needed":
            args = CheckAndSplitArgs(**arguments)
            result = await check_and_split_if_needed_tool(
                args.directory_path,
                args.series_threshold,
                args.auto_split
            )
        else:
            raise ValueError(f"未知工具: {name}")

        # 转换结果格式为MCP标准格式
        return [
            TextContent(
                type="text",
                text=content["text"]
            )
            for content in result["content"]
            if content["type"] == "text"
        ]

    except Exception as e:
        logger.error(f"工具调用失败: {name}, 错误: {e}", exc_info=True)

        error_response = {
            "error": True,
            "message": f"工具 {name} 执行失败: {str(e)}"
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(error_response, ensure_ascii=False)
            )
        ]


async def main():
    """启动MCP服务器"""
    try:
        logger.info("启动 DICOM 工具 MCP 服务器 ...")

        # 使用stdio传输启动服务器
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行失败: {e}", exc_info=True)
        sys.exit(1)


def run():
    """同步入口函数，用于 uvx 调用"""
    # 设置事件循环策略（Windows兼容性）
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # 运行服务器
    asyncio.run(main())


if __name__ == "__main__":
    run()