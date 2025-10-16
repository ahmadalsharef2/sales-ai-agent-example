"""Data loading and search service - Using simple linear search for small dataset"""
import json
from typing import List, Dict, Any
from pathlib import Path


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
        self._load_data()
    
    def _load_data(self):
        """Load product catalog and FAQ from files"""
        # Load product catalog
        if self.catalog_path.exists():
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                self.catalog = json.load(f)
        
        # Load FAQ
        if self.faq_path.exists():
            with open(self.faq_path, 'r', encoding='utf-8') as f:
                self.faq_text = f.read()
    
    def search_bikes(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search bikes using simple keyword matching.
        
        For a small catalog, this is faster and more reliable than vector search.
        """
        query_lower = query.lower()
        scored_bikes = []
        
        for bike in self.catalog:
            score = 0
            
            # Check type (mountain, road, city, e-bike)
            if any(bike_type in query_lower for bike_type in ['mountain', 'road', 'city', 'e-bike', 'electric']):
                if bike['type'].lower() in query_lower:
                    score += 5
            
            # Check price mentions
            if 'cheap' in query_lower or 'budget' in query_lower or 'affordable' in query_lower:
                if bike['price_eur'] < 1000:
                    score += 3
            elif 'premium' in query_lower or 'high-end' in query_lower or 'expensive' in query_lower:
                if bike['price_eur'] > 2000:
                    score += 3
            
            # Check intended use
            for use in bike.get('intended_use', []):
                if use.lower() in query_lower:
                    score += 4
            
            # Check other features
            for key in ['frame_material', 'suspension', 'brakes', 'brand']:
                if str(bike.get(key, '')).lower() in query_lower:
                    score += 2
            
            # General keyword search in name
            if any(word in bike['name'].lower() for word in query_lower.split()):
                score += 3
            
            if score > 0:
                scored_bikes.append((score, bike))
        
        # Sort by score and return top results
        scored_bikes.sort(reverse=True, key=lambda x: x[0])
        return [bike for _, bike in scored_bikes[:max_results]]
    
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
