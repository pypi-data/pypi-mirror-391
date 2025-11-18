"""
Prisma Web3 Python Package

Async SQLAlchemy implementation of Prisma Web3 database models.
"""

# Core components
from .base import Base
from .config import config
from .database import get_db, init_db, close_db, AsyncSessionLocal

# Models (for direct query usage)
from .models import (
    Token,
    Signal,
    PreSignal,
    SignalStatus,
    TokenMetrics,
    TokenAnalysisReport,
    CryptoNews,
)

# Repositories (pre-built data access)
from .repositories import (
    BaseRepository,  # For custom repository inheritance
    TokenRepository,
    SignalRepository,
    PreSignalRepository,
    CryptoNewsRepository,
)

# Utilities
from .utils import (
    TokenImporter,
    ChainConfig,
)

__version__ = "0.2.3"

__all__ = [
    # Core
    "Base",
    "config",
    "get_db",
    "init_db",
    "close_db",
    "AsyncSessionLocal",
    "__version__",

    # Models
    "Token",
    "Signal",
    "PreSignal",
    "SignalStatus",
    "TokenMetrics",
    "TokenAnalysisReport",
    "CryptoNews",

    # Repositories
    "BaseRepository",
    "TokenRepository",
    "SignalRepository",
    "PreSignalRepository",
    "CryptoNewsRepository",

    # Utils
    "TokenImporter",
    "ChainConfig",
]
