import asyncio
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from pathlib import Path
from agents.mcp import MCPServerStdio
from agents import Agent, Runner, trace
from dotenv import load_dotenv

load_dotenv(override=True)

class FXState(TypedDict, total=False):
    query: str
    currency: Literal["USD", "EUR"]
    amount: float
    inr: float
    answer: str


model = "gpt-4o-mini"


async def router_node(state: FXState) -> FXState:
    q = state["query"].lower()
    if "usd" in q or "dollar" in q:
        return {"currency": "USD"}
    if "eur" in q or "euro" in q:
        return {"currency": "EUR"}
    return {"answer": "Please tell me the currency {USD or EUR}.", "inr": 0.0}


def route_fn(state: FXState):
    if state.get("answer"):
        return "done"
    return state["currency"]


def make_usd_node(usd_mcp:MCPServerStdio):
    async def usd_node(state:FXState) -> FXState:
        agent = Agent(
            name="usd converter",
            model=model,
            instructions="Call usd_to_inr for USD amounts and return INR.",
            mcp_servers=[usd_mcp]
        )
        result = await Runner.run(agent,state["query"])
        return {"answer":result.final_output}
    return usd_node


def make_eur_node(eur_mcp:MCPServerStdio):
    async def eur_node(state:FXState,eur_mcp:MCPServerStdio)->FXState:
        agent=Agent(
            name="eur converter",
            model=model,
            instructions="Call eur_to_inr for EUR amounts and return INR.",
            mcp_servers=[eur_mcp]
        )

        result = await Runner.run(agent,state["query"])
        return {"answer":result.final_output}
    return eur_node


async def main():
    usd_params= {"command": "uv", "args": ["run", "usd_inr_converter.py"]}
    eur_params = {"command": "uv", "args": ["run", "eur_inr_converter.py"]}

    async with MCPServerStdio (params=usd_params) as usd_mcp, MCPServerStdio(params=eur_params) as eur_mcp:

        g= StateGraph(FXState)

        g.add_node("router",router_node)
        g.add_node("USD", make_usd_node(usd_mcp))
        g.add_node("EUR", make_eur_node(eur_mcp))
        g.add_edge(START,"router")
        g.add_conditional_edges("router",route_fn,{"USD":"USD","EUR":"EUR","done":END})
        g.add_edge("USD",END)
        g.add_edge("EUR", END)

        app = g.compile()

        out = await app.ainvoke({"query":"hey i have 100k in USD. what's the value in INR? I also have 50k in EUR. so how much is total INR i have?"})
        print(out["answer"])



if __name__=="__main__":
    asyncio.run(main())
