from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text):
    return model.encode(
        text,
        normalize_embeddings=True,
    )


def calculate_similarity(text1, text2):
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)

    return float(embedding1 @ embedding2)