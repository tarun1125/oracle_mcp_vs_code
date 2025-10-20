import json
# In a real implementation, you'd use spaCy or another NLP library here.
# For this scaffold, we'll do a simple keyword match.

def match_intent(query_text: str) -> str | None:
    """Matches user query text to a predefined query name."""
    with open("app/queries/queries.json") as f:
        queries = json.load(f)

    query_text_lower = query_text.lower()

    for name, details in queries.items():
        # Simple keyword matching
        if all(keyword in query_text_lower for keyword in details.get("keywords", [])):
            return name

    return None
