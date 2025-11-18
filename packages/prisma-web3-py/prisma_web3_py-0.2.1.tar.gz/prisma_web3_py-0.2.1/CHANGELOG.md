# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2025-11-12

### Added

- Added `PreSignalRepository` with comprehensive query methods:
  - `create_pre_signal()` - Create new pre-signals
  - `get_pre_signals_by_token()` - Query by token with time filters
  - `get_pre_signal_with_token()` - Get with relationship loading
  - `get_recent_pre_signals()` - Query recent signals
  - `update_pre_signal_status()` - Update signal status
  - `get_pre_signal_counts_by_type()` - Statistical queries
  - `get_trending_tokens_by_pre_signals()` - Trending token analysis
  - `get_pre_signals_by_source()` - Query by source
- Created example usage file (`examples/pre_signal_usage.py`) demonstrating all PreSignal operations
- Added model relationship validation test script

### Fixed

- **CRITICAL**: Fixed SQLAlchemy mapper configuration errors for composite foreign keys
  - Updated all `ForeignKeyConstraint` definitions to use qualified table names (e.g., `public.Token.chain`)
  - Fixed relationships between Token and related models (Signal, PreSignal, TokenMetrics, TokenAnalysisReport)
  - Added `viewonly=True` to Token's collection relationships to resolve mapper initialization errors
  - Fixed ForeignKey references in TokenPriceMonitor and TokenPriceHistory models
- Resolved "Could not determine join condition" errors for composite foreign key relationships
- Fixed "Foreign key associated with column could not find table" errors
- All SQLAlchemy mappers now initialize correctly without errors

### Changed

- Improved foreign key constraint definitions across all models for better PostgreSQL schema compatibility
- Updated import statements to include necessary SQLAlchemy ORM functions (`foreign`, `and_`)

---

## [0.1.1] - 2025-01-15

### Changed

- **Relaxed dependency versions** for better compatibility:
  - `python-dotenv>=0.19.0` (was `>=1.0.0`) - Now compatible with older projects
  - `asyncpg>=0.27.0` (was `>=0.29.0`) - Broader version support
  - Allows integration with more existing projects without version conflicts

### Fixed

- Version conflict with projects using `python-dotenv <1.0.0`
- Improved compatibility with Poetry and other dependency managers

---

## [0.1.0] - 2024-01-15

### Added

- Initial release of prisma-web3-py package
- 8 Core Models: Token, Signal, PreSignal, Groups, TokenMetrics, TokenAnalysisReport, TokenPriceMonitor, TokenPriceHistory
- Async Database Support with SQLAlchemy 2.0 + asyncpg
- Repository Pattern with specialized repositories
- Auto-Configuration from .env files
- Context Manager for easy database session management
- Full type hints support
- Comprehensive documentation
- Example code and integration guides

---

[0.1.1]: https://github.com/AnalyThothAI/prisma-web3/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/AnalyThothAI/prisma-web3/releases/tag/v0.1.0
