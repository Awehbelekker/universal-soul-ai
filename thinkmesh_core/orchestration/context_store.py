"""
Context Store
=============

Shared context and knowledge management for multi-agent orchestration.
Provides persistent context storage and retrieval for agent coordination.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from ..config import OrchestrationConfig
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context data"""
    USER_PROFILE = "user_profile"
    CONVERSATION_HISTORY = "conversation_history"
    TASK_CONTEXT = "task_context"
    AGENT_KNOWLEDGE = "agent_knowledge"
    SHARED_MEMORY = "shared_memory"
    SYSTEM_STATE = "system_state"


@dataclass
class SharedContext:
    """Shared context structure"""
    context_id: str
    context_type: ContextType
    data: Dict[str, Any]
    created_timestamp: float
    updated_timestamp: float
    access_count: int
    tags: List[str]
    expiry_timestamp: Optional[float] = None
    owner_agent: Optional[str] = None
    access_permissions: List[str] = None


class ContextStore:
    """
    Context Store
    
    Manages shared context and knowledge for multi-agent coordination,
    providing persistent storage and intelligent retrieval of context data.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.is_initialized = False
        
        # Context storage
        self.contexts: Dict[str, SharedContext] = {}
        self.context_index: Dict[ContextType, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        
        # Access tracking
        self.access_history: List[Dict[str, Any]] = {}
        self.context_usage: Dict[str, Dict[str, Any]] = {}
        
        # Cache management
        self.cache_size_limit = 1000
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    async def initialize(self) -> None:
        """Initialize the context store"""
        try:
            logger.info("Initializing Context Store...")
            
            # Initialize context indices
            await self._initialize_indices()
            
            # Load existing contexts
            await self._load_contexts()
            
            # Setup cache management
            await self._setup_cache_management()
            
            # Start background cleanup task
            asyncio.create_task(self._background_cleanup())
            
            self.is_initialized = True
            logger.info("Context Store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Context Store: {e}")
            raise ThinkMeshException(
                f"Context Store initialization failed: {e}",
                ErrorCode.ORCHESTRATION_INITIALIZATION_FAILED
            )
    
    async def store_context(self, context_type: ContextType, data: Dict[str, Any],
                          tags: Optional[List[str]] = None, 
                          expiry_seconds: Optional[int] = None,
                          owner_agent: Optional[str] = None) -> str:
        """Store context data and return context ID"""
        try:
            context_id = f"{context_type.value}_{int(time.time() * 1000)}"
            current_time = time.time()
            
            # Calculate expiry timestamp
            expiry_timestamp = None
            if expiry_seconds:
                expiry_timestamp = current_time + expiry_seconds
            
            # Create shared context
            shared_context = SharedContext(
                context_id=context_id,
                context_type=context_type,
                data=data.copy(),
                created_timestamp=current_time,
                updated_timestamp=current_time,
                access_count=0,
                tags=tags or [],
                expiry_timestamp=expiry_timestamp,
                owner_agent=owner_agent,
                access_permissions=[]
            )
            
            # Store context
            self.contexts[context_id] = shared_context
            
            # Update indices
            await self._update_indices(shared_context)
            
            # Check cache size
            await self._check_cache_size()
            
            logger.debug(f"Stored context {context_id} of type {context_type.value}")
            return context_id
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            raise
    
    async def retrieve_context(self, context_id: str, 
                             requesting_agent: Optional[str] = None) -> Optional[SharedContext]:
        """Retrieve context by ID"""
        try:
            if context_id not in self.contexts:
                return None
            
            context = self.contexts[context_id]
            
            # Check expiry
            if context.expiry_timestamp and time.time() > context.expiry_timestamp:
                await self._remove_context(context_id)
                return None
            
            # Check permissions
            if not await self._check_access_permission(context, requesting_agent):
                logger.warning(f"Access denied for agent {requesting_agent} to context {context_id}")
                return None
            
            # Update access tracking
            context.access_count += 1
            await self._record_access(context_id, requesting_agent)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to retrieve context {context_id}: {e}")
            return None
    
    async def search_contexts(self, context_type: Optional[ContextType] = None,
                            tags: Optional[List[str]] = None,
                            query: Optional[str] = None,
                            limit: int = 10) -> List[SharedContext]:
        """Search contexts by type, tags, or content"""
        try:
            candidate_ids = set(self.contexts.keys())
            
            # Filter by context type
            if context_type:
                type_ids = self.context_index.get(context_type, set())
                candidate_ids &= type_ids
            
            # Filter by tags
            if tags:
                for tag in tags:
                    tag_ids = self.tag_index.get(tag, set())
                    candidate_ids &= tag_ids
            
            # Get contexts and filter expired ones
            valid_contexts = []
            current_time = time.time()
            
            for context_id in candidate_ids:
                context = self.contexts.get(context_id)
                if not context:
                    continue
                
                # Check expiry
                if context.expiry_timestamp and current_time > context.expiry_timestamp:
                    await self._remove_context(context_id)
                    continue
                
                # Text search in data
                if query:
                    context_text = json.dumps(context.data).lower()
                    if query.lower() not in context_text:
                        continue
                
                valid_contexts.append(context)
            
            # Sort by relevance (access count and recency)
            valid_contexts.sort(
                key=lambda c: (c.access_count, c.updated_timestamp),
                reverse=True
            )
            
            return valid_contexts[:limit]
            
        except Exception as e:
            logger.error(f"Context search failed: {e}")
            return []
    
    async def update_context(self, context_id: str, data: Dict[str, Any],
                           requesting_agent: Optional[str] = None) -> bool:
        """Update existing context data"""
        try:
            if context_id not in self.contexts:
                return False
            
            context = self.contexts[context_id]
            
            # Check permissions
            if not await self._check_access_permission(context, requesting_agent):
                return False
            
            # Update data
            context.data.update(data)
            context.updated_timestamp = time.time()
            
            logger.debug(f"Updated context {context_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update context {context_id}: {e}")
            return False
    
    async def delete_context(self, context_id: str,
                           requesting_agent: Optional[str] = None) -> bool:
        """Delete context"""
        try:
            if context_id not in self.contexts:
                return False
            
            context = self.contexts[context_id]
            
            # Check permissions (owner or admin)
            if context.owner_agent and context.owner_agent != requesting_agent:
                return False
            
            await self._remove_context(context_id)
            logger.debug(f"Deleted context {context_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete context {context_id}: {e}")
            return False
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get aggregated context for a user"""
        try:
            user_contexts = await self.search_contexts(
                context_type=ContextType.USER_PROFILE,
                tags=[f"user:{user_id}"]
            )
            
            conversation_contexts = await self.search_contexts(
                context_type=ContextType.CONVERSATION_HISTORY,
                tags=[f"user:{user_id}"]
            )
            
            aggregated_context = {
                "user_id": user_id,
                "profile": {},
                "conversation_history": [],
                "preferences": {},
                "last_updated": time.time()
            }
            
            # Aggregate user profile data
            for context in user_contexts:
                aggregated_context["profile"].update(context.data)
            
            # Aggregate conversation history
            for context in conversation_contexts:
                if "messages" in context.data:
                    aggregated_context["conversation_history"].extend(context.data["messages"])
            
            # Sort conversation history by timestamp
            aggregated_context["conversation_history"].sort(
                key=lambda m: m.get("timestamp", 0)
            )
            
            return aggregated_context
            
        except Exception as e:
            logger.error(f"Failed to get user context for {user_id}: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    async def store_conversation_turn(self, user_id: str, user_message: str,
                                    ai_response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a conversation turn"""
        try:
            conversation_data = {
                "user_id": user_id,
                "timestamp": time.time(),
                "user_message": user_message,
                "ai_response": ai_response,
                "metadata": metadata or {}
            }
            
            context_id = await self.store_context(
                context_type=ContextType.CONVERSATION_HISTORY,
                data=conversation_data,
                tags=[f"user:{user_id}", "conversation"],
                expiry_seconds=7 * 24 * 3600  # 7 days
            )
            
            return context_id
            
        except Exception as e:
            logger.error(f"Failed to store conversation turn: {e}")
            raise
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history for a user"""
        try:
            contexts = await self.search_contexts(
                context_type=ContextType.CONVERSATION_HISTORY,
                tags=[f"user:{user_id}"],
                limit=limit * 2  # Get more to account for filtering
            )
            
            # Extract conversation turns
            turns = []
            for context in contexts:
                if "user_message" in context.data and "ai_response" in context.data:
                    turns.append({
                        "timestamp": context.data.get("timestamp", context.created_timestamp),
                        "user_message": context.data["user_message"],
                        "ai_response": context.data["ai_response"],
                        "metadata": context.data.get("metadata", {})
                    })
            
            # Sort by timestamp (most recent first) and limit
            turns.sort(key=lambda t: t["timestamp"], reverse=True)
            return turns[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get conversation history for {user_id}: {e}")
            return []
    
    async def _initialize_indices(self) -> None:
        """Initialize context indices"""
        for context_type in ContextType:
            self.context_index[context_type] = set()
    
    async def _load_contexts(self) -> None:
        """Load existing contexts from storage"""
        # In production, this would load from persistent storage
        logger.debug("Context loading completed (simulated)")
    
    async def _setup_cache_management(self) -> None:
        """Setup cache management parameters"""
        # Configure cache management based on available memory
        pass
    
    async def _update_indices(self, context: SharedContext) -> None:
        """Update context indices"""
        # Update type index
        self.context_index[context.context_type].add(context.context_id)
        
        # Update tag index
        for tag in context.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(context.context_id)
    
    async def _remove_context(self, context_id: str) -> None:
        """Remove context and update indices"""
        if context_id not in self.contexts:
            return
        
        context = self.contexts[context_id]
        
        # Remove from type index
        self.context_index[context.context_type].discard(context_id)
        
        # Remove from tag index
        for tag in context.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(context_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
        
        # Remove context
        del self.contexts[context_id]
    
    async def _check_access_permission(self, context: SharedContext,
                                     requesting_agent: Optional[str]) -> bool:
        """Check if agent has permission to access context"""
        # For now, allow all access
        # In production, implement proper permission checking
        return True
    
    async def _record_access(self, context_id: str, requesting_agent: Optional[str]) -> None:
        """Record context access for analytics"""
        access_record = {
            "timestamp": time.time(),
            "context_id": context_id,
            "requesting_agent": requesting_agent
        }
        
        if not hasattr(self, 'access_history'):
            self.access_history = []
        
        self.access_history.append(access_record)
        
        # Limit access history size
        if len(self.access_history) > 10000:
            self.access_history = self.access_history[-5000:]
    
    async def _check_cache_size(self) -> None:
        """Check and manage cache size"""
        if len(self.contexts) > self.cache_size_limit:
            await self._cleanup_expired_contexts()
            
            # If still over limit, remove least recently used
            if len(self.contexts) > self.cache_size_limit:
                await self._cleanup_lru_contexts()
    
    async def _cleanup_expired_contexts(self) -> None:
        """Clean up expired contexts"""
        current_time = time.time()
        expired_ids = []
        
        for context_id, context in self.contexts.items():
            if context.expiry_timestamp and current_time > context.expiry_timestamp:
                expired_ids.append(context_id)
        
        for context_id in expired_ids:
            await self._remove_context(context_id)
        
        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired contexts")
    
    async def _cleanup_lru_contexts(self) -> None:
        """Clean up least recently used contexts"""
        # Sort contexts by last access (oldest first)
        sorted_contexts = sorted(
            self.contexts.items(),
            key=lambda item: item[1].updated_timestamp
        )
        
        # Remove oldest 20% of contexts
        remove_count = max(1, len(sorted_contexts) // 5)
        
        for i in range(remove_count):
            context_id = sorted_contexts[i][0]
            await self._remove_context(context_id)
        
        logger.debug(f"Cleaned up {remove_count} LRU contexts")
    
    async def _background_cleanup(self) -> None:
        """Background task for periodic cleanup"""
        while self.is_initialized:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                if time.time() - self.last_cleanup > self.cleanup_interval:
                    await self._cleanup_expired_contexts()
                    self.last_cleanup = time.time()
                    
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
    
    async def get_context_statistics(self) -> Dict[str, Any]:
        """Get context store statistics"""
        stats = {
            "total_contexts": len(self.contexts),
            "contexts_by_type": {},
            "total_tags": len(self.tag_index),
            "cache_usage": len(self.contexts) / self.cache_size_limit,
            "access_history_size": len(getattr(self, 'access_history', []))
        }
        
        # Count contexts by type
        for context_type in ContextType:
            stats["contexts_by_type"][context_type.value] = len(
                self.context_index.get(context_type, set())
            )
        
        return stats
    
    async def shutdown(self) -> None:
        """Shutdown the context store"""
        try:
            logger.info("Shutting down Context Store...")
            
            # Save contexts to persistent storage
            await self._save_contexts()
            
            self.is_initialized = False
            logger.info("Context Store shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Context Store shutdown: {e}")
    
    async def _save_contexts(self) -> None:
        """Save contexts to persistent storage"""
        # In production, this would save to persistent storage
        logger.debug("Context saving completed (simulated)")
