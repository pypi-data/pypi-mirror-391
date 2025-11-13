# Prisma Web3 Python

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-green)](https://www.sqlalchemy.org/)
[![AsyncIO](https://img.shields.io/badge/AsyncIO-✓-brightgreen)](https://docs.python.org/3/library/asyncio.html)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**异步 Web3 数据库 ORM** - 基于 SQLAlchemy 2.0 + AsyncIO 的高性能区块链数据访问层

[特性](#-特性) • [安装](#-安装) • [快速开始](#-快速开始) • [文档](#-文档) • [示例](#-示例) • [扩展](#-扩展)

</div>

---

## 📖 目录

- [简介](#-简介)
- [特性](#-特性)
- [架构](#-架构)  
- [安装](#-安装)
- [快速开始](#-快速开始)
- [核心概念](#-核心概念)
- [详细使用](#-详细使用)
- [扩展开发](#-扩展开发)
- [API 参考](#-api-参考)
- [最佳实践](#-最佳实践)
- [常见问题](#-常见问题)

---

## 🎯 简介

**Prisma Web3 Python** 是一个专为 Web3 应用设计的异步数据库 ORM 层，提供：

- 🚀 **高性能异步操作** - 基于 AsyncIO + AsyncPG
- 🔄 **跨链支持** - 统一的数据模型处理多链资产
- 🎨 **简洁的 API** - Repository 模式，开箱即用
- 🔌 **完全可扩展** - 暴露所有底层组件，支持自定义
- 📊 **类型安全** - 完整的类型提示支持
- 🌐 **链名规范化** - 自动处理链名缩写和标准名转换

**适用场景**：
- Web3 数据分析平台
- Token 追踪和监控系统
- 链上信号聚合服务
- DeFi 数据仓库
- NFT 元数据管理

---

## ✨ 特性

### 核心功能

| 功能 | 说明 |
|------|------|
| **异步优先** | 全异步 API，支持高并发操作 |
| **跨链设计** | 单表设计存储跨链 Token，支持多链地址映射 |
| **链名智能化** | 自动规范化链名（`sol` ↔ `solana`，`bsc` ↔ `binance-smart-chain`） |
| **Repository 模式** | 预构建的数据访问层，包含常用查询方法 |
| **灵活查询** | 支持符号、名称、别名、模糊搜索 |
| **批量操作** | 高效的批量插入和更新 |
| **完整扩展性** | 暴露 Models、Repositories、Session 等所有组件 |

### 数据模型

#### Token（代币）
- 跨链 Token 信息存储
- 支持 platforms 字段存储多链地址
- 自动主链选择（按优先级）
- 社交链接、分类、别名支持

#### Signal（信号）
- Token 信号追踪
- 来源、类型、频次统计
- 时间序列分析

#### PreSignal（预信号）
- 早期信号捕获
- 多维度评分（频道呼声、多信号、KOL讨论）
- 状态管理（开放/已转换/已关闭）

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────┐
│              Your Application                        │
│  (FastAPI / Flask / Django / Custom)                 │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│          Prisma Web3 Python Package                  │
│                                                      │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ Repositories │◄───│   Models     │              │
│  │  - Token     │    │   - Token    │              │
│  │  - Signal    │    │   - Signal   │              │
│  │  - PreSignal │    │   - PreSignal│              │
│  └──────────────┘    └──────────────┘              │
│         │                    │                       │
│         └────────┬───────────┘                       │
│                  ▼                                   │
│        ┌──────────────────┐                         │
│        │   Database       │                         │
│        │   (Session Mgmt) │                         │
│        └──────────────────┘                         │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
          ┌──────────────────────────┐
          │   PostgreSQL Database    │
          │   (AsyncPG Driver)       │
          └──────────────────────────┘
```

---

## 📦 安装

### 要求

- Python 3.8+
- PostgreSQL 12+
- AsyncPG 驱动

### 使用 pip 安装

\`\`\`bash
# 基础安装
pip install prisma-web3-py

# 从源码安装（开发版）
git clone https://github.com/your-org/prisma-web3.git
cd prisma-web3/python
pip install -e .
\`\`\`

### 数据库设置

1. **创建数据库**：
\`\`\`bash
psql -U postgres
CREATE DATABASE your_database;
\`\`\`

2. **运行迁移**（使用 Prisma）：
\`\`\`bash
cd ../  # 回到项目根目录
npx prisma migrate dev
\`\`\`

3. **配置环境变量**：
\`\`\`bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/your_database
\`\`\`

---

## 🚀 快速开始

### 1. 初始化数据库连接

\`\`\`python
import asyncio
from prisma_web3_py import init_db, close_db, get_db

async def main():
    # 初始化数据库连接池
    await init_db()

    try:
        # 你的业务逻辑
        async with get_db() as session:
            # 使用 session 进行数据库操作
            pass
    finally:
        # 关闭连接池
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
\`\`\`

### 2. 使用 Repository 查询

\`\`\`python
from prisma_web3_py import get_db, TokenRepository

async def query_tokens():
    repo = TokenRepository()

    async with get_db() as session:
        # 获取 Token（支持链名缩写！）
        token = await repo.get_by_address(
            session,
            chain='sol',  # 自动转换为 'solana'
            token_address='oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo'
        )

        print(f"Token: {token.symbol} - {token.name}")
        print(f"Chain: {token.chain}")  # 输出: solana

        # 搜索 Tokens
        tokens = await repo.search_tokens(session, "BTC", limit=10)
        for t in tokens:
            print(f"- {t.symbol}: {t.name}")
\`\`\`

### 3. 插入数据

\`\`\`python
from prisma_web3_py import get_db, TokenRepository

async def insert_token():
    repo = TokenRepository()

    async with get_db() as session:
        token_data = {
            "chain": "eth",  # 使用缩写
            "token_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
            "symbol": "UNI",
            "name": "Uniswap",
            "coingecko_id": "uniswap",
            "decimals": 18,
            "platforms": {
                "ethereum": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                "polygon-pos": "0xb33eaad8d922b1083446dc23f610c2567fb5180f"
            }
        }

        token_id = await repo.upsert_token(session, token_data)
        await session.commit()

        print(f"Token saved with ID: {token_id}")
\`\`\`

### 4. 使用 Models 直接查询

\`\`\`python
from prisma_web3_py import get_db, Token, Signal
from sqlalchemy import select, func

async def custom_query():
    async with get_db() as session:
        # 自定义复杂查询
        stmt = (
            select(Token, func.count(Signal.id).label('signal_count'))
            .join(Signal, (Token.chain == Signal.chain) &
                          (Token.token_address == Signal.token_address))
            .group_by(Token.id)
            .order_by(func.count(Signal.id).desc())
            .limit(10)
        )

        result = await session.execute(stmt)
        for token, count in result:
            print(f"{token.symbol}: {count} signals")
\`\`\`

---

## 💡 核心概念

### 1. Repository Pattern（仓储模式）

Repository 是数据访问层的抽象，隐藏了 SQL 查询细节。

所有 Repository 都继承自 `BaseRepository`，提供基础 CRUD 方法。

### 2. 链名规范化

所有 Repository 自动处理链名转换：

\`\`\`python
# 这些都可以工作
await repo.get_by_address(session, "sol", "address")   # 缩写
await repo.get_by_address(session, "eth", "address")   # 缩写
await repo.get_by_address(session, "solana", "address")  # 标准名

# Repository 会自动转换为 CoinGecko 标准名存入数据库
\`\`\`

支持的链：Ethereum (`eth`), BSC (`bsc`), Solana (`sol`), Polygon (`poly`), Arbitrum (`arb`), Base (`base`) 等 18+ 条链。

### 3. 跨链 Token 设计

Token 表采用单表设计存储跨链资产：

\`\`\`python
{
    "chain": "ethereum",        # 主链（优先级最高）
    "token_address": "0x...",   # 主链地址
    "symbol": "UNI",
    "platforms": {              # 跨链地址映射 (JSONB)
        "ethereum": "0x...",
        "polygon-pos": "0x...",
        "arbitrum-one": "0x..."
    }
}
\`\`\`

### 4. 异步 Context Manager

使用 `get_db()` 自动管理 Session 生命周期：

\`\`\`python
async with get_db() as session:
    # session 自动创建
    result = await repo.get_all(session)
    await session.commit()
    # session 自动关闭
\`\`\`

---

## 📚 详细使用

完整的使用示例请查看主 README 顶部的快速开始章节。

主要操作包括：
- Token 查询、创建、更新
- Signal 管理
- PreSignal 处理
- 自定义查询
- 批量导入

详细 API 文档请参考 [API 参考](#-api-参考) 部分。

---

## 🔌 扩展开发

Prisma Web3 Python 完全可扩展。详细指南请参考 [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)。

### 快速示例

#### 1. 继承 BaseRepository

\`\`\`python
from prisma_web3_py import BaseRepository, Token

class MyTokenRepository(BaseRepository[Token]):
    async def get_high_value_tokens(self, session, min_supply: float):
        # 自定义查询
        pass
\`\`\`

#### 2. 使用 Models 直接查询

\`\`\`python
from prisma_web3_py import get_db, Token
from sqlalchemy import select

async with get_db() as session:
    stmt = select(Token).where(Token.symbol == 'BTC')
    result = await session.execute(stmt)
\`\`\`

#### 3. 扩展现有 Repository

\`\`\`python
from prisma_web3_py import TokenRepository

class ExtendedTokenRepository(TokenRepository):
    async def new_feature(self, session):
        # 添加新方法
        pass
\`\`\`

---

## 📖 API 参考

### 核心组件

\`\`\`python
from prisma_web3_py import (
    # Core
    Base, get_db, init_db, close_db, AsyncSessionLocal,
    
    # Models
    Token, Signal, PreSignal, SignalStatus,
    
    # Repositories
    BaseRepository, TokenRepository, SignalRepository, PreSignalRepository,
    
    # Utils
    TokenImporter, ChainConfig
)
\`\`\`

### TokenRepository 主要方法

- `get_by_address(session, chain, token_address)` - 按链和地址查询
- `search_tokens(session, search_term, chain, limit)` - 搜索
- `search_by_symbol(session, symbol, exact)` - 按符号搜索
- `search_by_name(session, name, exact)` - 按名称搜索
- `search_by_alias(session, alias)` - 按别名搜索
- `fuzzy_search(session, text, threshold, limit)` - 模糊搜索
- `upsert_token(session, token_data)` - 插入或更新
- `get_recent_tokens(session, chain, limit)` - 最近创建
- `get_recently_updated_tokens(session, hours, chain, limit)` - 最近更新

完整 API 请查看源码注释。

---

## 🎯 最佳实践

### 1. 使用 Context Manager

✅ **推荐**：
\`\`\`python
async with get_db() as session:
    result = await repo.get_all(session)
    await session.commit()
\`\`\`

### 2. 错误处理

\`\`\`python
from sqlalchemy.exc import SQLAlchemyError

async with get_db() as session:
    try:
        await repo.create(session, **data)
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Error: {e}")
        raise
\`\`\`

### 3. 使用链名缩写

\`\`\`python
# 推荐：使用缩写，更简洁
await repo.get_by_address(session, 'sol', 'address')
await repo.get_by_address(session, 'eth', 'address')
await repo.get_by_address(session, 'bsc', 'address')
\`\`\`

---

## ❓ 常见问题

### Q1: 如何处理链名？

**A**: 所有 Repository 都自动规范化链名。你可以使用缩写（`sol`, `eth`, `bsc`）或标准名（`solana`, `ethereum`, `binance-smart-chain`），数据库会统一存储为 CoinGecko 标准名。

### Q2: 如何执行自定义查询？

**A**: 三种方式：
1. 直接使用 Models + SQLAlchemy
2. 继承 BaseRepository
3. 扩展现有 Repository

详见 [扩展开发](#-扩展开发) 或 [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)。

### Q3: 支持哪些数据库？

**A**: 目前只支持 **PostgreSQL**（使用 AsyncPG 驱动）。

---

## 📚 文档

- **扩展指南**: [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md) - 如何扩展模块
- **架构文档**: [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构说明
- **导入指南**: [IMPORT_GUIDE.md](IMPORT_GUIDE.md) - Token 数据导入

---

## 🛠️ 开发工具

### 测试

\`\`\`bash
# 运行所有测试
python scripts/run_all_tests.py

# 运行特定测试
python scripts/test_token.py
python scripts/test_signal.py
python scripts/test_pre_signal.py
\`\`\`

### 数据导入

\`\`\`bash
# 导入 token 数据
python scripts/import_token_recognition_data.py
\`\`\`

### 验证

\`\`\`bash
# 验证数据一致性
python scripts/verify_consistency.py

# 测试数据库连接
python scripts/test_connection.py
\`\`\`

---

## 📝 更新日志

### v0.1.8 (最新)
- ✨ 完全暴露 Models、Repositories、Session 等组件
- ✨ 新增扩展指南（EXTENSION_GUIDE.md）
- 🐛 修复外键约束问题（链名规范化）
- 📚 新增详细 README 文档

### v0.1.6
- ✨ 新增链名自动规范化功能
- ✨ TokenRepository 新增多种搜索方法
- ♻️ 移除 TokenRecognition 模块

---

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐️！**

Made with ❤️ by the Prisma Web3 Team

</div>
