"""
Emerging Theme Discovery Module.
Detects new/emerging themes in patient feedback using embeddings and clustering.
"""

from typing import List, Dict, Tuple
import joblib
import os
from sentence_transformers import SentenceTransformer
import hdbscan
import numpy as np
from datetime import datetime


class ThemeDiscovery:
    """Discover emerging themes in feedback using semantic clustering."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", model_path: str = "models"):
        """
        Initialize the ThemeDiscovery engine.
        
        Args:
            model_name: Name of the SentenceTransformer model
            model_path: Path to save embeddings and cluster data
        """
        self.model_name = model_name
        self.model_path = model_path
        os.makedirs(model_path, exist_ok=True)
        
        # Load the sentence transformer model
        self.transformer = SentenceTransformer(model_name)
        
        self.clusterer = None
        self.embeddings = None
        self.feedback_texts = []
        self.themes = {}
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for feedback texts.
        
        Args:
            texts: List of feedback texts
            
        Returns:
            Array of embeddings (n_samples x embedding_dim)
        """
        embeddings = self.transformer.encode(texts, show_progress_bar=False)
        return embeddings
    
    def discover_themes(
        self,
        texts: List[str],
        min_cluster_size: int = 10,
        min_samples: int = 5,
        threshold: float = 0.5
    ) -> Dict[int, Dict]:
        """
        Discover themes from feedback texts using HDBSCAN clustering.
        
        Args:
            texts: List of feedback texts
            min_cluster_size: Minimum cluster size for HDBSCAN
            min_samples: Minimum samples for HDBSCAN
            threshold: Clustering threshold
            
        Returns:
            Dictionary with theme information
        """
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        self.embeddings = embeddings
        self.feedback_texts = texts
        
        # Perform clustering
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples
        )
        labels = self.clusterer.fit_predict(embeddings)
        
        # Organize results
        themes = {}
        unique_labels = set(labels)
        
        for label in sorted(unique_labels):
            cluster_mask = labels == label
            cluster_texts = [texts[i] for i in range(len(texts)) if cluster_mask[i]]
            cluster_embeddings = embeddings[cluster_mask]
            
            if label == -1:
                theme_name = "Unclustered/Outliers"
            else:
                theme_name = self._generate_theme_label(cluster_texts, label)
            
            themes[label] = {
                "label": label,
                "name": theme_name,
                "size": len(cluster_texts),
                "texts": cluster_texts,
                "centroid": cluster_embeddings.mean(axis=0)
            }
        
        self.themes = themes
        self._save_themes()
        
        return themes
    
    def _generate_theme_label(self, texts: List[str], label_id: int) -> str:
        """
        Generate a descriptive label for a theme cluster.
        
        Args:
            texts: Texts in the cluster
            label_id: Cluster label ID
            
        Returns:
            Theme name/label
        """
        # Extract common keywords from cluster texts
        all_words = []
        for text in texts[:10]:  # Use first 10 texts
            words = text.lower().split()
            all_words.extend([w for w in words if len(w) > 3])
        
        # Count word frequencies
        from collections import Counter
        word_counts = Counter(all_words)
        
        # Get top words
        top_words = [word for word, count in word_counts.most_common(3)]
        
        if top_words:
            theme_name = f"Theme_{label_id}_{'_'.join(top_words[:2])}"
        else:
            theme_name = f"Theme_{label_id}"
        
        return theme_name
    
    def get_theme_summary(self) -> List[Dict]:
        """
        Get summary of discovered themes.
        
        Returns:
            List of theme summaries
        """
        summaries = []
        
        for label, theme_info in self.themes.items():
            summary = {
                "id": label,
                "name": theme_info["name"],
                "size": theme_info["size"],
                "percentage": f"{(theme_info['size'] / sum(t['size'] for t in self.themes.values())) * 100:.1f}%"
            }
            summaries.append(summary)
        
        return sorted(summaries, key=lambda x: x["size"], reverse=True)
    
    def find_emerging_themes(
        self,
        new_texts: List[str],
        existing_themes: List[int],
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Find new/emerging themes by comparing with existing themes.
        
        Args:
            new_texts: New feedback texts to analyze
            existing_themes: List of existing theme labels
            threshold: Similarity threshold for clustering
            
        Returns:
            List of emerging themes
        """
        if not new_texts:
            return []
        
        # Generate embeddings for new texts
        new_embeddings = self.generate_embeddings(new_texts)
        
        emerging_themes = []
        
        # Check similarity to existing themes
        for new_emb, new_text in zip(new_embeddings, new_texts):
            min_similarity = float('-inf')
            closest_theme = None
            
            for label, theme_info in self.themes.items():
                centroid = theme_info["centroid"]
                # Cosine similarity
                similarity = np.dot(new_emb, centroid) / (
                    np.linalg.norm(new_emb) * np.linalg.norm(centroid) + 1e-9
                )
                
                if similarity > min_similarity:
                    min_similarity = similarity
                    closest_theme = label
            
            # If similarity below threshold, it's an emerging theme
            if min_similarity < threshold:
                emerging_themes.append({
                    "text": new_text,
                    "similarity_to_closest": float(min_similarity),
                    "closest_theme": closest_theme,
                    "is_emerging": True,
                    "timestamp": datetime.now().isoformat()
                })
        
        return emerging_themes
    
    def get_similar_feedbacks(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Find similar feedbacks to a query text.
        
        Args:
            query_text: Query feedback text
            top_k: Number of similar feedbacks to return
            
        Returns:
            List of similar feedbacks with similarity scores
        """
        if not self.feedback_texts:
            return []
        
        # Generate embedding for query
        query_embedding = self.generate_embeddings([query_text])[0]
        
        # Calculate similarities
        similarities = []
        for i, text in enumerate(self.feedback_texts):
            # Cosine similarity
            similarity = np.dot(query_embedding, self.embeddings[i]) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(self.embeddings[i]) + 1e-9
            )
            similarities.append((i, text, similarity))
        
        # Sort by similarity and get top k
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        results = []
        for idx, text, similarity in similarities[:top_k]:
            results.append({
                "text": text,
                "similarity": float(similarity),
                "index": idx
            })
        
        return results
    
    def _save_themes(self):
        """Save theme information to disk."""
        # Save themes metadata
        themes_metadata = {}
        for label, theme_info in self.themes.items():
            themes_metadata[str(label)] = {
                "name": theme_info["name"],
                "size": theme_info["size"]
            }
        
        joblib.dump(themes_metadata, os.path.join(self.model_path, "themes_metadata.pkl"))
    
    def save_embeddings(self):
        """Save embeddings to disk."""
        if self.embeddings is not None:
            joblib.dump(self.embeddings, os.path.join(self.model_path, "feedback_embeddings.pkl"))
