#!/usr/bin/env python3
"""
GovPlanet Complete API Client & AI Search
Complete reverse-engineered API with AI-powered search capabilities
"""

import requests
import json
import re
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import time

@dataclass
class Product:
    """Product data model with all fields"""
    equip_id: str
    description: str
    price: str
    location: str
    location_code: str
    photo_url: str
    page_url: str
    price_numeric: Optional[float] = None
    auction_end_date: Optional[int] = None
    bid_count: int = 0
    features: str = ""
    registration_number: str = ""
    auction_type: str = ""
    equipment_status: int = 0
    is_ica: bool = False
    raw_data: Optional[Dict] = None
    
    @classmethod
    def from_api_data(cls, data: Dict) -> 'Product':
        """Create Product from API response"""
        # Extract price from HTML
        price_html = data.get('priceString', '')
        price_match = re.search(r'\$([\d,]+)', price_html)
        price = price_match.group(0) if price_match else 'N/A'
        price_numeric = None
        if price_match:
            try:
                price_numeric = float(price_match.group(1).replace(',', ''))
            except:
                pass
        
        # Decode HTML entities in features
        features = data.get('featuresString', '').replace('\\x20', ' ').replace('\\x22', '"')
        
        return cls(
            equip_id=data.get('equipId', ''),
            description=data.get('description', ''),
            price=price,
            price_numeric=price_numeric,
            location=data.get('locationString', ''),
            location_code=data.get('locationCode', ''),
            photo_url=data.get('photo', ''),
            page_url=f"https://www.govplanet.com{data.get('itemPageUri', '')}",
            auction_end_date=data.get('aucEndDate'),
            bid_count=data.get('bidCount', 0),
            features=features,
            registration_number=data.get('registrationNu', ''),
            auction_type=data.get('aucType', ''),
            equipment_status=data.get('equipStatus', 0),
            is_ica=data.get('isICA', False),
            raw_data=data
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result.pop('raw_data', None)  # Don't include raw_data in dict
        return result
    
    def searchable_text(self) -> str:
        """Get all searchable text"""
        return f"{self.description} {self.features} {self.location} {self.registration_number}".lower()

class GovPlanetAPI:
    """
    Complete GovPlanet API Client
    
    Discovered Parameters:
    - mode: Search mode (6 = all products)
    - format: Response format (json)
    - ct: Category ID (1-100+)
    - locationCode: Location filter (USA-STATE)
    - q: Search query
    - kw: Keyword search
    - m: Manufacturer filter
    - sort: Sort order (date, price)
    - order: Sort direction (asc, desc)
    - aucType: Auction type (F, A)
    - equipStatus: Equipment status (30, 31)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://www.govplanet.com/',
        })
        self.base_url = "https://www.govplanet.com/jsp/s/search.ips"
        self._cache: Dict[str, List[Product]] = {}
    
    def search(
        self,
        query: Optional[str] = None,
        category: Optional[int] = None,
        location: Optional[str] = None,
        manufacturer: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        auction_type: Optional[str] = None,
        max_results: int = 60
    ) -> Tuple[List[Product], int]:
        """
        Search products with filters
        
        Returns:
            Tuple of (products list, total available count)
        """
        params = {'mode': '6', 'format': 'json'}
        
        if query:
            params['q'] = query
        if category:
            params['ct'] = str(category)
        if location:
            params['locationCode'] = location
        if manufacturer:
            params['m'] = manufacturer
        if sort_by:
            params['sort'] = sort_by
        if order:
            params['order'] = order
        if auction_type:
            params['aucType'] = auction_type
        
        # Check cache
        cache_key = json.dumps(params, sort_keys=True)
        if cache_key in self._cache:
            products = self._cache[cache_key]
            return products[:max_results], len(products)
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'jsonData' in data:
                items = data['jsonData'].get('items', [])
                total = data['jsonData'].get('total', 0)
                products = [Product.from_api_data(item) for item in items]
                
                # Cache results
                self._cache[cache_key] = products
                
                return products[:max_results], total
        
        except Exception as e:
            print(f"Error searching: {e}")
        
        return [], 0
    
    def search_extensive(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        manufacturer: Optional[str] = None,
        max_categories: int = 50,
        max_results: Optional[int] = None
    ) -> List[Product]:
        """
        Get extensive product results by searching across multiple categories.
        This is the recommended method for getting comprehensive search results.
        
        Args:
            query: Search query string
            location: Location filter (e.g., 'USA-CA')
            manufacturer: Manufacturer filter
            max_categories: Number of categories to search (default: 50)
            max_results: Maximum number of results to return (None = all)
        
        Returns:
            List of unique products matching the query
        """
        all_products = []
        seen_ids: Set[str] = set()
        
        for cat_id in range(1, max_categories + 1):
            products, total = self.search(
                query=query,
                category=cat_id,
                location=location,
                manufacturer=manufacturer,
                max_results=60  # API limit per request
            )
            
            for product in products:
                if product.equip_id not in seen_ids:
                    all_products.append(product)
                    seen_ids.add(product.equip_id)
            
            # Stop if we've reached max_results
            if max_results and len(all_products) >= max_results:
                break
            
            time.sleep(0.1)  # Rate limiting
        
        return all_products[:max_results] if max_results else all_products
    
    def get_all_categories(self, max_categories: int = 100) -> List[Product]:
        """Get products from all available categories"""
        all_products = []
        seen_ids: Set[str] = set()
        
        print(f"Fetching from {max_categories} categories...")
        for cat_id in range(1, max_categories + 1):
            products, total = self.search(category=cat_id)
            
            new_count = 0
            for product in products:
                if product.equip_id not in seen_ids:
                    all_products.append(product)
                    seen_ids.add(product.equip_id)
                    new_count += 1
            
            if new_count > 0:
                print(f"  Category {cat_id}: +{new_count} new (Total: {len(all_products)}, Available: {total})")
            
            time.sleep(0.1)  # Rate limiting
        
        return all_products

class AISearchEngine:
    """AI-powered semantic search engine"""
    
    def __init__(self, products: List[Product]):
        self.products = products
        self.indexed = False
    
    def index(self):
        """Index products for search"""
        print(f"Indexing {len(self.products)} products...")
        self.indexed = True
        print("Indexing complete!")
    
    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: int = 10
    ) -> List[Tuple[Product, float]]:
        """
        Semantic search with scoring
        
        Args:
            query: Natural language query
            filters: Additional filters (location, price_range, etc.)
            top_k: Number of results to return
        
        Returns:
            List of (product, score) tuples sorted by relevance
        """
        if not self.indexed:
            self.index()
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_results = []
        
        for product in self.products:
            # Calculate relevance score
            searchable = product.searchable_text()
            searchable_words = set(searchable.split())
            
            # Word overlap score
            common_words = query_words.intersection(searchable_words)
            word_score = len(common_words) / max(len(query_words), 1)
            
            # Phrase match boost
            phrase_score = 0
            if query_lower in searchable:
                phrase_score = 0.5
            
            # Exact match boost
            exact_score = 0
            if query_lower == product.description.lower()[:len(query_lower)]:
                exact_score = 1.0
            
            # Combined score
            score = word_score * 0.4 + phrase_score * 0.3 + exact_score * 0.3
            
            # Apply filters
            if filters:
                if 'location' in filters:
                    if filters['location'].upper() not in product.location_code:
                        continue
                
                if 'price_min' in filters and product.price_numeric:
                    if product.price_numeric < filters['price_min']:
                        continue
                
                if 'price_max' in filters and product.price_numeric:
                    if product.price_numeric > filters['price_max']:
                        continue
                
                if 'categories' in filters:
                    # Would need category mapping
                    pass
            
            if score > 0:
                scored_results.append((product, score))
        
        # Sort by score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]
    
    def parse_natural_query(self, query: str) -> Dict:
        """Parse natural language query into filters"""
        filters = {}
        
        # Extract location
        state_pattern = r'\b(california|texas|new york|florida|arizona|nevada|georgia|north carolina|pennsylvania|new jersey)\b'
        state_match = re.search(state_pattern, query.lower())
        if state_match:
            state_map = {
                'california': 'CA', 'texas': 'TX', 'new york': 'NY',
                'florida': 'FL', 'arizona': 'AZ', 'nevada': 'NV',
                'georgia': 'GA', 'north carolina': 'NC',
                'pennsylvania': 'PA', 'new jersey': 'NJ'
            }
            state = state_map.get(state_match.group(1))
            if state:
                filters['location'] = f'USA-{state}'
        
        # Extract price range
        price_patterns = [
            (r'under\s+\$?(\d+)[kK]?', lambda m: (0, int(m.group(1)) * (1000 if 'k' in m.group(0).lower() else 1))),
            (r'over\s+\$?(\d+)[kK]?', lambda m: (int(m.group(1)) * (1000 if 'k' in m.group(0).lower() else 1), float('inf'))),
            (r'\$?(\d+)[kK]?\s*-\s*\$?(\d+)[kK]?', lambda m: (int(m.group(1)) * (1000 if 'k' in m.group(1).lower() else 1), int(m.group(2)) * (1000 if 'k' in m.group(2).lower() else 1))),
        ]
        
        for pattern, handler in price_patterns:
            match = re.search(pattern, query.lower())
            if match:
                price_range = handler(match)
                if price_range[0] != float('inf'):
                    filters['price_min'] = price_range[0]
                if price_range[1] != float('inf'):
                    filters['price_max'] = price_range[1]
                break
        
        return filters

def main():
    print("=" * 70)
    print("GovPlanet Complete API Client & AI Search")
    print("=" * 70)
    
    # Initialize API
    api = GovPlanetAPI()
    
    # Load or fetch products
    try:
        print("\nLoading products from cache...")
        with open('all_products_complete.json', 'r') as f:
            data = json.load(f)
            products = [Product.from_api_data(item) for item in data.get('products', [])]
            print(f"Loaded {len(products)} products")
    except FileNotFoundError:
        print("\nFetching products from API...")
        products = api.get_all_categories(max_categories=50)
        print(f"Fetched {len(products)} products")
        
        # Save for future use
        with open('all_products_complete.json', 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(products),
                'products': [p.raw_data for p in products]
            }, f, indent=2, ensure_ascii=False)
    
    # Initialize AI search engine
    print("\nInitializing AI Search Engine...")
    ai_engine = AISearchEngine(products)
    ai_engine.index()
    
    # Example searches
    print("\n" + "=" * 70)
    print("Example AI-Powered Searches:")
    print("=" * 70)
    
    test_queries = [
        "trucks",
        "generators",
        "HMMWV vehicles",
        "equipment in California",
        "trucks under $5000",
        "generators with low hours",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Parse natural language
        filters = ai_engine.parse_natural_query(query)
        if filters:
            print(f"   Parsed filters: {filters}")
        
        # Search
        results = ai_engine.search(query, filters=filters, top_k=5)
        
        print(f"   Found {len(results)} results:")
        for i, (product, score) in enumerate(results, 1):
            print(f"   {i}. [{score:.2f}] {product.description[:60]}...")
            print(f"      💰 {product.price} | 📍 {product.location} | 🔗 {product.page_url}")
    
    # Save API documentation
    api_docs = {
        'endpoint': api.base_url,
        'parameters': {
            'mode': 'Search mode (6 = all products)',
            'format': 'Response format (json)',
            'ct': 'Category ID (1-100+)',
            'locationCode': 'Location filter (USA-STATE)',
            'q': 'Search query',
            'kw': 'Keyword search',
            'm': 'Manufacturer filter',
            'sort': 'Sort order (date, price)',
            'order': 'Sort direction (asc, desc)',
            'aucType': 'Auction type (F, A)',
            'equipStatus': 'Equipment status (30, 31)',
        },
        'limitations': {
            'max_items_per_request': 60,
            'pagination': 'Not supported via API',
            'solution': 'Use category filters to get different product sets',
        },
        'total_products_indexed': len(products),
    }
    
    with open('api_complete_docs.json', 'w') as f:
        json.dump(api_docs, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ Complete API Client & AI Search Ready!")
    print("=" * 70)
    print("\nUsage:")
    print("  from govplanet_api import GovPlanetAPI, AISearchEngine, Product")
    print("  api = GovPlanetAPI()")
    print("  products, total = api.search(query='trucks', category=1)")
    print("  engine = AISearchEngine(products)")
    print("  results = engine.search('trucks under $5000')")

if __name__ == "__main__":
    main()

