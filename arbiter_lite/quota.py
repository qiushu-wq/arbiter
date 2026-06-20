"""Arbiter Lite — 多Agent配额管理 (MIT)
40行代码，解决多Agent上下文争抢问题。
每个Agent分配固定配额，闲置Agent的配额自动回收给活跃Agent。
"""

from datetime import datetime, timedelta
from typing import Dict, List


class QuotaManager:
    """固定分区 + 即时回收的配额管理器"""

    def __init__(self, max_tokens: int, agent_names: List[str], idle_timeout: int = 300):
        self.max_tokens = max_tokens
        self.partition_size = max_tokens // max(len(agent_names), 1)
        self.quotas: Dict[str, int] = {a: self.partition_size for a in agent_names}
        self.last_active: Dict[str, datetime] = {a: datetime.now() for a in agent_names}
        self.idle_timeout = idle_timeout  # 默认5分钟

    def request(self, agent: str, tokens_needed: int) -> int:
        """请求配额。返回实际获得的token数。"""
        now = datetime.now()
        self.last_active[agent] = now

        # 即时回收：闲置Agent的配额
        reclaimed = 0
        for a in self.quotas:
            if a == agent:
                continue
            idle_seconds = (now - self.last_active[a]).total_seconds()
            if idle_seconds > self.idle_timeout:
                half = self.quotas[a] // 2
                self.quotas[a] -= half
                reclaimed += half

        self.quotas[agent] = self.quotas.get(agent, self.partition_size) + reclaimed
        granted = min(tokens_needed, self.quotas[agent])
        self.quotas[agent] -= granted
        return granted

    def status(self) -> Dict:
        now = datetime.now()
        return {a: {
            'quota': q,
            'partition': self.partition_size,
            'idle_seconds': int((now - self.last_active[a]).total_seconds())
        } for a, q in self.quotas.items()}
