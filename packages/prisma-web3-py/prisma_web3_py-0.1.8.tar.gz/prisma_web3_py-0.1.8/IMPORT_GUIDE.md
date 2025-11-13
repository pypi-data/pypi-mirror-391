# 🚀 Token Data Import Guide

完整的代币数据导入指南，包括验证、导入和使用说明。

---

## 📋 导入前检查清单

### ✅ 所有验证已通过

运行验证脚本确认系统就绪：
```bash
# 一致性检查（7/7 通过）
python scripts/verify_consistency.py

# 数据验证（1000 tokens 有效）
python scripts/test_import_data.py
```

**验证结果**:
- ✅ Prisma Schema ↔ Python Model: 32字段完全匹配
- ✅ TokenImporter 字段处理: 16个必需字段
- ✅ 主链优先级: ethereum > BSC > polygon > solana...
- ✅ 主网代币处理: 使用 coingecko_id 作为 token_address
- ✅ 唯一约束: (chain, token_address) + coingecko_id
- ✅ 模型关系: 4个关系，使用 viewonly=True
- ✅ 导入脚本: 自动加载并合并 aliases

---

## 📊 数据概览

### 数据文件位置
```
python/token_recognition/data/
├── tokens.json    (1000 tokens)
└── aliases.json   (741 alias mappings)
```

### 数据统计
| 类型 | 数量 | 说明 |
|------|------|------|
| **总代币数** | 1000 | 全部有效 |
| **主网代币** | 111 | BTC, ETH, LTC... |
| **跨链代币** | 457 | 2条以上链 |
| **单链代币** | 432 | 仅一条链 |
| **带别名代币** | 797 | 自动合并 |

### Top 链分布
1. ethereum: 486
2. binance-smart-chain: 293
3. solana: 186
4. base: 184
5. arbitrum-one: 148
6. polygon-pos: 98
7. avalanche: 78

### 社交链接覆盖率
- Website: 96.5%
- Twitter: 88.9%
- Telegram: 58.3%
- GitHub: 49.9%
- Discord: 42.5%

---

## 🚀 执行导入

### 基本导入命令

```bash
cd /Users/qinghuan/Documents/code/prisma-web3/python

# 标准导入（推荐）- 自动合并 aliases
python scripts/import_token_recognition_data.py
```

### 可选参数

```bash
# 只创建新代币，跳过已存在的
python scripts/import_token_recognition_data.py --no-update

# 自定义批次大小（默认50）
python scripts/import_token_recognition_data.py --batch-size 100

# 指定自定义文件路径
python scripts/import_token_recognition_data.py \
  --tokens-file path/to/tokens.json \
  --aliases-file path/to/aliases.json
```

### 预期输出

```
============================================================
Token Recognition Data Import
============================================================
Tokens file: /path/to/tokens.json
Aliases file: /path/to/aliases.json
Update existing: True
Batch size: 50
============================================================
Loading tokens from tokens.json...
Loaded 1000 tokens
Loading aliases from aliases.json...
Loaded 741 alias mappings
Created alias map with 741 entries
Merged aliases for 797 tokens  ← 自动合并！
Database connection established
Importing 1000 tokens...
Progress: 50/1000 tokens processed
Progress: 100/1000 tokens processed
Progress: 150/1000 tokens processed
...
Progress: 1000/1000 tokens processed
Import complete
============================================================
Import Complete!
============================================================
Total tokens processed: 1000
Created: 1000
Updated: 0
Skipped: 0
Errors: 0
============================================================
```

---

## 🔧 关键技术细节

### 1. 主网代币处理（Bug Fix）

**问题**: 多个主网代币（BTC, ETH等）都有 `chain=''` 和 `token_address=''`，违反唯一约束。

**解决方案**:
```python
# 主网代币现在使用:
chain = ""
token_address = coingecko_id  # e.g., "bitcoin", "ethereum"
platforms = {}
```

**示例**:
| Token | chain | token_address | platforms |
|-------|-------|---------------|-----------|
| BTC | `""` | `"bitcoin"` | `{}` |
| ETH | `""` | `"ethereum"` | `{}` |

### 2. 跨链代币处理

主链优先级（从高到低）:
1. ethereum
2. binance-smart-chain
3. base
4. arbitrum-one
5. optimistic-ethereum
6. polygon-pos
7. solana
8. avalanche

**示例（USDT）**:
```python
# 主链存储在 chain/token_address
chain = "ethereum"
token_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"

# 其他链存储在 platforms JSON
platforms = {
  "tron": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
  "solana": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
  "polygon-pos": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"
}
```

### 3. 链名称规范化与缩写 (Chain Configuration)

**设计原则**:
- 数据库存储 CoinGecko 标准名称（数据一致性）
- 应用层使用缩写（便捷性）

