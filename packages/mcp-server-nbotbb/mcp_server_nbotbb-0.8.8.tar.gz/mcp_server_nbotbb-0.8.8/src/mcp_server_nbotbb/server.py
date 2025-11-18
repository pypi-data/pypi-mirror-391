import json
import mysql.connector
from mysql.connector import Error
from typing import Any, Dict, List, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.shared.exceptions import McpError


# ========== MySQL 配置 ==========
MYSQL_CONFIG = {
    'host': 'rm-uf659xxpoxch0io8avo.mysql.rds.aliyuncs.com',  # 注意：你之前写错了域名！
    'port': 3306,
    'user': 'nongshang_user',
    'password': 'NongShang@2024!',
    'database': 'products_db',
    'charset': 'utf8mb4',
    'autocommit': True,
    'pool_name': 'mcp_pool',
    'pool_size': 5
}

import decimal

def _convert_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)  # 或 str(obj) 如果你希望保留精度
    elif isinstance(obj, dict):
        return {k: _convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimal(item) for item in obj]
    else:
        return obj

# ========== 工具函数 ==========
def _query_products_mysql(product_list: List[Dict[str, str]], query_field: str = "product_name") -> Dict[str, List]:
    result = {}
    connection = None
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)  # 返回 dict 而非 tuple

        for prod in product_list:
            name = prod.get(query_field)
            if not name:
                continue

            # 查询 products 表
            cursor.execute("SELECT * FROM products WHERE name LIKE %s LIMIT 5", (f"%{name}%",))
            products = cursor.fetchall()

            # 为每个 product 查询 skus
            for p in products:
                cursor.execute("SELECT * FROM product_skus WHERE goods_id = %s", (p["goods_id"],))
                p["skus"] = cursor.fetchall()

            if products:
                result[name] = products

    except Error as e:
        raise McpError(f"MySQL query failed: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return result


def agro_product_search(product_list: List[Dict[str, str]], user_preferences: Dict[str, str] = None) -> Dict[str, Any]:
    try:
        results = _query_products_mysql(product_list, "product_name")
        if not results:
            results = _query_products_mysql(product_list, "main_effect")

        # 转换 Decimal → float
        results = _convert_decimal(results)
        return {"message": "Success", "data": results}
    except Exception as e:
        return {"message": "Error", "error": str(e)}


# ========== 其他工具函数保持不变 ==========
def agro_product_recommend(crop: str, pest_or_disease: str, region: str = None, growth_stage: str = None) -> Dict[str, Any]:
    recommendations = []
    if "锈病" in pest_or_disease and crop == "小麦":
        recommendations.append({
            "product_name": "戊唑醇悬浮剂",
            "recommend_reason": f"{crop}锈病防治",
            "dosage": "亩用30ml，兑水30kg喷雾",
            "safety_interval": "14天"
        })
    else:
        recommendations.append({
            "product_name": "通用型杀菌剂",
            "recommend_reason": f"针对{pest_or_disease}",
            "dosage": "请咨询农技员",
            "safety_interval": "N/A"
        })
    return {"message": "Success", "data": recommendations}


def extract_delivery_address(
    name: str = "", phone: str = "", province: str = "",
    city: str = "", district: str = "", detailed_address: str = "", postal_code: str = ""
) -> Dict[str, Any]:
    if province == city:
        city = ""
    cleaned = {
        "name": name.strip(),
        "phone": phone.strip(),
        "province": province.strip(),
        "city": city.strip(),
        "district": district.strip(),
        "detailed_address": detailed_address.strip(),
        "postal_code": postal_code.strip()
    }
    return {"message": "Success", "data": cleaned}


# ========== MCP Server ==========
async def serve(db_path: str) -> None:
    # 注意：现在 db_path 参数不再使用，但保留签名以兼容启动方式
    server = Server("nbotbb-agro-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="agro_product_search",
                description="根据结构化商品列表查询农资库存与价格",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "product_list": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_name": {"type": "string"},
                                    "brand": {"type": "string"},
                                    "specification": {"type": "string"},
                                    "main_effect": {"type": "string"}
                                },
                                "required": ["product_name"]
                            }
                        },
                        "user_preferences": {"type": "object"}
                    },
                    "required": ["product_list"]
                }
            ),
            Tool(
                name="agro_product_recommend",
                description="基于作物、病虫害推荐产品",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crop": {"type": "string"},
                        "pest_or_disease": {"type": "string"},
                        "region": {"type": "string"},
                        "growth_stage": {"type": "string"}
                    },
                    "required": ["crop", "pest_or_disease"]
                }
            ),
            Tool(
                name="extract_delivery_address",
                description="标准化地址字段",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "phone": {"type": "string"},
                        "province": {"type": "string"},
                        "city": {"type": "string"},
                        "district": {"type": "string"},
                        "detailed_address": {"type": "string"},
                        "postal_code": {"type": "string"}
                    }
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        try:
            if name == "agro_product_search":
                res = agro_product_search(
                    product_list=arguments["product_list"],
                    user_preferences=arguments.get("user_preferences")
                )
            elif name == "agro_product_recommend":
                res = agro_product_recommend(
                    crop=arguments["crop"],
                    pest_or_disease=arguments["pest_or_disease"],
                    region=arguments.get("region"),
                    growth_stage=arguments.get("growth_stage")
                )
            elif name == "extract_delivery_address":
                res = extract_delivery_address(**{k: v for k, v in arguments.items() if k in [
                    "name", "phone", "province", "city", "district", "detailed_address", "postal_code"
                ]})
            else:
                raise ValueError(f"Unknown tool: {name}")

            return [TextContent(type="text", text=json.dumps(res, ensure_ascii=False))]

        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"message": "Error", "error": str(e)}, ensure_ascii=False))]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)