"""
全文搜索服务 - 基于SQLite FTS5
支持文章标题、内容、标签的全文检索
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.logger import logger
from ..core.database import async_session_maker


class SearchService:
    """全文搜索服务"""
    
    def __init__(self):
        self.db_session: Optional[AsyncSession] = None
    
    async def _get_session(self) -> AsyncSession:
        """获取数据库会话"""
        if self.db_session is None:
            self.db_session = async_session_maker()
        return self.db_session
    
    async def initialize_fts(self):
        """
        初始化FTS5虚拟表
        在数据库迁移时调用
        """
        try:
            async with async_session_maker() as session:
                # 创建FTS5虚拟表
                await session.execute(text("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS article_search USING fts5(
                        title,
                        content,
                        tags,
                        article_id UNINDEXED,
                        tokenize='porter unicode61'
                    )
                """))
                
                # 创建触发器保持数据同步
                # 插入触发器
                await session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS article_insert_trigger
                    AFTER INSERT ON articles
                    BEGIN
                        INSERT INTO article_search(title, content, tags, article_id)
                        VALUES (NEW.title, NEW.content, NEW.tags, NEW.id);
                    END
                """))
                
                # 更新触发器
                await session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS article_update_trigger
                    AFTER UPDATE ON articles
                    BEGIN
                        UPDATE article_search
                        SET title = NEW.title,
                            content = NEW.content,
                            tags = NEW.tags
                        WHERE article_id = NEW.id;
                    END
                """))
                
                # 删除触发器
                await session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS article_delete_trigger
                    AFTER DELETE ON articles
                    BEGIN
                        DELETE FROM article_search WHERE article_id = OLD.id;
                    END
                """))
                
                await session.commit()
                logger.info("FTS5全文搜索表初始化成功")
                
        except Exception as e:
            logger.error(f"FTS5初始化失败: {e}")
            raise
    
    async def rebuild_index(self):
        """
        重建全文搜索索引
        用于初始化或数据修复
        """
        try:
            async with async_session_maker() as session:
                # 清空现有索引
                await session.execute(text("DELETE FROM article_search"))
                
                # 重新索引所有文章
                await session.execute(text("""
                    INSERT INTO article_search(title, content, tags, article_id)
                    SELECT title, content, tags, id FROM articles
                """))
                
                await session.commit()
                logger.info("全文搜索索引重建完成")
                
        except Exception as e:
            logger.error(f"重建索引失败: {e}")
            raise
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        全文搜索
        
        Args:
            query: 搜索关键词
            filters: 过滤条件（status, date_range等）
            limit: 返回数量
            offset: 偏移量
            
        Returns:
            搜索结果
        """
        try:
            async with async_session_maker() as session:
                # 处理搜索查询
                # 支持多关键词搜索，使用AND连接
                keywords = query.split()
                fts_query = ' AND '.join(keywords)
                
                # 基础查询
                base_sql = """
                    SELECT 
                        a.id,
                        a.title,
                        a.summary,
                        a.content,
                        a.status,
                        a.tags,
                        a.view_count,
                        a.like_count,
                        a.created_at,
                        a.updated_at,
                        rank as search_rank
                    FROM article_search s
                    JOIN articles a ON s.article_id = a.id
                    WHERE article_search MATCH :query
                """
                
                params = {"query": fts_query}
                
                # 添加过滤条件
                where_clauses = []
                if filters:
                    if filters.get('status'):
                        where_clauses.append("a.status = :status")
                        params['status'] = filters['status']
                    
                    if filters.get('date_from'):
                        where_clauses.append("a.created_at >= :date_from")
                        params['date_from'] = filters['date_from']
                    
                    if filters.get('date_to'):
                        where_clauses.append("a.created_at <= :date_to")
                        params['date_to'] = filters['date_to']
                
                if where_clauses:
                    base_sql += " AND " + " AND ".join(where_clauses)
                
                # 排序
                base_sql += " ORDER BY rank"
                
                # 获取总数
                count_sql = f"""
                    SELECT COUNT(*) FROM ({base_sql})
                """
                count_result = await session.execute(text(count_sql), params)
                total = count_result.scalar()
                
                # 分页
                base_sql += " LIMIT :limit OFFSET :offset"
                params['limit'] = limit
                params['offset'] = offset
                
                # 执行查询
                result = await session.execute(text(base_sql), params)
                rows = result.fetchall()
                
                # 处理结果
                articles = []
                for row in rows:
                    article = {
                        "id": row.id,
                        "title": row.title,
                        "summary": row.summary,
                        "status": row.status,
                        "tags": row.tags.split(',') if row.tags else [],
                        "view_count": row.view_count,
                        "like_count": row.like_count,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                        "search_rank": row.search_rank,
                        # 高亮匹配内容
                        "highlight": self._extract_highlight(row.content, keywords)
                    }
                    articles.append(article)
                
                return {
                    "success": True,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "query": query,
                    "articles": articles
                }
                
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "articles": [],
                "total": 0
            }
    
    def _extract_highlight(self, content: str, keywords: List[str], length: int = 200) -> str:
        """
        提取匹配内容的高亮片段
        
        Args:
            content: 文章内容
            keywords: 关键词列表
            length: 片段长度
            
        Returns:
            高亮片段
        """
        if not content:
            return ""
        
        content_lower = content.lower()
        
        # 找到第一个匹配位置
        match_pos = -1
        for keyword in keywords:
            pos = content_lower.find(keyword.lower())
            if pos != -1:
                match_pos = pos
                break
        
        if match_pos == -1:
            # 没有匹配，返回开头
            return content[:length] + "..." if len(content) > length else content
        
        # 提取片段
        start = max(0, match_pos - length // 2)
        end = min(len(content), start + length)
        
        snippet = content[start:end]
        
        # 添加省略号
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    async def get_suggestions(
        self,
        query: str,
        limit: int = 10
    ) -> List[str]:
        """
        获取搜索建议（自动补全）
        
        Args:
            query: 输入的查询
            limit: 返回数量
            
        Returns:
            建议列表
        """
        try:
            async with async_session_maker() as session:
                # 从标题中获取建议
                sql = """
                    SELECT DISTINCT title
                    FROM article_search
                    WHERE title MATCH :query || '*'
                    ORDER BY rank
                    LIMIT :limit
                """
                
                result = await session.execute(
                    text(sql),
                    {"query": query, "limit": limit}
                )
                
                rows = result.fetchall()
                suggestions = [row.title for row in rows]
                
                return suggestions
                
        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []
    
    async def get_popular_keywords(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取热门搜索关键词
        
        Args:
            limit: 返回数量
            
        Returns:
            热门关键词列表
        """
        try:
            async with async_session_maker() as session:
                # 从标签中提取热门关键词
                sql = """
                    SELECT 
                        TRIM(value) as keyword,
                        COUNT(*) as count
                    FROM articles,
                    json_each('["' || REPLACE(tags, ',', '","') || '"]')
                    WHERE tags IS NOT NULL AND tags != ''
                    GROUP BY TRIM(value)
                    ORDER BY count DESC
                    LIMIT :limit
                """
                
                result = await session.execute(text(sql), {"limit": limit})
                rows = result.fetchall()
                
                keywords = [
                    {"keyword": row.keyword, "count": row.count}
                    for row in rows
                ]
                
                return keywords
                
        except Exception as e:
            logger.error(f"获取热门关键词失败: {e}")
            return []


# 全局实例
search_service = SearchService()
