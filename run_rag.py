import sys
from prepare_content import search_by_query
from ollama import chat

query = "What are human rights violations in North Korea?"

if len(sys.argv) > 1:
    query = sys.argv[1]

context = search_by_query(query)

prompt = f"<|content_start>{context} <|content_end> {query}"

response = chat(model="deepseek-r1:8b", messages=[
    {
        "role": "user",
        "content": prompt,
    },
])

print(response.message.content)
