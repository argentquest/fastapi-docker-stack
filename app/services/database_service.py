# V2 Database Service with pgvector support
import logging
from typing import List, Dict, Any, Optional
import asyncpg
import json
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """PostgreSQL + pgvector database service for V2 POC"""
    
    def __init__(self):
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_COMMAND_TIMEOUT
            )
            logger.info("Database connection pool initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def create_ai_log(
        self,
        system_prompt: str,
        user_context: str,
        ai_result: str,
        embedding: List[float],
        file_url: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ) -> dict:
        """
        Create a new AI test log entry.
        
        Args:
            system_prompt: System prompt used
            user_context: User's input context
            ai_result: AI's response
            embedding: Vector embedding of the user context
            file_url: URL to stored file (optional)
            response_time_ms: Response time in milliseconds (optional)
            
        Returns:
            Dict with the created log entry data
        """
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO ai_test_logs 
                    (system_prompt, user_context, ai_result, embedding, file_url, response_time_ms, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id, system_prompt, user_context, ai_result, file_url, response_time_ms, created_at
                """, 
                system_prompt, 
                user_context, 
                ai_result, 
                embedding,  # pgvector handles the list conversion
                file_url,
                response_time_ms,
                datetime.utcnow()
                )
                
                log_entry = dict(result)
                logger.info(f"Created AI log entry with ID: {log_entry['id']}")
                return log_entry
                
        except Exception as e:
            logger.error(f"Error creating AI log: {e}")
            raise RuntimeError(f"AI log creation failed: {e}")
    
    async def get_ai_logs(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """
        Retrieve AI test logs.
        
        Args:
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of log entry dictionaries
        """
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, system_prompt, user_context, ai_result, file_url, 
                           response_time_ms, created_at
                    FROM ai_test_logs
                    ORDER BY created_at DESC
                    LIMIT $1 OFFSET $2
                """, limit, offset)
                
                logs = [dict(result) for result in results]
                logger.debug(f"Retrieved {len(logs)} AI logs")
                return logs
                
        except Exception as e:
            logger.error(f"Error retrieving AI logs: {e}")
            raise RuntimeError(f"AI log retrieval failed: {e}")
    
    async def find_similar_logs(
        self,
        embedding: List[float],
        limit: int = 5,
        min_similarity: float = 0.5
    ) -> List[dict]:
        """
        Find similar AI logs using vector similarity search.
        
        Args:
            embedding: Vector embedding to search with
            limit: Maximum number of similar logs to return
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            List of similar log entries with similarity scores
        """
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, system_prompt, user_context, ai_result, file_url,
                           response_time_ms, created_at,
                           1 - (embedding <=> $1::vector) as similarity
                    FROM ai_test_logs
                    WHERE 1 - (embedding <=> $1::vector) >= $2
                    ORDER BY embedding <=> $1::vector
                    LIMIT $3
                """, embedding, min_similarity, limit)
                
                similar_logs = []
                for result in results:
                    log_dict = dict(result)
                    log_dict['similarity'] = float(log_dict['similarity'])
                    similar_logs.append(log_dict)
                
                logger.info(f"Found {len(similar_logs)} similar logs above {min_similarity} threshold")
                return similar_logs
                
        except Exception as e:
            logger.error(f"Error finding similar logs: {e}")
            raise RuntimeError(f"Similar logs search failed: {e}")
    
    async def get_log_by_id(self, log_id: int) -> Optional[dict]:
        """
        Get a specific AI log by ID.
        
        Args:
            log_id: ID of the log to retrieve
            
        Returns:
            Log entry dict or None if not found
        """
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT id, system_prompt, user_context, ai_result, file_url,
                           response_time_ms, created_at
                    FROM ai_test_logs
                    WHERE id = $1
                """, log_id)
                
                if result:
                    logger.debug(f"Retrieved AI log with ID: {log_id}")
                    return dict(result)
                else:
                    logger.debug(f"AI log with ID {log_id} not found")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving AI log {log_id}: {e}")
            raise RuntimeError(f"AI log retrieval failed: {e}")
    
    async def get_log_statistics(self) -> dict:
        """
        Get statistics about AI logs.
        
        Returns:
            Dict with various statistics
        """
        try:
            async with self.pool.acquire() as conn:
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_logs,
                        COUNT(CASE WHEN file_url IS NOT NULL THEN 1 END) as logs_with_files,
                        AVG(response_time_ms) as avg_response_time_ms,
                        MIN(created_at) as earliest_log,
                        MAX(created_at) as latest_log
                    FROM ai_test_logs
                """)
                
                statistics = dict(stats) if stats else {}
                
                # Convert decimals to float for JSON serialization
                if statistics.get('avg_response_time_ms'):
                    statistics['avg_response_time_ms'] = float(statistics['avg_response_time_ms'])
                
                logger.debug("Retrieved AI log statistics")
                return statistics
                
        except Exception as e:
            logger.error(f"Error retrieving log statistics: {e}")
            return {}
    
    async def delete_old_logs(self, days: int = 30) -> int:
        """
        Delete AI logs older than specified days.
        
        Args:
            days: Number of days to keep logs
            
        Returns:
            Number of deleted logs
        """
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM ai_test_logs
                    WHERE created_at < NOW() - INTERVAL $1
                """, f"{days} days")
                
                # Extract number of deleted rows from result
                deleted_count = int(result.split()[-1])
                logger.info(f"Deleted {deleted_count} AI logs older than {days} days")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error deleting old logs: {e}")
            return 0
    
    async def health_check(self) -> dict:
        """Check database connectivity and pgvector functionality"""
        try:
            async with self.pool.acquire() as conn:
                # Test basic connectivity
                result = await conn.fetchval("SELECT 1")
                
                # Test pgvector extension
                extensions = await conn.fetch("""
                    SELECT extname FROM pg_extension WHERE extname = 'vector'
                """)
                
                # Test table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'ai_test_logs'
                    )
                """)
                
                # Get log count
                log_count = await conn.fetchval("SELECT COUNT(*) FROM ai_test_logs")
                
                return {
                    "status": "healthy",
                    "connectivity": "ok" if result == 1 else "failed",
                    "pgvector_extension": "installed" if extensions else "missing",
                    "ai_test_logs_table": "exists" if table_exists else "missing",
                    "total_logs": int(log_count) if log_count else 0
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global service instance
database_service = DatabaseService()