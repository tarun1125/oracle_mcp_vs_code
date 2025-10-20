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
