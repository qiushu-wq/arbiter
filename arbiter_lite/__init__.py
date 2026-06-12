"""Arbiter Lite — Multi-Agent Context Quota Manager (MIT)

40 lines of Python. Fixes the most common multi-agent crash: context contention.
Each agent gets a fixed partition. Idle agent quotas are reclaimed instantly.
"""

from .quota import QuotaManager

__version__ = "0.1.0"
__all__ = ["QuotaManager"]
