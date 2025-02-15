from sklearn.feature_extraction.text import TfidfVectorizer
import re

def extract_keywords(text, num_keywords=5):
    """Extracts important keywords using TF-IDF."""
    if not text:
        return []

    text = re.sub(r"[^a-zA-Z\s]", "", text).lower()

    vectorizer = TfidfVectorizer(stop_words="english", max_features=100)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()

    keyword_scores = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    
    return [word for word, score in keyword_scores[:num_keywords]]