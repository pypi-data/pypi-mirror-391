from datetime import datetime
from enum import Enum
import json
from typing import Sequence

from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.shared.exceptions import McpError

from pydantic import BaseModel


class TimeTools(str, Enum):
    GET_CURRENT_TIME = "get_current_time"


class TimeResult(BaseModel):
    timezone: str
    datetime: str
    day_of_week: str
    is_dst: bool


def get_local_tz(local_tz_override: str | None = None) -> ZoneInfo:
    if local_tz_override:
        return ZoneInfo(local_tz_override)
    local_tzname = get_localzone_name()
    if local_tzname:
        return ZoneInfo(local_tzname)
    return ZoneInfo("UTC")


def get_zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except Exception as e:
        raise McpError(f"Invalid timezone: {e}")


class TimeServer:
    def get_current_time(self, timezone_name: str) -> TimeResult:
        timezone = get_zoneinfo(timezone_name)
        now = datetime.now(timezone)
        return TimeResult(
            timezone=timezone_name,
            datetime=now.isoformat(timespec="seconds"),
            day_of_week=now.strftime("%A"),
            is_dst=bool(now.dst()),
        )


async def serve(local_timezone: str | None = None) -> None:
    server = Server("mcp-server-nbotbb")
    time_server = TimeServer()
    local_tz = str(get_local_tz(local_timezone))

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=TimeTools.GET_CURRENT_TIME.value,
                description="Get current time in a specific timezone",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": f"IANA timezone name (e.g., 'Asia/Shanghai'). Default local: '{local_tz}'"
                        }
                    },
                    "required": ["timezone"],
                },
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        try:
            if name != TimeTools.GET_CURRENT_TIME.value:
                raise ValueError(f"Unknown tool: {name}")

            timezone = arguments.get("timezone")
            if not timezone:
                raise ValueError("Missing required argument: timezone")

            result = time_server.get_current_time(timezone)

            # ✅ 关键：返回带 "message" 的 JSON 字符串
            response = {
                "message": "Success",
                "data": result.model_dump()
            }
            return [TextContent(type="text", text=json.dumps(response))]

        except Exception as e:
            # ✅ 错误也返回结构化 JSON（带 message）
            error_response = {
                "message": "Error",
                "error": str(e)
            }
            return [TextContent(type="text", text=json.dumps(error_response))]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)