from support_agent.retrieval import (
    create_pinecone_index,
    ingest_handbook,
search_handbook
)

index = create_pinecone_index()
print(search_handbook("Can I get my money back?", index))
print(search_handbook("How long until my package arrives?", index))
print(search_handbook("What if my item arrives broken?", index))
