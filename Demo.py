from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def substract(a:int,b:int)->int:
    """substract two numbers"""
    if a>b:
        return a-b
    elif a<b:
        return b-a
    else:
        return 0


def main():
    mcp.run(transport="stdio")


if __name__=="__main__":
    main()

