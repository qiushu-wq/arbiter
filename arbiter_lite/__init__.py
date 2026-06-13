"""Arbiter Lite — Multi-Agent Context Quota Manager (MIT)

Quota management + optional token compression (via Headroom integration).
Each agent gets a fixed partition. Idle agent quotas are reclaimed instantly.
With Headroom: 60-95% fewer tokens before context reaches the LLM.
"""

from .quota import QuotaManager
from .compress import compress_context, get_compression_stats

__version__ = "0.2.0"
__all__ = ["QuotaManager", "compress_context", "get_compression_stats"]
