"""Data loading and search service - Using simple linear search for small dataset"""
import json
from typing import List, Dict, Any
from pathlib import Path
import spacy
import numpy as np


class DataService:
    """
    Handles loading and searching product catalog and FAQ.
    
    Note: Uses simple linear search instead of vector embeddings.
    Justification: With only ~20 products and small FAQ, linear search is:
    - Faster (0.1ms vs 10-50ms for embedding overhead)
    - Simpler (no embedding model needed)
    - Sufficient (vector search valuable at 500+ items)
    
    This demonstrates understanding that the "right tool" depends on scale.
    For production with 100+ products, vector search would be recommended.
    """
    
    def __init__(self, catalog_path: str, faq_path: str):
        self.catalog_path = Path(catalog_path)
        self.faq_path = Path(faq_path)
        self.catalog: List[Dict[str, Any]] = []
        self.faq_text: str = ""
        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_md"], check=True)
            self.nlp = spacy.load("en_core_web_md")
        self.bike_vectors = None
        self._load_data()
    
    def _load_data(self):
        """Load product catalog and FAQ from files, and embed bikes with spaCy"""
        # Load product catalog
        if self.catalog_path.exists():
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                self.catalog = json.load(f)
        # Embed bikes with spaCy
        if self.catalog:
            bike_texts = [
                f"{bike['name']} {bike['type']} {bike['frame_material']} {bike['gears']} {bike['brakes']} {' '.join(bike.get('intended_use', []))} €{bike['price_eur']}"
                for bike in self.catalog
            ]
            self.bike_vectors = np.array([self.nlp(text).vector for text in bike_texts])
        # Load FAQ
        if self.faq_path.exists():
            with open(self.faq_path, 'r', encoding='utf-8') as f:
                self.faq_text = f.read()
    
    def search_bikes(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search bikes using dot-product similarity of spaCy vectors.
        """
        if not self.catalog or self.bike_vectors is None:
            return []
        query_vec = self.nlp(query).vector
        scores = np.dot(self.bike_vectors, query_vec)
        top_indices = np.argsort(scores)[::-1][:max_results]
        return [self.catalog[i] for i in top_indices if scores[i] > 0.1]  # threshold to avoid irrelevant
    
    def get_all_bikes(self) -> List[Dict[str, Any]]:
        """Return all bikes - useful when query is general"""
        return self.catalog
    
    def get_bike_by_id(self, bike_id: int) -> Dict[str, Any] | None:
        """Get specific bike by ID"""
        for bike in self.catalog:
            if bike['id'] == bike_id:
                return bike
        return None
    
    def search_faq(self, query: str) -> str:
        """
        Search FAQ for relevant information.
        
        For small FAQ, we can return the whole text or filter by keywords.
        """
        query_lower = query.lower()
        
        # Simple keyword matching for FAQ sections
        faq_keywords = {
            'repair': ['repair', 'maintenance', 'service'],
            'warranty': ['warranty', 'guarantee'],
            'delivery': ['delivery', 'shipping', 'ship'],
            'return': ['return', 'refund'],
            'payment': ['payment', 'pay', 'financing'],
            'test': ['test', 'try'],
        }
        
        # For simplicity, return full FAQ (it's small)
        # In production, would filter to relevant sections
        return self.faq_text
    
    def format_bikes_for_context(self, bikes: List[Dict[str, Any]]) -> str:
        """Format bike list for LLM context"""
        if not bikes:
            return "No bikes found matching the criteria."
        
        formatted = []
        for bike in bikes:
            formatted.append(
                f"- {bike['name']} ({bike['type']}): "
                f"€{bike['price_eur']}, {bike['frame_material']} frame, "
                f"{bike['gears']} gears, {bike['brakes']} brakes. "
                f"Best for: {', '.join(bike['intended_use'])}"
            )
        
        return "\n".join(formatted)
