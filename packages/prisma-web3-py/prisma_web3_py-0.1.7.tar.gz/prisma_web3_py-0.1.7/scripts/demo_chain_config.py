"""
Demo script showing ChainConfig usage.

Quick demonstration of chain abbreviation and conversion features.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prisma_web3_py.utils import ChainConfig, Chain, abbr, standard, display


def main():
    print("\n" + "="*60)
    print("CHAIN CONFIGURATION DEMO")
    print("="*60)

    # Demo 1: Basic conversions
    print("\n📝 Demo 1: Basic Conversions")
    print("-" * 60)
    print(f"  ethereum -> {abbr('ethereum')}")
    print(f"  bsc -> {standard('bsc')}")
    print(f"  eth -> {display('eth')}")

    # Demo 2: Using constants
    print("\n📝 Demo 2: Using Chain Constants")
    print("-" * 60)
    print(f"  Chain.ETH = {Chain.ETH}")
    print(f"  Chain.BSC = {Chain.BSC}")
    print(f"  Chain.ETHEREUM = {Chain.ETHEREUM}")

    # Demo 3: Priority sorting
    print("\n📝 Demo 3: Chain Priority Ordering")
    print("-" * 60)
    chains = ["solana", "ethereum", "polygon-pos", "arbitrum-one"]
    sorted_chains = sorted(chains, key=ChainConfig.get_priority)
    for i, chain in enumerate(sorted_chains, 1):
        priority = ChainConfig.get_priority(chain)
        print(f"  {i}. {chain:20} (priority: {priority}) -> {abbr(chain)}")

    # Demo 4: All supported chains
    print("\n📝 Demo 4: Supported Chains (Top 10)")
    print("-" * 60)
    all_chains = ChainConfig.get_all_chains()[:10]
    for i, chain in enumerate(all_chains, 1):
        print(f"  {i:2}. {chain:25} ({abbr(chain):5}) - {display(chain)}")

    # Demo 5: Bidirectional conversion
    print("\n📝 Demo 5: Bidirectional Conversion")
    print("-" * 60)
    test_cases = [
        ("eth", "ethereum"),
        ("bsc", "binance-smart-chain"),
        ("sol", "solana"),
    ]
    for abbr_input, expected_standard in test_cases:
        result = ChainConfig.get_standard_name(abbr_input)
        back = ChainConfig.get_abbreviation(result)
        status = "✅" if result == expected_standard and back == abbr_input else "❌"
        print(f"  {status} {abbr_input} <-> {result} <-> {back}")

    print("\n" + "="*60)
    print("✅ Demo completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
