"""
MCP Insights Server - Python Implementation (using asyncmy)
Stores and queries AI summaries/evaluations with MySQL backend.
"""

import os
from typing import Any
from datetime import datetime
import httpx
from asyncmy import create_pool
from asyncmy.pool import Pool
from asyncmy.cursors import DictCursor
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("essay-wechat-analysis-mcp-server-lc")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', ''),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'db': os.getenv('DB_NAME', ''),
    'charset': 'utf8mb4',
    'autocommit': True,
}

# Default account key
DEFAULT_ACCOUNT = os.getenv('DEFAULT_ACCOUNT', 'default')

# Global database pool
db_pool: Pool | None = None


async def get_db_pool() -> Pool:
    """Get or create database connection pool."""
    global db_pool
    if db_pool is None:
        db_pool = await create_pool(
            **DB_CONFIG,
            minsize=5,
            maxsize=20,
        )
    return db_pool


def resolve_account_key(account: str | None) -> str:
    """Resolve account key from provided value or default."""
    if account and account.strip():
        return account.strip()
    return DEFAULT_ACCOUNT


@mcp.tool()
async def save_summary(
        wxid: str,
        summary: str,
        account: str = "",
        offset: int = 0
) -> dict[str, Any]:
    """
    保存由AI生成的摘要；不会覆盖旧记录，会以追加的方式存储

    Args:
        wxid: 微信ID (talker/user_name)
        summary: 摘要内容
        account: 账号ID (wxid_*_*)；多账号时必填
        offset: 消息计数偏移（可选，默认0）
    """
    if not wxid or not summary:
        raise ValueError("wxid and summary are required")

    acc_key = resolve_account_key(account)
    pool = await get_db_pool()

    # Ensure offset is non-negative
    if offset < 0:
        offset = 0

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO summaries(account, wxid, summary, `offset`) VALUES(%s, %s, %s, %s)",
                (acc_key, wxid, summary, offset)
            )
            insert_id = cursor.lastrowid
            await conn.commit()

    return {"status": "ok", "id": insert_id}


@mcp.tool()
async def get_latest_summary(
        wxid: str,
        account: str = ""
) -> dict[str, Any]:
    """
    根据微信ID查询最近一次保存的摘要

    Args:
        wxid: 微信ID (talker/user_name)
        account: 账号ID (wxid_*_*)；多账号时必填
    """
    if not wxid:
        raise ValueError("wxid is required")

    acc_key = resolve_account_key(account)
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute(
                """SELECT summary, `offset`, created_at 
                   FROM summaries 
                   WHERE account = %s AND wxid = %s 
                   ORDER BY created_at DESC, id DESC 
                   LIMIT 1""",
                (acc_key, wxid)
            )
            row = await cursor.fetchone()

    if not row:
        return {"found": False}

    return {
        "found": True,
        "wxid": wxid,
        "summary": row['summary'],
        "offset": row['offset'],
        "created_at": row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else str(
            row['created_at'])
    }


@mcp.tool()
async def save_evaluation(
        wxid: str,
        intent_level: str,
        sentiment: str,
        account: str = "",
        satisfaction_score: str = "0",
        churn_warning: str = "0",
        needs: str = "",
        complaint_risk_warning: str = "0",
        professionalism_score: str = "0"
) -> dict[str, Any]:
    """
    保存AI评估/分析结果；不会覆盖旧记录，会以追加的方式存储

    Args:
        wxid: 微信ID (talker/user_name)
        intent_level: 客户意向等级评估：高/中/低
        sentiment: 客户情绪识别：满意/中性/不满
        account: 账号ID (wxid_*_*)；多账号时必填
        satisfaction_score: 服务满意度评分：整数，例 0-100
        churn_warning: 客户流失预警 0/1
        needs: 客户需求自动提取（文本）
        complaint_risk_warning: 投诉风险预警 0/1
        professionalism_score: 服务专业度评分：整数，例 0-100
    """
    if not wxid or not intent_level or not sentiment:
        raise ValueError("wxid, intent_level and sentiment are required")

    acc_key = resolve_account_key(account)
    pool = await get_db_pool()

    # Convert and validate scores
    try:
        satisfaction = int(satisfaction_score)
        satisfaction = max(0, min(100, satisfaction))  # Clamp to 0-100
    except (ValueError, TypeError):
        satisfaction = 0

    try:
        professionalism = int(professionalism_score)
        professionalism = max(0, min(100, professionalism))  # Clamp to 0-100
    except (ValueError, TypeError):
        professionalism = 0

    # Convert warnings to 0/1
    try:
        churn = 1 if int(churn_warning) != 0 else 0
    except (ValueError, TypeError):
        churn = 0

    try:
        complaint = 1 if int(complaint_risk_warning) != 0 else 0
    except (ValueError, TypeError):
        complaint = 0

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """INSERT INTO evaluations(
                    account, wxid, intent_level, satisfaction_score, 
                    churn_warning, sentiment, needs, complaint_risk_warning, 
                    professionalism_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (acc_key, wxid, intent_level, satisfaction, churn,
                 sentiment, needs, complaint, professionalism)
            )
            insert_id = cursor.lastrowid
            await conn.commit()

    return {"status": "ok", "id": insert_id}


@mcp.tool()
async def query_evaluations(
        wxid: str,
        account: str = "",
        limit: int = 20,
        offset: int = 0
) -> dict[str, Any]:
    """
    查询某个微信ID的历史评估记录，按时间倒序

    Args:
        wxid: 微信ID (talker/user_name)
        account: 账号ID (wxid_*_*)；多账号时必填
        limit: 返回条数（可选，默认20）
        offset: 偏移量（可选，默认0）
    """
    if not wxid:
        raise ValueError("wxid is required")

    if limit <= 0:
        limit = 20
    if offset < 0:
        offset = 0

    acc_key = resolve_account_key(account)
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute(
                """SELECT intent_level, satisfaction_score, churn_warning, 
                          sentiment, needs, complaint_risk_warning, 
                          professionalism_score, created_at
                   FROM evaluations 
                   WHERE account = %s AND wxid = %s 
                   ORDER BY created_at DESC, id DESC 
                   LIMIT %s OFFSET %s""",
                (acc_key, wxid, limit, offset)
            )
            rows = await cursor.fetchall()

    items = []
    for row in rows:
        items.append({
            "intent_level": row['intent_level'],
            "satisfaction_score": row['satisfaction_score'],
            "churn_warning": row['churn_warning'],
            "sentiment": row['sentiment'],
            "needs": row['needs'],
            "complaint_risk_warning": row['complaint_risk_warning'],
            "professionalism_score": row['professionalism_score'],
            "created_at": row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else str(
                row['created_at'])
        })

    return {
        "wxid": wxid,
        "total": len(items),
        "items": items,
        "ts": datetime.utcnow().isoformat()
    }


def run():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run()
