import os
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import asyncpg
from contextlib import asynccontextmanager


class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.connection_string = self._get_connection_string()

    def _get_connection_string(self) -> str:
        """Get PostgreSQL connection string from environment variables"""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'ping_monitor')
        username = os.getenv('DB_USER', 'admin')
        password = os.getenv('DB_PASSWORD', 'password')

        return f"postgresql://{username}:{password}@{host}:{port}/{database}"

    async def initialize(self):
        """Initialize the database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            print("✅ Database connection pool initialized")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise

    async def close(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            print("✅ Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool"""
        if not self.pool:
            await self.initialize()

        async with self.pool.acquire() as connection:
            yield connection

    async def insert_ping_result(self, url: str, ip: str, status: str,
                                 response_time: Optional[float], count: int) -> int:
        """Insert a new ping result into the database"""
        query = """
                INSERT INTO ping_results (timestamp, url, ip, status, response_time_ms, count)
                VALUES ($1, $2, $3, $4, $5, $6) RETURNING id \
                """

        async with self.get_connection() as conn:
            result = await conn.fetchval(
                query,
                datetime.now(),
                url,
                ip,
                status,
                response_time,
                count
            )
            return result

    async def get_ping_results(self, url: Optional[str] = None,
                               limit: int = 100,
                               offset: int = 0) -> List[Dict[str, Any]]:
        """Get ping results with optional filtering"""
        if url:
            query = """
                    SELECT id, timestamp, url, host(ip) as ip, status, response_time_ms::float as response_time_ms, count
                    FROM ping_results
                    WHERE url = $1
                    ORDER BY timestamp DESC
                        LIMIT $2 \
                    OFFSET $3 \
                    """
            params = [url, limit, offset]
        else:
            query = """
                    SELECT id, timestamp, url, host(ip) as ip, status, response_time_ms::float as response_time_ms, count
                    FROM ping_results
                    ORDER BY timestamp DESC
                        LIMIT $1 \
                    OFFSET $2 \
                    """
            params = [limit, offset]

        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def get_latest_status(self) -> List[Dict[str, Any]]:
        """Get the latest status for each monitored URL"""
        query = """
                SELECT url, host(ip) as ip, status, response_time_ms::float as response_time_ms, timestamp, count
                FROM latest_ping_status
                ORDER BY url \
                """

        async with self.get_connection() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    async def get_url_statistics(self, url: str, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a specific URL over the last N hours"""
        query = """
        SELECT 
            COUNT(*) as total_pings,
            COUNT(CASE WHEN status = 'Success' THEN 1 END) as successful_pings,
            AVG(response_time_ms) as avg_response_time,
            MIN(response_time_ms) as min_response_time,
            MAX(response_time_ms) as max_response_time
        FROM ping_results
        WHERE url = $1 AND timestamp >= NOW() - INTERVAL '%s hours'
        """ % hours

        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, url)
            if row:
                stats = dict(row)
                stats['uptime_percentage'] = (
                    (stats['successful_pings'] / stats['total_pings'] * 100)
                    if stats['total_pings'] > 0 else 0
                )
                return stats
            return {}

    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Remove old ping results to keep database size manageable"""
        query = """
        DELETE FROM ping_results
        WHERE timestamp < NOW() - INTERVAL '%s days'
        """ % days_to_keep

        async with self.get_connection() as conn:
            deleted_count = await conn.execute(query)
            print(f"🗑️ Cleaned up {deleted_count} old records")
            return deleted_count


# Global database manager instance
db_manager = DatabaseManager()
