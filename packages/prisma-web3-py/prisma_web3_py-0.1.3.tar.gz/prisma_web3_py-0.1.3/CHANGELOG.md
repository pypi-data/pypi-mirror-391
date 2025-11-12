# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
