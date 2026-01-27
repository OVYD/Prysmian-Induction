from modules.data_manager import load_data

def search_content(query):
    """
    Searches for the query string in categories and steps.
    Returns a list of dictionaries with search results.
    """
    if not query or len(query.strip()) < 2:
        return []
    
    query = query.lower()
    data = load_data()
    results = []
    
    categories = data.get("categories_list", {})
    
    for cat_id, cat_name in categories.items():
        cat_content = data.get(cat_id, {})
        description = cat_content.get("description", "")
        steps = cat_content.get("steps", [])
        
        # Search in Category Name and Description
        if query in cat_name.lower() or query in description.lower():
            results.append({
                "type": "Category",
                "title": cat_name,
                "preview": description[:100] + "..." if description else "No description",
                "location": cat_id,
                "score": 10 if query in cat_name.lower() else 5
            })
            
        # Search in Steps
        for idx, step in enumerate(steps):
            title = step.get("title", "")
            text = step.get("text", "")
            
            if (title and query in title.lower()) or (text and query in text.lower()):
                preview_text = text[:100].replace("\n", " ") + "..." if text else "Media Content"
                step_title = title if title else f"Step {idx + 1}"
                
                results.append({
                    "type": "Step",
                    "title": f"{cat_name} > {step_title}",
                    "preview": preview_text,
                    "location": cat_id,
                    "score": 3,
                    "step_index": idx
                })
                
    # Sort by score (relevance)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
