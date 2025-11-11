# GovPlanet API - Complete Integration Guide

A complete reverse-engineered API client for GovPlanet with extensive product search capabilities. This guide is designed for frontend developers to integrate comprehensive product search functionality.

## 🎯 Overview

This API client provides access to GovPlanet's product catalog with the ability to search across **1,000+ products** by querying multiple categories simultaneously. 

**Current Capabilities:**
- Single request: **60 products** (API limit per request)
- Extensive search: **100+ products** by searching across multiple categories
- Maximum potential: **1,420+ unique products** when searching all categories

The API returns up to 60 products per request, but by searching across categories, you can get extensive results including exactly 100 products for any query.

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Get Exactly 100 Results ⭐ (Most Common Use Case)

```python
from govplanet_api import GovPlanetAPI

api = GovPlanetAPI()

# Get exactly 100 results for any query
products = api.search_extensive(
    query='truck',           # Your search query
    max_categories=20,       # Search 20 categories (enough for 100 results)
    max_results=100          # Return exactly 100 products
)

print(f"Found {len(products)} products")
```

**Why This Works:**
- Each category can return up to 60 products
- Searching 20 categories gives us up to 1,200 potential products
- The method automatically deduplicates products
- Setting `max_results=100` returns exactly 100 unique products

**Performance:** ~2-3 seconds for 100 results (20 categories × 0.1s delay)

### Basic Search (Single Request)

```python
from govplanet_api import GovPlanetAPI

api = GovPlanetAPI()

# Simple search - returns up to 60 products
products, total = api.search(query='trucks')
print(f"Found {len(products)} products (Total available: {total})")
```

### Extensive Search (100+ Results)

```python
from govplanet_api import GovPlanetAPI

api = GovPlanetAPI()

# Search across multiple categories for comprehensive results
products = api.search_extensive(
    query='trucks',
    max_categories=50,  # Search 50 categories
    max_results=500     # Return up to 500 products
)

print(f"Found {len(products)} unique products")
```

## 📚 API Reference

### `GovPlanetAPI` Class

#### `search()` - Single Request Search

Search products with filters. Returns up to 60 products per request.

```python
products, total = api.search(
    query='trucks',              # Search query (optional)
    category=1,                  # Category ID 1-100+ (optional)
    location='USA-CA',           # Location filter (optional)
    manufacturer='AM General',   # Manufacturer filter (optional)
    sort_by='price',             # Sort: 'date' or 'price' (optional)
    order='asc',                 # Order: 'asc' or 'desc' (optional)
    auction_type='F',            # Auction type: 'F' or 'A' (optional)
    max_results=60               # Max results (default: 60)
)
```

**Returns:** `Tuple[List[Product], int]` - (products list, total available count)

#### `search_extensive()` - Multi-Category Search ⭐ RECOMMENDED

Search across multiple categories to get comprehensive results. This is the **recommended method** for getting extensive product results.

```python
products = api.search_extensive(
    query='trucks',              # Search query (optional)
    location='USA-CA',           # Location filter (optional)
    manufacturer='AM General',   # Manufacturer filter (optional)
    max_categories=50,           # Number of categories to search (default: 50)
    max_results=500              # Maximum results to return (None = all)
)
```

**Returns:** `List[Product]` - List of unique products

**Why use this?**
- Searches across multiple categories automatically
- Returns hundreds or thousands of unique products
- Handles deduplication automatically
- Best for comprehensive search results

### `Product` Data Model

Each product contains:

```python
{
    'equip_id': str,              # Unique product ID
    'description': str,            # Product description
    'price': str,                 # Formatted price (e.g., "$1,500")
    'price_numeric': float,       # Numeric price for filtering
    'location': str,              # Location name (e.g., "California")
    'location_code': str,         # Location code (e.g., "USA-CA")
    'photo_url': str,             # Product image URL
    'page_url': str,              # Full product page URL
    'auction_end_date': int,      # Auction end timestamp
    'bid_count': int,             # Number of bids
    'features': str,              # Product features
    'registration_number': str,   # Registration number
    'auction_type': str,          # Auction type
    'equipment_status': int,      # Equipment status code
    'is_ica': bool                # ICA flag
}
```

### `AISearchEngine` Class

Semantic search engine for natural language queries.

