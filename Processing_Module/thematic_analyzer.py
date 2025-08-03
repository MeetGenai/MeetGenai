"""
thematic_analyzer.py

Purpose:
    This module is designed to uncover the latent topics or themes within a
    body of text, such as a transcript chunk. It employs a sophisticated approach
    using sentence-transformer models to generate semantic vector embeddings for
    text segments. These embeddings are then clustered using K-Means to group
    conversationally related segments. Finally, TF-IDF is used to extract the
    most representative keywords for each identified theme.

Key Features:
    - Leverages `sentence-transformers` for powerful semantic understanding.
    - Uses `scikit-learn` for efficient clustering and feature extraction.
    - Determines a specified number of topics from the text.
    - Extracts meaningful, multi-word keywords for each topic.
    - Handles sparse content gracefully by adjusting the number of topics.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

class ThematicAnalyzer:
    """
    Discovers underlying discussion themes using semantic clustering and TF-IDF.
    """

    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2', seed: int = 42):
        """
        Initializes the analyzer and loads the sentence embedding model.

        Args:
            embedding_model: The name of the SentenceTransformer model to use.
            seed: A random state seed for reproducible clustering results.
        """
        try:
            print(f"...Loading thematic analysis model: {embedding_model}...")
            self.model = SentenceTransformer(embedding_model)
        except Exception as e:
            print(f"  Critical Error: Could not load SentenceTransformer model '{embedding_model}'.")
            print(f"   Please ensure the library is installed (`pip install sentence-transformers`) and you have an internet connection.")
            print(f"   Error: {e}")
            self.model = None
        self.random_state = seed

    def discover_themes(self,
                        segments: List[Dict[str, Any]],
                        num_themes: int = 5) -> Dict[int, List[str]]:
        """
        Extracts dominant themes by clustering segment embeddings.

        Args:
            segments: A list of transcript segment dictionaries.
            num_themes: The target number of themes to identify.

        Returns:
            A dictionary mapping each theme ID to a list of its top keywords.
        """
        if not self.model:
            print("  Thematic analysis model not loaded. Skipping theme discovery.")
            return {}

        # Filter for segments with enough content to be meaningful
        valid_texts = [seg['text'] for seg in segments if len(seg.get('text', '').split()) > 4]

        if not valid_texts:
            return {}

        # Dynamically adjust the number of themes if content is sparse
        if len(valid_texts) < num_themes:
            num_themes = max(1, len(valid_texts))

        try:
            # 1. Generate semantic vector embeddings for each text segment
            embeddings = self.model.encode(valid_texts, show_progress_bar=False)

            # 2. Perform K-Means clustering on the embeddings
            kmeans = KMeans(n_clusters=num_themes, random_state=self.random_state, n_init='auto')
            cluster_labels = kmeans.fit_predict(embeddings)

            # 3. Extract representative keywords for each theme (cluster)
            theme_keywords = self._extract_theme_keywords(valid_texts, cluster_labels, num_themes)
            return theme_keywords

        except Exception as e:
            print(f"  An error occurred during theme discovery: {e}")
            return {}

    def _extract_theme_keywords(self,
                                texts: List[str],
                                labels: np.ndarray,
                                num_themes: int) -> Dict[int, List[str]]:
        """
        Uses TF-IDF to find the most representative words for each cluster.
        """
        theme_keywords = {}
        try:
            # Vectorizer considers single words and two-word phrases, ignoring common stop words.
            vectorizer = TfidfVectorizer(
                max_features=1500,
                stop_words='english',
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = np.array(vectorizer.get_feature_names_out())

            for i in range(num_themes):
                # Find all texts belonging to the current theme cluster
                cluster_indices = np.where(labels == i)[0]
                if len(cluster_indices) == 0:
                    continue

                # Calculate the mean TF-IDF score for each word within the cluster
                cluster_tfidf_scores = tfidf_matrix[cluster_indices].mean(axis=0)
                
                # Get the indices of the top 5 keywords based on score
                top_keyword_indices = np.asarray(cluster_tfidf_scores).flatten().argsort()[-5:][::-1]
                
                theme_keywords[i + 1] = feature_names[top_keyword_indices].tolist()

        except Exception as e:
            print(f"  Could not extract keywords using TF-IDF: {e}")
            return {i + 1: ["keyword extraction failed"] for i in range(num_themes)}
            
        return theme_keywords
