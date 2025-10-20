🧠 SQL Intent Query Executor — MCP Tool (Enhanced)
⚙️ Overview

This project provides a modular, multi-environment SQL Intent Executor built for VS Code Copilot Agent Mode via MCP protocol.

Users ask:

“Get me employee hires in 2023 from UAT database.”

The system automatically:

Maps it to a stored parameterized SQL template.

Extracts parameters (like year=2023, env=UAT).

Connects to the right Oracle environment.

Executes safely and returns structured results.

Logs everything for audit & debugging.

🧩 Updated Architecture
graph TD
    A[User Query] --> B[Copilot Agent / Gemini CLI]
    B --> C[FastMCP Server]
    C -->|Intent Match| D[intent_matcher.py]
    C -->|Context Memory| E[memory_manager.py]
    C -->|Env-Aware Execution| F[query_executor.py]
    F -->|Log & Error Handling| G[logger.py]
    G --> H[Oracle DBs: Dev / Test / UAT / Prod]

⚙️ Folder Structure
sql-intent-executor/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI + global exception handling
│   ├── mcp_server.py          # MCP adapter for VS Code agent
│   ├── query_executor.py      # Env-aware Oracle execution
│   ├── intent_matcher.py      # NLP + keyword similarity
│   ├── memory_manager.py      # Session context
│   ├── logger.py              # Structured logging
│   ├── config.py              # Env-based config loader
│   ├── models.py              # Pydantic schemas
│   ├── utils.py               # Helpers for parsing, formatting
│   └── queries/
│       └── queries.json       # Stored SQL templates
│
├── requirements.txt
├── .env.dev
├── .env.test
├── .env.uat
├── .env.prod
└── README.md

🧰 Environment Configuration

You’ll maintain a .env file for each environment.

Example: .env.dev

ENV_NAME=DEV
ORACLE_USER=dev_user
ORACLE_PASS=dev_password
ORACLE_DSN=localhost:1521/DEVDB
LOG_LEVEL=DEBUG


Example: .env.prod

ENV_NAME=PROD
ORACLE_USER=prod_user
ORACLE_PASS=prod_password
ORACLE_DSN=prodhost:1521/PRODDB
LOG_LEVEL=INFO

🧩 config.py

Handles dynamic environment selection.

import os
from dotenv import load_dotenv

def load_env(env_name: str):
    env_file = f".env.{env_name.lower()}"
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Environment file not found: {env_file}")
    load_dotenv(env_file)
    return {
        "ENV_NAME": os.getenv("ENV_NAME"),
        "ORACLE_USER": os.getenv("ORACLE_USER"),
        "ORACLE_PASS": os.getenv("ORACLE_PASS"),
        "ORACLE_DSN": os.getenv("ORACLE_DSN"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }

🧩 logger.py

Structured logging (works on Windows too).

import logging
import os

def setup_logger(env: str = "DEV"):
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{env.lower()}.log")

    logging.basicConfig(
        level=logging.DEBUG if env.upper() != "PROD" else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("sql_intent_executor")

🧩 query_executor.py

Environment-aware query execution with logging & error handling.

import oracledb, json
from app.logger import setup_logger
from app.config import load_env

def execute_query(env_name, query_name, params):
    env_config = load_env(env_name)
    logger = setup_logger(env_name)

    try:
        with open("app/queries/queries.json") as f:
            queries = json.load(f)
        if query_name not in queries:
            raise ValueError(f"Query '{query_name}' not found.")

        sql = queries[query_name]["sql"]
        logger.info(f"[{env_name}] Executing query: {query_name} with params: {params}")

        conn = oracledb.connect(
            user=env_config["ORACLE_USER"],
            password=env_config["ORACLE_PASS"],
            dsn=env_config["ORACLE_DSN"]
        )
        cursor = conn.cursor()
        cursor.execute(sql, params)
        cols = [col[0] for col in cursor.description]
        data = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        logger.info(f"[{env_name}] Query successful: {len(data)} records fetched")
        return data

    except oracledb.DatabaseError as e:
        logger.error(f"[{env_name}] Oracle error: {e}")
        raise
    except Exception as e:
        logger.error(f"[{env_name}] Unexpected error: {e}")
        raise

🧩 main.py

FastAPI app with centralized exception handling.

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

🧩 mcp_server.py

Serves as the MCP adapter for VS Code Copilot agent mode.

from fastmcp import FastMCP

server = FastMCP(
    name="sql-intent",
    description="Intent-based SQL executor for Oracle",
)

@server.tool()
def sql_intent(query_text: str, env: str = "DEV") -> dict:
    """Executes a stored SQL template based on natural language query and environment."""
    from app.main import handle_query
    payload = {"query_text": query_text, "env": env}
    response = handle_query(payload)
    return response

🧭 Logging Behavior

All logs go to logs/{env}.log

Console shows high-level progress.

Database and system errors captured in detail.

Works perfectly in Windows (UTF-8 safe file handlers).

🧩 Example Query Flow

User query:

“Get me sales in the North region from UAT”

Processing:

spaCy maps intent → sales_in_region

Parameters extracted → { "region": "North" }

Env detected → UAT

Query runs via .env.uat

Logs to logs/uat.log

Response:

{
  "env": "UAT",
  "matched_query": "sales_in_region",
  "params": {"region": "North"},
  "records": 15,
  "results": [ ... ]
}

🧠 Error Handling Matrix
Error Type	Description	Response	Logged
oracledb.DatabaseError	Oracle connectivity / SQL issue	500 with DB error	✅
FileNotFoundError	Missing env file	500	✅
ValueError	Query name not found	400	✅
Other Exception	Unexpected runtime error	500	✅
🧩 Next Upgrade Ideas
Enhancement	Description
🧩 Environment inference	NLP model auto-detects “from dev / test / prod” in query
🧰 Log rotation	Use TimedRotatingFileHandler for daily logs
🧠 Parameter extraction	Integrate Gemini via agent mode for smarter param parsing
🗃️ Persistent memory	Replace in-memory context with SQLite
🧾 Audit trail	Store each query request + response metadata