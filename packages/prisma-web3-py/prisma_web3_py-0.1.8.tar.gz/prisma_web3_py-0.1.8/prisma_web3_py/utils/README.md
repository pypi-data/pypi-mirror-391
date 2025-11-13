# Prisma Web3 Utils

Utility modules for the prisma-web3-py package.

## Modules

### 1. TokenImporter

Import tokens from CoinGecko JSON format into the database.

**Features**:
- Automatic primary chain detection
- Batch import with configurable commit size
- Update existing tokens
- Statistics tracking
- Error handling and logging

**Usage**:

```python
from prisma_web3_py import get_db
from prisma_web3_py.utils import TokenImporter

importer = TokenImporter()

async with get_db() as session:
    # Import from JSON file
    stats = await importer.import_from_json(
        session,
        "tokens.json",
        update_existing=True,
        batch_size=50
    )

    print(f"Created: {stats['created']}")
    print(f"Updated: {stats['updated']}")
    print(f"Errors: {stats['errors']}")
```

**CLI Tool**:

```bash
python scripts/import_tokens.py data/tokens.json
python scripts/import_tokens.py data/tokens.json --no-update
python scripts/import_tokens.py data/tokens.json --batch-size 100
```

**Expected JSON Format**:

```json
[
  {
    "coingecko_id": "uniswap",
    "symbol": "UNI",
    "name": "Uniswap",
    "description": "UNI is the governance token for Uniswap",
    "logo": "https://...",
    "market_cap_rank": 20,
    "platforms": {
      "ethereum": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
      "polygon": "0xb33eaad8d922b1083446dc23f610c2567fb5180f",
      "arbitrum": "0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0"
    },
    "categories": ["DeFi", "DEX"],
    "aliases": ["UNI-V2"],
    "social_links": {
      "website": "https://uniswap.org",
      "twitter": "@Uniswap",
      "telegram": "https://t.me/uniswap",
      "github": "uniswap",
      "discord": "https://discord.gg/uniswap"
    }
  }
]
```

**Primary Chain Priority**:
1. ethereum
2. binance-smart-chain
3. polygon-pos
4. solana
5. arbitrum-one
6. optimistic-ethereum
7. avalanche
8. (fallback to first chain in platforms)

**Mainnet Tokens**:
For tokens like BTC, ETH that don't have a specific chain:
```json
{
  "coingecko_id": "bitcoin",
  "symbol": "BTC",
  "name": "Bitcoin",
  "platforms": {}  // Empty platforms
}
```
These will be stored with `chain=""` and `token_address=""`.

---

### 2. TokenRecognition

Recognize token symbols from text and retrieve token information from database.

**Features**:
- Extract token symbols from text ($BTC, WETH, etc.)
- Get token address for specific chain
- Support alias matching
- In-memory caching (1-hour TTL)
- Search tokens by symbol/name
- Get all chain addresses for a token

**Usage**:

```python
from prisma_web3_py import get_db
from prisma_web3_py.utils import TokenRecognition

recognizer = TokenRecognition()

async with get_db() as session:
    # Extract tokens from text
    text = "I just bought $BTC and WETH on Uniswap"
    tokens = await recognizer.recognize_from_text(session, text)

    for token in tokens:
        print(f"{token.symbol}: {token.name}")

    # Get token address on specific chain
    uni_address = await recognizer.get_token_address(
        session,
        symbol="UNI",
        chain="ethereum"
    )
    print(f"UNI on Ethereum: {uni_address}")

    # Get all chain addresses
    all_addresses = await recognizer.get_all_chain_addresses(
        session,
        symbol="UNI"
    )
    # Returns: {"ethereum": "0x...", "polygon": "0x...", "arbitrum": "0x..."}

    # Get token by address
    token = await recognizer.get_token_by_address(
        session,
        chain="ethereum",
        address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
    )

    # Search tokens
    results = await recognizer.search_tokens(
        session,
        query="uni",
        limit=10
    )
```

**Global Instance**:

```python
from prisma_web3_py.utils import get_recognizer

recognizer = get_recognizer()  # Returns global singleton
```

**Pattern Recognition**:

The recognizer can extract tokens from various text patterns:
- `$BTC` - Dollar prefix pattern
- `BTC` - Plain symbol (with word boundaries)
- Filters out common non-token words (API, URL, CEO, etc.)

**Caching**:

By default, the recognizer caches top tokens by market cap:
```python
# Use cache (default)
tokens = await recognizer.recognize_from_text(session, text, use_cache=True)

# Bypass cache
tokens = await recognizer.recognize_from_text(session, text, use_cache=False)

# Manually invalidate cache
recognizer._invalidate_cache()
```

**Alias Matching**:

If a token has aliases in the database:
```python
# Token in DB: symbol="UNI", aliases=["UNI-V2", "Uniswap-V2"]

token = await recognizer.get_token_by_symbol(session, "UNI-V2")
# Returns the UNI token
```

---

## Testing

Run tests for the utils modules:

```bash
# Test TokenImporter (via token tests)
python scripts/test_token.py

# Test TokenRecognition
python scripts/test_token_recognition.py

# Run all tests
python scripts/run_all_tests.py
```

## Examples

See example usage in:
- `prisma_web3_py/utils/token_importer.py` (bottom of file)
- `prisma_web3_py/utils/token_recognition.py` (bottom of file)
- `scripts/import_tokens.py` (CLI tool)
- `scripts/test_token_recognition.py` (comprehensive tests)

## Dependencies

- `sqlalchemy` - Database ORM
- `asyncpg` - Async PostgreSQL driver
- `python-dotenv` - Environment configuration

All dependencies are included in the main package requirements.
