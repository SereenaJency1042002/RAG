import psycopg2
from ollama import embed
from database_connect_embeddings import get_psql_session, TextEmbedding

query =  "human rights violations in North Korea"

def get_query_embedding(query):
    return embed(
        model="nomic-embed-text",
        input=[query]
    )["embeddings"][0]

def search_embeddings(query_embedding, session, limit=5):
    return session.query(
        TextEmbedding.id,
        TextEmbedding.sentence_number,
        TextEmbedding.content,
        TextEmbedding.file_name,
        TextEmbedding.embedding.cosine_distance(query_embedding).label("distance")
    ).order_by("distance").limit(limit).all()

def get_surrounding_sentences(entry_ids, file_names, group_window_size, session):
    surrounding_sentences = []
    for entry_id, file_name in zip(entry_ids, file_names):
        surrounding_sentences.append(
            session.query(
                TextEmbedding.id,
                TextEmbedding.sentence_number,
                TextEmbedding.content,
                TextEmbedding.file_name
            )
            .filter(TextEmbedding.id >= entry_id - group_window_size)
            .filter(TextEmbedding.id <= entry_id + group_window_size)
            .filter(TextEmbedding.file_name == file_name).all()
        )
    return surrounding_sentences

if __name__ == "__main__":
    session = get_psql_session()
    query_embedding = get_query_embedding(query)
    results = search_embeddings(query_embedding=query_embedding, session=session, limit=5)

    print(f"\nTop 5 results for: '{query}'\n")
    print("-" * 60)
    for result in results:
        print(f"\nID: {result.id} | File: {result.file_name}")
        print(f"Sentence #{result.sentence_number}")
        print(f"Distance: {result.distance:.4f}")
        print(f"Content: {result.content[:200]}...")

    print("\n" + "=" * 60)
    print("Getting surrounding sentences for top result...")
    entry_ids = [r.id for r in results]
    file_names = [r.file_name for r in results]
    surrounding = get_surrounding_sentences(entry_ids, file_names, 2, session)
    for i, group in enumerate(surrounding):
        print(f"\nContext group {i+1}:")
        for s in group:
            print(f"  [{s.sentence_number}] {s.content[:150]}...")
