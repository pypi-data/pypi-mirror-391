from .server import serve


def main():
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to handle product queries"
    )
    parser.add_argument("--product_db", type=str, help="Override local timezone")

    args = parser.parse_args()
    asyncio.run(serve(args.product_db))


if __name__ == "__main__":
    main()
