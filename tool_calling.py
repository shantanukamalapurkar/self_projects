import os
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
os.environ["LANGCHAIN_TRACING_V2"] = "True"
load_dotenv(override=True)
@tool
def add(a:int,b:int)->int:
    """Adds two integers"""
    return a+b

@tool
def multiply(a:int,b:int)->int:
    """Multiply two integers"""
    return a*b


tools = [add, multiply]

llm = ChatOpenAI(model="gpt-4o-mini")
llm_openai = llm.bind_tools(tools)

query = "What is 3+3 and what is 41*17?"
#result = llm_openai.invoke(query)
result=llm.bind_tools(tools).invoke(query)
tools_messages=[]
for call in result.tool_calls:
    tool_name=call["name"]
    tool_args=call["args"]

    for tool in tools:
        if tool.name==tool_name:
            output=tool.invoke(tool_args)

            tools_messages.append(
                ToolMessage(
                    content=str(output),
                    tool_call_id=call["id"]
                )
            )

final_response = llm.invoke([result,*tools_messages])

print(final_response.content)