```python
from govplanet_api import AISearchEngine

# Initialize with products
engine = AISearchEngine(products)
engine.index()

# Search with natural language
results = engine.search(
    query='trucks under $5000 in California',
    filters={'price_max': 5000, 'location': 'USA-CA'},
    top_k=10
)

# Results are scored by relevance
for product, score in results:
    print(f"[{score:.2f}] {product.description} - {product.price}")
```

## 💡 Usage Examples

### Example 1: Get Exactly 100 Results for a Query ⭐

```python
from govplanet_api import GovPlanetAPI

api = GovPlanetAPI()

# Get exactly 100 products matching "truck"
products = api.search_extensive(
    query='truck',
    max_categories=20,  # Search 20 categories
    max_results=100     # Return exactly 100 products
)

print(f"Found {len(products)} products")
for product in products[:10]:
    print(f"- {product.description} - {product.price} - {product.location}")
```

**Quick Examples:**
```python
# Get 100 trucks
trucks = api.search_extensive(query='truck', max_categories=20, max_results=100)

# Get 100 generators
generators = api.search_extensive(query='generator', max_categories=20, max_results=100)

# Get 100 products in California
products = api.search_extensive(location='USA-CA', max_categories=30, max_results=100)
```

**Key Points:**
- `max_categories=20` ensures enough categories are searched to get 100 results
- `max_results=100` limits the return to exactly 100 products
- Each category can return up to 60 products, so 2-3 categories is usually enough for 100 results
- **Performance**: ~2-3 seconds for 100 results

### Example 2: Search for Trucks

```python
from govplanet_api import GovPlanetAPI

api = GovPlanetAPI()

# Get extensive results
trucks = api.search_extensive(
    query='truck',
    max_categories=50,
    max_results=200
)

print(f"Found {len(trucks)} trucks")
for truck in trucks[:10]:
    print(f"- {truck.description} - {truck.price} - {truck.location}")
```

### Example 3: Search by Location

```python
# Get all products in California
california_products = api.search_extensive(
    location='USA-CA',
    max_categories=50
)

print(f"Found {len(california_products)} products in California")
```

### Example 4: Search with Multiple Filters

```python
# Search for generators in Texas
generators = api.search_extensive(
    query='generator',
    location='USA-TX',
    max_categories=30,
    max_results=100
)

# Filter by price (client-side)
affordable = [g for g in generators if g.price_numeric and g.price_numeric < 5000]
print(f"Found {len(affordable)} generators under $5000")
```

### Example 5: Natural Language Search

```python
from govplanet_api import GovPlanetAPI, AISearchEngine

api = GovPlanetAPI()

# Get products
products = api.search_extensive(query='vehicle', max_categories=30)

# Initialize AI search
engine = AISearchEngine(products)
engine.index()

# Natural language queries
queries = [
    "HMMWV vehicles",
    "trucks under $5000",
    "generators in California",
    "equipment with low hours"
]

for query in queries:
    results = engine.search(query, top_k=5)
    print(f"\nQuery: '{query}'")
    for product, score in results:
        print(f"  [{score:.2f}] {product.description[:50]}... - {product.price}")
```

## 🔍 API Parameters Reference

### Endpoint
```
https://www.govplanet.com/jsp/s/search.ips
```

### Available Parameters

| Parameter | Type | Description | Example Values |
|-----------|------|-------------|----------------|
| `mode` | int | Search mode | `6` (all products) |
| `format` | string | Response format | `json` |
| `q` | string | Search query | `"truck"`, `"generator"` |
| `ct` | int | Category ID | `1`, `2`, `3`... (1-100+) |
| `locationCode` | string | Location filter | `"USA-CA"`, `"USA-TX"` |
| `m` | string | Manufacturer | `"AM General"` |
| `sort` | string | Sort field | `"date"`, `"price"` |
| `order` | string | Sort direction | `"asc"`, `"desc"` |
| `aucType` | string | Auction type | `"F"`, `"A"` |
| `equipStatus` | int | Equipment status | `30`, `31` |

### Location Codes

Use `USA-{STATE}` format:
- `USA-CA` - California
- `USA-TX` - Texas
- `USA-NY` - New York
- `USA-FL` - Florida
- `USA-AZ` - Arizona
- ... (all US states)

## 📊 Response Structure

### API Response Format

