from mcp.server.fastmcp import FastMCP

eur_inr=FastMCP("eur_inr")

@eur_inr.tool()
def eur_to_inr(a:float)->float:
    """converts euro amount to inr amount"""
    return a*100;

if __name__=="__main__":
    eur_inr.run()