from app.loaders.my_api_loader import fetch_tickets, fetch_articles

def handle_model_request():
    try:
        results = fetch_tickets(category="all", page=1, limit=10)
        # Format response for AI model
        if isinstance(results, dict) and "tickets" in results:
            tickets = results["tickets"]
        else:
            tickets = results
        
        summary = f"Found {len(tickets)} recent tickets:\n\n" + "\n".join(
            [f"- {ticket.get('subject', 'No Subject')} ({ticket.get('ticketNumber', 'N/A')})" for ticket in tickets[:5]]
        )

        return {"response": summary}
    except Exception as e:
        return {"error": str(e)}

def handle_articles_request():
    """Handle requests for knowledge base articles"""
    try:
        results = fetch_articles(category="all", page=1, limit=10)
        # Format response for AI model based on articles structure
        if isinstance(results, dict) and "articles" in results:
            articles = results["articles"]
            total = results.get("total", len(articles))
            current_page = results.get("currentPage", 1)
            total_pages = results.get("totalPages", 1)
            
            # Create a formatted summary of articles
            articles_summary = f"Found {total} articles (Page {current_page} of {total_pages}):\n\n"
            
            for article in articles[:5]:  # Show first 5 articles
                title = article.get('title', 'Untitled')
                category = article.get('categoryName', 'Uncategorized')
                author = article.get('authorName', 'Unknown Author')
                status = article.get('status', 'Unknown')
                
                articles_summary += f"📄 {title}\n"
                articles_summary += f"   Category: {category}\n"
                articles_summary += f"   Author: {author}\n"
                articles_summary += f"   Status: {status}\n\n"
            
            if len(articles) > 5:
                articles_summary += f"... and {len(articles) - 5} more articles"
            
            return {"response": articles_summary}
        else:
            return {"error": "Invalid articles response format"}
            
    except Exception as e:
        return {"error": str(e)}
