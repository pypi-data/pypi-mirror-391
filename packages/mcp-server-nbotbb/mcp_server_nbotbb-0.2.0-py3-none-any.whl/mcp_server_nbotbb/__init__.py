from .server import serve


def main():
    """MCP Time Server - Time and timezone conversion functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to handle time queries and timezone conversions"
    )
    parser.add_argument("--local-name", type=str, help="Override local name")

    args = parser.parse_args()
    asyncio.run(serve(args.local_name))


if __name__ == "__main__":
    main()