```json
{
  "jsonData": {
    "total": 22487,
    "items": [
      {
        "equipId": "14224716",
        "description": "Product description",
        "priceString": "<span>US $1,490</span>",
        "locationString": "Arizona",
        "locationCode": "USA-AZ",
        "photo": "https://cdn.ironpla.net/...",
        "itemPageUri": "/for-sale/...",
        "featuresString": "Feature details...",
        "aucEndDate": 1762891200000,
        "bidCount": 3,
        ...
      }
    ]
  }
}
```

## ⚠️ Important Limitations

1. **Max 60 items per request** - The API returns a maximum of 60 products per single request
2. **No pagination** - Standard pagination parameters (`start`, `offset`, `page`) don't work
3. **Solution** - Use `search_extensive()` which searches across multiple categories to get comprehensive results

## 🎯 Best Practices

### For Getting 100 Results

```python
# ✅ RECOMMENDED: Get exactly 100 results
products = api.search_extensive(
    query='your query',
    max_categories=20,  # 20 categories is enough for 100 results
    max_results=100     # Return exactly 100 products
)
```

### For Extensive Results (100+)

```python
# ✅ For 500+ results, search more categories
products = api.search_extensive(
    query='your query',
    max_categories=50,  # Search many categories
    max_results=500     # Set reasonable limit
)
```

### For Quick Single Requests

```python
# ✅ Use search() for quick single requests
products, total = api.search(query='trucks', category=1)
```

### For Natural Language Queries

```python
# ✅ Use AISearchEngine for semantic search
engine = AISearchEngine(products)
results = engine.search('trucks under $5000')
```

## 🔧 Frontend Integration Examples

### JavaScript/TypeScript Example

```javascript
// Backend API endpoint (using Python Flask/FastAPI)
// POST /api/search
// {
//   "query": "trucks",
//   "location": "USA-CA",
//   "max_categories": 50,
//   "max_results": 200
// }

// Frontend fetch
async function searchProducts(query, location = null) {
  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      location: location,
      max_categories: 50,
      max_results: 200
    })
  });
  
  const products = await response.json();
  return products;
}

// Usage
const trucks = await searchProducts('trucks', 'USA-CA');
console.log(`Found ${trucks.length} trucks`);
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function ProductSearch() {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    const results = await searchProducts(query);
    setProducts(results);
    setLoading(false);
  };

  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search products..."
      />
      <button onClick={handleSearch}>Search</button>
      
      {loading && <p>Loading...</p>}
      {products.map(product => (
        <div key={product.equip_id}>
          <h3>{product.description}</h3>
          <p>{product.price} - {product.location}</p>
          <img src={product.photo_url} alt={product.description} />
        </div>
      ))}
    </div>
  );
}
```

## 📈 Performance Tips

1. **Use caching** - The API client includes built-in caching
2. **Limit categories** - Start with `max_categories=30` and increase if needed
3. **Set max_results** - Use reasonable limits to avoid memory issues
4. **Rate limiting** - The client includes automatic rate limiting (0.1s between requests)

## 🐛 Error Handling

```python
try:
    products = api.search_extensive(query='trucks')
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

## 📝 Notes

- **Rate Limiting**: The API includes automatic delays between requests (0.1s)
- **Caching**: Results are cached to avoid duplicate requests
- **Deduplication**: `search_extensive()` automatically removes duplicate products
- **Data Format**: Price is extracted from HTML automatically

## 🔗 Additional Resources

- Product data includes full URLs: `product.page_url` for direct links
- Images available: `product.photo_url` for product images
- Raw data: `product.raw_data` contains full API response

## 📄 License

This is a reverse engineering project for educational purposes. Use responsibly and in compliance with GovPlanet's terms of service.

## 📦 Publishing to PyPI

### Quick Publish Steps

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Build the package:**
   ```bash
   python -m build
   ```

3. **Upload to PyPI:**
   ```bash
   # Test first on TestPyPI (recommended)
   python -m twine upload --repository testpypi dist/*
   
   # Then upload to real PyPI
   python -m twine upload dist/*
   ```

### Before Publishing

- Create PyPI account: https://pypi.org/account/register/
- Get API token: https://pypi.org/manage/account/token/
- When prompted, use:
  - Username: `__token__`
  - Password: `pypi-your-api-token-here`

### After Publishing

Users can install with:
```bash
pip install govplanet-api
```

---

**Note:** This is a reverse engineering project for educational purposes. Use responsibly and in compliance with GovPlanet's terms of service.
# government-surplus-api-client