**标准名称 <-> 缩写映射**:
| 标准名称 | 缩写 | 显示名称 |
|---------|------|---------|
| `ethereum` | `eth` | Ethereum |
| `binance-smart-chain` | `bsc` | BNB Chain |
| `solana` | `sol` | Solana |
| `base` | `base` | Base |
| `arbitrum-one` | `arb` | Arbitrum |
| `polygon-pos` | `poly` | Polygon |
| `avalanche` | `avax` | Avalanche |
| `optimistic-ethereum` | `op` | Optimism |

**使用示例**:
```python
from prisma_web3_py.utils import ChainConfig, Chain

# 方式1: 使用 ChainConfig 类
ChainConfig.get_abbreviation("ethereum")  # -> "eth"
ChainConfig.get_standard_name("eth")      # -> "ethereum"
ChainConfig.get_display_name("eth")       # -> "Ethereum"

# 方式2: 使用便捷函数
from prisma_web3_py.utils import abbr, standard, display

abbr("ethereum")      # -> "eth"
standard("eth")       # -> "ethereum"
display("bsc")        # -> "BNB Chain"

# 方式3: 使用常量
Chain.ETH             # -> "eth"
Chain.BSC             # -> "bsc"
Chain.ETHEREUM        # -> "ethereum"
```

**Token 模型集成**:
```python
token = await token_repo.get_by_symbol(session, "UNI")

# 获取链缩写
token.get_chain_abbr()                    # -> "eth"
token.get_chain_display_name()            # -> "Ethereum"

# 使用缩写获取地址
token.get_address_on_chain_abbr("eth")    # 支持缩写
token.get_address_on_chain("ethereum")    # 支持标准名称

# 获取所有链信息（含缩写）
chains = token.get_all_chains_with_abbr()
# [
#   {'standard': 'ethereum', 'abbr': 'eth', 'display': 'Ethereum'},
#   {'standard': 'polygon-pos', 'abbr': 'poly', 'display': 'Polygon'}
# ]
```

**TokenRecognition 支持**:
```python
from prisma_web3_py.utils import TokenRecognition

recognizer = TokenRecognition()

# 现在同时支持标准名称和缩写！
address1 = await recognizer.get_token_address(session, "UNI", "ethereum")
address2 = await recognizer.get_token_address(session, "UNI", "eth")
# address1 == address2  ✅

token1 = await recognizer.get_token_by_address(session, "ethereum", "0x...")
token2 = await recognizer.get_token_by_address(session, "eth", "0x...")
# token1 == token2  ✅
```

### 4. Aliases 合并逻辑

**aliases.json**:
```json
{
  "canonical": "BTC",
  "aliases": ["MEZO WRAPPED BTC", "MEZO BTC"]
}
```

**tokens.json** (原始):
```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "aliases": []
}
```

**合并后导入到数据库**:
```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "aliases": ["MEZO WRAPPED BTC", "MEZO BTC"]
}
```

---

## 🧪 导入后验证

### 1. 检查数据库

```sql
-- 总代币数
SELECT COUNT(*) FROM "Token";
-- 预期: 1000

-- 主网代币
SELECT symbol, name, chain, token_address
FROM "Token"
WHERE chain = ''
LIMIT 10;
-- 预期: BTC (bitcoin), ETH (ethereum), etc.

-- 跨链代币（USDT）
SELECT
  symbol,
  name,
  chain as primary_chain,
  token_address as primary_address,
  platforms
FROM "Token"
WHERE symbol = 'USDT';

-- 检查别名
SELECT symbol, name, aliases
FROM "Token"
WHERE jsonb_array_length(aliases) > 0
LIMIT 10;
-- 预期: 797个代币有别名

-- 各链代币数量统计
SELECT chain, COUNT(*) as count
FROM "Token"
WHERE chain != ''
GROUP BY chain
ORDER BY count DESC;
```

### 2. 运行测试脚本

```bash
# 测试 TokenRecognition 模块
python scripts/test_token_recognition.py

# 运行完整测试套件
python scripts/run_all_tests.py
```

### 3. 使用 TokenRecognition

```python
from prisma_web3_py import get_db
from prisma_web3_py.utils import TokenRecognition

recognizer = TokenRecognition()

async with get_db() as session:
    # 测试文本识别
    text = "I bought $BTC and USDT"
    tokens = await recognizer.recognize_from_text(session, text)
    assert len(tokens) == 2  # BTC and USDT

    # 测试别名匹配
    token = await recognizer.get_token_by_symbol(session, "MEZO WRAPPED BTC")
    assert token.symbol == "BTC"  # 通过别名找到 BTC

    # 测试跨链地址
    addresses = await recognizer.get_all_chain_addresses(session, "USDT")
    assert "ethereum" in addresses
    assert "tron" in addresses
    assert "solana" in addresses

    # 测试主网代币
    btc = await recognizer.get_token_by_symbol(session, "BTC")
    assert btc.is_mainnet_token() == True
    assert btc.chain == ""
    assert btc.token_address == "bitcoin"
```

---

## 🛠️ 常见问题

