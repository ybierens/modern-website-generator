"""
Database connection and operations for the Website Generator.

This module handles all database interactions including connection management,
CRUD operations for websites and jobs, and transaction handling.
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

import asyncpg
from asyncpg import Pool

from .models import WebsiteRecord, JobRecord, JobStatus


class Database:
    """Database connection and operations manager."""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:postgres@postgres:5432/website_generator"
        )
    
    async def connect(self):
        """Establish database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            print("✅ Database connection pool established")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            print("✅ Database connection pool closed")
    
    async def health_check(self) -> bool:
        """Check database connection health."""
        try:
            async with self.pool.acquire() as connection:
                await connection.fetchval("SELECT 1")
                return True
        except Exception as e:
            print(f"❌ Database health check failed: {e}")
            return False
    
    async def create_website(self, identifier: str, original_url: str, original_html: str = None) -> UUID:
        """Create a new website record."""
        async with self.pool.acquire() as connection:
            website_id = uuid4()
            await connection.execute(
                """
                INSERT INTO websites (id, identifier, original_url, original_html, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                """,
                website_id, identifier, original_url, original_html
            )
            return website_id
    
    async def get_website(self, identifier: str) -> Optional[WebsiteRecord]:
        """Get website by identifier."""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                SELECT id, identifier, original_url, original_html, generated_html, template_name, created_at, updated_at
                FROM websites 
                WHERE identifier = $1
                """,
                identifier
            )
            if row:
                return WebsiteRecord(**dict(row))
            return None
    
    async def get_website_by_id(self, website_id: UUID) -> Optional[WebsiteRecord]:
        """Get website by ID."""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                SELECT id, identifier, original_url, original_html, generated_html, template_name, created_at, updated_at
                FROM websites 
                WHERE id = $1
                """,
                website_id
            )
            if row:
                return WebsiteRecord(**dict(row))
            return None
    
    async def update_website_html(self, website_id: UUID, generated_html: str) -> bool:
        """Update the generated HTML for a website."""
        async with self.pool.acquire() as connection:
            result = await connection.execute(
                """
                UPDATE websites 
                SET generated_html = $1, updated_at = NOW()
                WHERE id = $2
                """,
                generated_html, website_id
            )
            return result == "UPDATE 1"
    
    async def website_exists(self, identifier: str) -> bool:
        """Check if website with identifier already exists."""
        async with self.pool.acquire() as connection:
            count = await connection.fetchval(
                "SELECT COUNT(*) FROM websites WHERE identifier = $1",
                identifier
            )
            return count > 0
    
    async def create_job(self, website_id: UUID = None) -> UUID:
        """Create a new job record."""
        async with self.pool.acquire() as connection:
            job_id = uuid4()
            await connection.execute(
                """
                INSERT INTO jobs (id, website_id, status, created_at, updated_at)
                VALUES ($1, $2, 'pending', NOW(), NOW())
                """,
                job_id, website_id
            )
            return job_id
    
    async def get_job(self, job_id: UUID) -> Optional[JobRecord]:
        """Get job by ID."""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                SELECT id, website_id, status, error_message, created_at, updated_at
                FROM jobs 
                WHERE id = $1
                """,
                job_id
            )
            if row:
                return JobRecord(**dict(row))
            return None
    
    async def update_job_status(self, job_id: UUID, status: str, error_message: str = None, website_id: UUID = None) -> bool:
        """Update job status and optionally link to website."""
        async with self.pool.acquire() as connection:
            if website_id:
                result = await connection.execute(
                    """
                    UPDATE jobs 
                    SET status = $1, error_message = $2, website_id = $3, updated_at = NOW()
                    WHERE id = $4
                    """,
                    status, error_message, website_id, job_id
                )
            else:
                result = await connection.execute(
                    """
                    UPDATE jobs 
                    SET status = $1, error_message = $2, updated_at = NOW()
                    WHERE id = $3
                    """,
                    status, error_message, job_id
                )
            return result == "UPDATE 1"
    
    async def get_recent_websites(self, limit: int = 10) -> List[WebsiteRecord]:
        """Get recently created websites."""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT id, identifier, original_url, original_html, generated_html, template_name, created_at, updated_at
                FROM websites 
                ORDER BY created_at DESC 
                LIMIT $1
                """,
                limit
            )
            return [WebsiteRecord(**dict(row)) for row in rows]
    
    async def create_image_mapping(self, website_id: UUID, original_url: str, cloudinary_url: str, alt_text: str = None) -> UUID:
        """Create a new image mapping record."""
        async with self.pool.acquire() as connection:
            mapping_id = uuid4()
            await connection.execute(
                """
                INSERT INTO image_mappings (id, website_id, original_url, cloudinary_url, alt_text, created_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
                """,
                mapping_id, website_id, original_url, cloudinary_url, alt_text
            )
            return mapping_id
    
    async def get_image_mappings(self, website_id: UUID) -> Dict[str, str]:
        """Get all image URL mappings for a website as a dictionary."""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(
                "SELECT original_url, cloudinary_url FROM image_mappings WHERE website_id = $1",
                website_id
            )
            return {row['original_url']: row['cloudinary_url'] for row in rows}
    
    async def get_website_images(self, website_id: UUID) -> List[Dict]:
        """Get all image mapping records for a website."""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT id, original_url, cloudinary_url, alt_text, created_at 
                FROM image_mappings 
                WHERE website_id = $1 
                ORDER BY created_at
                """,
                website_id
            )
            return [dict(row) for row in rows]
    
    async def update_website_template(self, website_id: UUID, template_name: str) -> bool:
        """Update the template name for a website."""
        async with self.pool.acquire() as connection:
            result = await connection.execute(
                """
                UPDATE websites 
                SET template_name = $1, updated_at = NOW()
                WHERE id = $2
                """,
                template_name, website_id
            )
            return result == "UPDATE 1"


# Global database instance
db = Database()
