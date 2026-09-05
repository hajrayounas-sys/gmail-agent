from dotenv import load_dotenv
load_dotenv()
from sentence_transformers import SentenceTransformer
import chromadb
from memory import load_contacts
import re

model = SentenceTransformer('all-MiniLM-L6-v2')

# This creates (or opens, if it already exists) a folder on disk
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# A "collection" is like a table in a normal database.
# get_or_create_collection means: if it already exists, reuse it;
# otherwise, make a new empty one.
collection = chroma_client.get_or_create_collection(name="contacts")


def rebuild_contact_index():
    contacts = load_contacts()

    names = list(contacts.keys())
    emails = list(contacts.values())

    # Turn every contact name into a vector, all at once (a "batch").
    embeddings = model.encode(names).tolist()

    # Chroma needs a unique ID string for each entry.
    ids = [f"contact_{i}" for i in range(len(names))]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=names,
        metadatas=[{"email": email} for email in emails]
    )

    print(f"Indexed {len(names)} contacts into Chroma.")

def _nearest_match(text, top_k=1):
    query_embedding = model.encode([text]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    matched_name = results["documents"][0][0]
    matched_email = results["metadatas"][0][0]["email"]
    distance = results["distances"][0][0]

    return {"name": matched_name, "email": matched_email, "distance": distance}


def resolve_contact(query_text, max_distance=1.0):
    result = _nearest_match(query_text)

    if result["distance"] > max_distance:
        return None

    return result


def resolve_contact_from_sentence(sentence, max_distance=1.0):
    words = re.findall(r"[a-zA-Z']+", sentence.lower())

    candidates = set()
    for window_size in (1, 2, 3):
        for i in range(len(words) - window_size + 1):
            phrase = " ".join(words[i:i + window_size])
            candidates.add(phrase)

    best_match = None
    for phrase in candidates:
        result = _nearest_match(phrase)
        if best_match is None or result["distance"] < best_match["distance"]:
            best_match = result

    if best_match is None or best_match["distance"] > max_distance:
        return None

    return best_match

if __name__ == "__main__":
   rebuild_contact_index()
#if __name__ == "__main__":
#    test_queries = [
#        "professor",
#        "my supervisor",
#        "prof",
#        "my friend",
#        "my landlord"
#    ]
#
#    for query in test_queries:
#        result = resolve_contact(query)
#        if result is None:
#            print(f"Query: '{query}' → No confident match found.")
#        else:
#            print(f"Query: '{query}' → Matched: '{result['name']}' ({result['email']}) | distance: {result['distance']:.4f}")