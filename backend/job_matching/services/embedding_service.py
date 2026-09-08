from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Stateless TF-IDF vectorizer.
# It is fitted on the texts being compared, so it requires no API key,
# model download, Torch, CUDA, or external service.

def get_embedding(text):
    """Convert a single text into a normalized TF-IDF vector."""
    if not isinstance(text, str):
        text = str(text or "")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    return vectorizer.fit_transform([text])


def calculate_similarity(text1, text2):
    """Return cosine similarity between two texts as a float from 0 to 1."""
    text1 = str(text1 or "")
    text2 = str(text2 or "")

    if not text1.strip() or not text2.strip():
        return 0.0

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )

    vectors = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return float(similarity)
