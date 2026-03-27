from ollama import embed, chat

embeddings = embed(model="nomic-embed-text", input=["Here is an example sentence","Here's a second one!"])

print(len(embeddings['embeddings'][0]))

response = chat(model='deepseek-r1:8b', messages=[
    {
        'role': 'user',
        'content': 'Why did the chicken cross the road?',
    },
])

print(response.message.content)
