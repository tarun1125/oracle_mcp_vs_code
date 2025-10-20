# In-memory store for session context. Replace with a persistent store for production.
_memory_store = {}

def update_context(session_id: str, last_query: str, params: dict):
    """Updates the context for a given session."""
    if session_id not in _memory_store:
        _memory_store[session_id] = {}
    _memory_store[session_id]["last_query"] = last_query
    _memory_store[session_id]["params"] = params

def get_context(session_id: str) -> dict | None:
    """Retrieves the context for a given session."""
    return _memory_store.get(session_id)
