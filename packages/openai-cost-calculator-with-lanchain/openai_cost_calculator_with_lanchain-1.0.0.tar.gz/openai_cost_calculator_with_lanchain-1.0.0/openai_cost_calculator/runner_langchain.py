from langchain_openai import ChatOpenAI
from openai_cost_calculator import estimate_cost_typed
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

messages = [
    (
        "system",
        "You are a helpful translator. Translate the user sentence to French.",
    ),
    ("human", "I love programming."),
]

response = model.invoke(messages)
print(estimate_cost_typed(response, is_langchain_response=True))