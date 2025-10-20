from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.query_executor import execute_query
from app.intent_matcher import match_intent
from app.memory_manager import update_context
from app.logger import setup_logger

app = FastAPI(title="SQL Intent Executor")
logger = setup_logger()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "details": str(exc)}
    )

@app.post("/query")
async def handle_query(payload: dict):
    user_query = payload.get("query_text")
    user_env = payload.get("env", "DEV")
    user_id = payload.get("user_id", "default")

    query_name = match_intent(user_query)
    if not query_name:
        raise HTTPException(status_code=400, detail="No matching query found.")

    # Example parameter extraction (can be replaced with LLM parsing)
    params = {"year": 2023} if "2023" in user_query else {}

    results = execute_query(user_env, query_name, params)
    update_context(user_id, query_name, params)

    return {
        "env": user_env,
        "matched_query": query_name,
        "params": params,
        "records": len(results),
        "results": results
    }
