# def populate_chroma_db():
#     chroma_client = chromadb.HttpClient(host="localhost", port=8000)
#     collection = chroma_client.get_or_create_collection(name="abs")

#     entities = json.load(open("entities.json", "r"))

#     documents = []
#     metadatas = []
#     ids = []

#     for i, item in enumerate(entities):
#         doc_content = f"Entity: {item['entity']}\nDescription: {item['description']}\nKey Relations: {item['key_relations']}\nHistory: {item['history']}"
#         documents.append(doc_content)
#         metadatas.append({"entity": item['entity']})
#         ids.append(f"entity_{i}")

#     collection.add(
#         documents=documents,
#         metadatas=metadatas,
#         ids=ids
#     )
#     print(f"Added {len(documents)} entities to ChromaDB.")