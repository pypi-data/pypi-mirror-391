from datetime import datetime, timedelta
from enum import Enum
import json
from typing import Sequence


from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError

from pydantic import BaseModel


class TestTools(str, Enum):
    NAME_KK = "name_kk"
    
class KKResult(BaseModel):
    namekk: str

class KKInput(BaseModel):
    name: str

class TestServer:
    def name_kk(self, kkname: str) -> KKResult:
        res = f"{kkname}，你好！很高兴见到你！我是你的AI助手。"
        return KKResult(namekk=res)

async def serve(local_name: str | None = None) -> None:
    server = Server("mcp-test")
    test_server = TestServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=TestTools.NAME_KK.value,
                description="从对话中提取人名",
                input_schema={
                    "type": "object",
                    "properties": {
                        "kkname": {
                            "type": "string",
                            "description": "对话中的人名(例如：张伟，王一博，啵啵)",
                        }
                    },
                    "required": ["kkname"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        try:
            match name:
                case TestTools.NAME_KK.value:
                    kkname = arguments["kkname"]
                    if not kkname:
                        return [TextContent(text="请输入人名")]
                    result = test_server.name_kk(kkname=kkname)
                case _:
                    raise ValueError(f"Unknown tool: {name}")

            return [
                TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
            ]

        except Exception as e:
            raise McpError(f"Error calling tool {name}: {str(e)}") from e

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)

   


    



   
