from sklearn.feature_extraction.text import TfidfVectorizer
from stop_words import get_stop_words
from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self, projects):
        self.projects = projects
        # Combinar stop words de português e inglês
        stop_words = get_stop_words('portuguese') + get_stop_words('english')
        self.vectorizer = TfidfVectorizer(stop_words=stop_words)
        self._fit()

    def _project_text(self, p):
        title = ([p["title"]] * 5)
        tags = (p["tags"] * 3)
        return " ".join(title + tags + p["steps"]) 

    def _fit(self):
        corpus = [self._project_text(p) for p in self.projects]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def recommend(self, description, threshold=0.1):
        v = self.vectorizer.transform([description])
        if v.nnz == 0:
            return None

        sims = cosine_similarity(v, self.tfidf_matrix)[0]
        best_idx = int(sims.argmax())
        best_score = float(sims[best_idx])

        if best_score < threshold:
            return None

        project = self.projects[best_idx]
        project["score"] = best_score
        return project

    def list_projects(self):
        return self.projects
