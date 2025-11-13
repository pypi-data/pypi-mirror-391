from .server import serve

def main():
    import asyncio
    asyncio.run(serve())