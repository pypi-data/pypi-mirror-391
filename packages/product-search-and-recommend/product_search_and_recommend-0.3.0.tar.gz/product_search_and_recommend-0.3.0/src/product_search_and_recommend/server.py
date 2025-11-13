# server.py
import json
from typing import Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import ValidationError

from .enums import ProductTools
from .models import ProductSearchInput
from .service import mock_product_database_query


class ProductService:
    def search_and_recommend(self, arguments: dict) -> dict:
        """处理商品查询请求"""
        try:
            # 使用 Pydantic 校验输入
            input_data = ProductSearchInput(**arguments)
        except ValidationError as e:
            raise ValueError(f"Invalid input: {e}")

        # 调用业务逻辑
        results = mock_product_database_query(input_data)
        
        return {
            "query_summary": {
                "total_products": len(input_data.product_list),
                "has_user_preferences": input_data.user_preferences is not None
            },
            "results": results
        }


async def serve(local_timezone: str | None = None) -> None:
    """启动 MCP 服务器（local_timezone 参数保留以兼容 time 服务器结构）"""
    server = Server("mcp-product")
    product_service = ProductService()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=ProductTools.PRODUCT_SEARCH.value,
                description="商品查询和推荐：根据用户提供的商品名称、品牌、规格及主要功效，查询并推荐匹配的商品。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "product_list": {
                            "type": "array",
                            "description": "商品查询列表...",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_name": {"type": "string"},
                                    "brand": {"type": "string"},
                                    "specification": {"type": "string"},
                                    "main_effect": {"type": "string"}
                                },
                                "required": ["main_effect"],
                                "additionalProperties": False
                            }
                        },
                        "user_preferences": {
                            "type": "object",
                            "properties": {
                                "price_preference": {
                                    "type": "string",
                                    "enum": ["cheapest", "balanced", "premium"]
                                },
                                "date_preference": {
                                    "type": "string",
                                    "enum": ["recent", "any"]
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "required": ["product_list"],
                    "additionalProperties": False
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        if name == ProductTools.PRODUCT_SEARCH.value:
            result = product_service.search_and_recommend(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)