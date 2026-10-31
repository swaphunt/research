"""Database connections via environment variables. No credentials in the code.

RESEARCH_DB_URL points to the research database (the stack in collectors/) as a libpq URL,
postgresql://<user>:<password>@<host>:<port>/<database>.
Other databases (e.g. SwapHunt's) are given as their own env name: connect("SWAPHUNT_DB_URL").
"""
import os

import psycopg


def url(env: str = "RESEARCH_DB_URL") -> str:
    try:
        return os.environ[env]
    except KeyError:
        raise RuntimeError(f"environment variable {env} is not set") from None


def connect(env: str = "RESEARCH_DB_URL", **kw) -> psycopg.Connection:
    return psycopg.connect(url(env), **kw)


def query_df(sql: str, params=None, env: str = "RESEARCH_DB_URL"):
    """Run a SELECT and return a pandas DataFrame."""
    import pandas as pd

    with connect(env) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [c.name for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)
