"""Arbiter + Headroom — Token compression integration
Optional pre-processor: compress context before LLM calls.
Saves 60-95% tokens. Falls back to pass-through if headroom not installed.
"""
from typing import Any, Dict

try:
    from headroom import compress as _headroom_compress
    HAS_HEADROOM = True
except ImportError:
    HAS_HEADROOM = False


def compress_context(context: Any) -> Any:
    """Compress context before LLM call. No-op if headroom not installed."""
    if not HAS_HEADROOM:
        return context

    if isinstance(context, str):
        return _headroom_compress(context)
    if isinstance(context, list):
        return [_headroom_compress(m) if isinstance(m, str) else m for m in context]
    if isinstance(context, dict):
        return {k: _headroom_compress(v) if isinstance(v, str) else v
                for k, v in context.items()}
    return context


def get_compression_stats() -> Dict:
    """Check if headroom compression is available."""
    return {
        'available': HAS_HEADROOM,
        'install': 'pip install headroom-ai' if not HAS_HEADROOM else None,
        'savings': '60-95% fewer tokens' if HAS_HEADROOM else 'N/A',
    }
