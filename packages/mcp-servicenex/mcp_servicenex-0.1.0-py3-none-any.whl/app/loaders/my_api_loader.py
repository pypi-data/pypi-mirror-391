import requests
from app.config import MY_API_BASE_URL, MY_API_KEY

def fetch_tickets(category="all", page=1, limit=10):
    """
    Fetch support tickets from the ServiceNex API with pagination support
    Uses MY_API_KEY from environment (set by Claude Desktop config per-user)
    """
    if not MY_API_KEY:
        raise ValueError("API key not configured. Please set MY_API_KEY in Claude Desktop config.")
    
    headers = {
        "x-api-key": MY_API_KEY,
        "Accept": "application/json"
    }
    
    params = {
        "category": category,
        "page": page,
        "limit": limit
    }
    
    url = f"{MY_API_BASE_URL}/tickets"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def fetch_articles(category="all", page=1, limit=10):
    """
    Fetch articles from the knowledge base API with pagination and filtering
    Uses MY_API_KEY from environment (set by Claude Desktop config per-user)
    """
    if not MY_API_KEY:
        raise ValueError("API key not configured. Please set MY_API_KEY in Claude Desktop config.")
    
    headers = {
        "x-api-key": MY_API_KEY,
        "Accept": "application/json"
    }
    
    params = {
        "category": category,
        "page": page,
        "limit": limit
    }
    
    url = f"{MY_API_BASE_URL}/knowledge/published"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Keep fetch_data as an alias for backward compatibility
def fetch_data(category="all", page=1, limit=10):
    """Deprecated: Use fetch_tickets() instead"""
    return fetch_tickets(category=category, page=page, limit=limit)