### Q1: 导入时出现唯一约束错误？
**A**: 已修复。主网代币现在使用 coingecko_id 作为 token_address，避免冲突。

### Q2: 如何确认 aliases 已导入？
**A**: 查询数据库：
```sql
SELECT COUNT(*) FROM "Token"
WHERE jsonb_array_length(aliases) > 0;
-- 应该返回 797
```

### Q3: 如何重新导入？
**A**: 如果需要完全重新导入：
1. 删除现有数据: `DELETE FROM "Token" WHERE coingecko_id IS NOT NULL;`
2. 重新运行导入: `python scripts/import_token_recognition_data.py`

### Q4: 如何更新代币数据?
**A**: 更新 JSON 文件后，直接重新运行导入（默认会更新已存在的代币）：
```bash
python scripts/import_token_recognition_data.py
```

### Q5: TokenRecognition 无法识别某个代币？
**A**: 检查步骤：
```python
# 1. 确认代币已导入
token = await recognizer.get_token_by_symbol(session, "SYMBOL")
if not token:
    print("Token not imported")

# 2. 检查别名
token = await recognizer.get_token_by_symbol(session, "ALIAS_NAME")

# 3. 搜索代币
results = await recognizer.search_tokens(session, "partial_name")
```

---

## 📁 核心文件说明

### 脚本文件

| 文件 | 用途 |
|------|------|
| `import_token_recognition_data.py` | **主导入脚本**（自动合并 aliases） |
| `test_import_data.py` | 数据验证（导入前） |
| `verify_consistency.py` | 一致性检查（模型、schema、脚本） |
| `test_token_recognition.py` | 功能测试（导入后） |
| `run_all_tests.py` | 完整测试套件 |

### 核心模块

| 模块 | 说明 |
|------|------|
| `prisma_web3_py/utils/token_importer.py` | TokenImporter 类 |
| `prisma_web3_py/utils/token_recognition.py` | TokenRecognition 类 |
| `prisma_web3_py/models/token.py` | Token 模型 |
| `prisma_web3_py/repositories/token_repository.py` | Token 仓储 |

### 文档文件

| 文档 | 内容 |
|------|------|
| `IMPORT_GUIDE.md` | **本文档** - 完整导入指南 |
| `docs/SIMPLIFIED_TOKEN_DESIGN.md` | 设计文档 |
| `docs/TOKEN_REFACTOR_IMPLEMENTATION.md` | 实现细节 |
| `prisma_web3_py/utils/README.md` | Utils 模块文档 |
| `token_recognition/IMPORT_GUIDE.md` | 详细技术说明 |

---

## ⚡ 快速开始

### 最简单的导入流程

```bash
# 1. 切换到 python 目录
cd /Users/qinghuan/Documents/code/prisma-web3/python

# 2. （可选）验证一切就绪
python scripts/verify_consistency.py

# 3. 执行导入
python scripts/import_token_recognition_data.py

# 4. 验证导入结果
python scripts/test_token_recognition.py

# 完成！🎉
```

### 验证导入成功

```sql
-- 连接数据库
psql $DATABASE_URL

-- 快速检查
SELECT
  COUNT(*) as total_tokens,
  COUNT(*) FILTER (WHERE chain = '') as mainnet_tokens,
  COUNT(*) FILTER (WHERE jsonb_array_length(aliases) > 0) as tokens_with_aliases
FROM "Token";

-- 预期结果:
-- total_tokens: 1000
-- mainnet_tokens: 111
-- tokens_with_aliases: 797
```

---

## 🎯 下一步

导入成功后：

1. ✅ **数据已持久化**: 1000个代币在数据库中
2. ✅ **使用 TokenRecognition**: 从数据库查询，不再需要 JSON 文件
3. ✅ **支持别名搜索**: 797个代币可通过别名查找
4. ✅ **跨链地址查询**: 支持查询代币在不同链上的地址

### 在应用中使用

```python
from prisma_web3_py.utils import TokenRecognition

recognizer = TokenRecognition()

# 识别用户消息中的代币
user_message = "Just bought some $BTC and USDT!"
tokens = await recognizer.recognize_from_text(session, user_message)

# 获取代币地址
uni_eth = await recognizer.get_token_address(session, "UNI", "ethereum")
uni_polygon = await recognizer.get_token_address(session, "UNI", "polygon")

# 搜索代币
results = await recognizer.search_tokens(session, "uniswap", limit=10)
```

---

## 📞 需要帮助？

- 📖 查看 `docs/TOKEN_REFACTOR_IMPLEMENTATION.md` 了解技术细节
- 🔧 运行 `python scripts/verify_consistency.py` 检查系统状态
- 🧪 运行 `python scripts/test_import_data.py` 验证数据有效性
- 💬 查看脚本输出的详细日志定位问题

---

**准备就绪！运行导入命令开始吧！** 🚀

```bash
python scripts/import_token_recognition_data.py
```
