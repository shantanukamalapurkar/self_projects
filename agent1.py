import os
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv(override=True)
openai_key = os.getenv('OPENAI_API_KEY')

first_tools=[\
    {
    "type": "function",
    "function":{
        "name":"get_exchange_rate",
        "description": "Get the current exchange rate of base currency and target currency",
        "parameters":{
            "type":"object",
            "properties":{
                "base_currency": {
                    "type": "string",
                    "description":"The base currency for exchange rate calculation i.e USD,EUR,INR"
                },
                "target_currency":{
                    "type": "string",
                    "description": "The target currency for exchange rate calculation i.e USD,EUR,INR"
                },
                "date":{
                    "type": "string",
                    "description": "A specific day to reference, in YYYY-MM-DD format"
                },
            },
            "required":["base_cuurency","target_currency"],
        },
    },
},
    #search internet
    {
        "type":"function",
        "function": {
            "name":"Search_Internet",
            "description":"Get Internet search results for real time information",
            "paremeters":{
                "type":"object",
                "properties":{
                    "search_query":{
                        "type":"string",
                        "description":"The query to search the web for",
                    }
                },
                "required":["search_query"],
            },
        },
    }
]
client = OpenAI()

messages = [{"role":"user",
             "content":"How much is a dollar worth in Japan? How about poland? Whats the current news in Argentina?"}]

response=client.chat.completions.create(
    model="gpt-4o-mini",
    messages = messages,
    tools=first_tools,
    tool_choice="auto"


)
#print(response, "\n")

#print(response.choices[0].message,"\n")


def pprint_response(response):
    print("--- Full Response ---\n")
    print(response, "\n")

    print("--- Chat Completion Message ---\n")
    print(response.choices[0].message,"\n")
    if response.choices[0].message.tool_calls:
        for i in range(0, len(response.choices[0].message.tool_calls)):
            print(f"--- Tool Call {i + 1} ---\n")
            print(f"Function: {response.choices[0].message.tool_calls[i].function.name}\n")
            print(f"Arguments: {response.choices[0].message.tool_calls[i].function.arguments}\n")



pprint_response(response)