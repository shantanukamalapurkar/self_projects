from mcp.server.fastmcp import FastMCP
usd_inr = FastMCP("usd_inr")

@usd_inr.tool()
def usd_to_inr(a:float)-> float:
    """converts usd to inr using fixed rate of conversion"""
    return a*90.85


if __name__=="__main__":
    usd_inr.run()
