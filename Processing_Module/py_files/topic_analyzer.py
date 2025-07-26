from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class TopicAnalyzer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def extract_topics_and_themes(self, segments, n_topics=5):
        """Extract topics using semantic clustering"""
        if not segments:
            return [], {}
        
        # Extract meaningful text content
        texts = []
        valid_segments = []
        
        for seg in segments:
            if len(seg['text'].strip()) > 10:
                texts.append(seg['text'])
                valid_segments.append(seg)
        
        if len(texts) < n_topics:
            n_topics = max(1, len(texts) // 2)
        
        if not texts:
            return [], {}
        
        # Generate embeddings
        try:
            embeddings = self.model.encode(texts)
        except Exception as e:
            print(f" Warning: Could not generate embeddings: {e}")
            return [], {}
        
        # Cluster similar content
        if len(texts) > 1:
            try:
                kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(embeddings)
            except Exception as e:
                print(f" Warning: Clustering failed: {e}")
                clusters = [0] * len(texts)
        else:
            clusters = [0] * len(texts)
        
        # Extract keywords using TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=100, 
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        try:
            # Check if we have enough diverse text
            unique_texts = list(set(texts))
            if len(unique_texts) < 2:
                # Handle case with insufficient unique text
                topic_keywords = {i: ['general_discussion'] for i in range(n_topics)}
            else:
                tfidf_matrix = vectorizer.fit_transform(texts)
                feature_names = vectorizer.get_feature_names_out()
                
                topic_keywords = {}
                for i in range(n_topics):
                    cluster_indices = [j for j, cluster in enumerate(clusters) if cluster == i]
                    if cluster_indices:
                        cluster_texts = [texts[j] for j in cluster_indices]
                        if cluster_texts:
                            cluster_tfidf = vectorizer.transform(cluster_texts)
                            mean_scores = cluster_tfidf.mean(axis=0).A1
                            
                            # Handle cases where all scores are zero or NaN
                            if np.isnan(mean_scores).all() or (mean_scores == 0).all():
                                topic_keywords[i] = ['miscellaneous']
                            else:
                                top_indices = mean_scores.argsort()[-10:][::-1]
                                topic_keywords[i] = [feature_names[idx] for idx in top_indices if not np.isnan(mean_scores[idx])]
                                if not topic_keywords[i]:
                                    topic_keywords[i] = ['general_topic']
        except Exception as e:
            print(f" Warning: TF-IDF analysis failed: {e}")
            topic_keywords = {i: ['analysis_failed'] for i in range(n_topics)}
        
        return clusters, topic_keywords

    
    def get_semantic_summary(self, text, max_length=200):
        """Generate semantic summary of text"""
        sentences = text.split('.')
        if len(sentences) <= 3:
            return text[:max_length]
        
        # Score sentences by length and keyword presence
        keywords = ['important', 'key', 'main', 'primary', 'crucial', 'significant']
        scored_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                score = len(sentence.split())
                for keyword in keywords:
                    if keyword in sentence.lower():
                        score *= 1.5
                scored_sentences.append((sentence, score))
        
        # Return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        summary_sentences = [sent[0] for sent in scored_sentences[:3]]
        
        summary = '. '.join(summary_sentences)
        return summary[:max_length] + "..." if len(summary) > max_length else summary
