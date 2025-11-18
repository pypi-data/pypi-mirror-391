"""
Cleanup script to remove test data from the database.
Use this to clean up data from failed test runs.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma_web3_py import get_db, init_db, close_db
from sqlalchemy import text


async def cleanup_test_data():
    """Remove all test data from database."""

    print("\n" + "="*60)
    print("Cleanup Test Data")
    print("="*60)

    await init_db()

    try:
        async with get_db() as session:
            # Delete test signals
            print("\n[1] Deleting test signals...")
            result = await session.execute(
                text("""
                    DELETE FROM "Signal"
                    WHERE token_address LIKE '0xTEST%'
                    OR token_address LIKE '0xtest%'
                """)
            )
            signal_count = result.rowcount
            print(f"✓ Deleted {signal_count} test signals")

            # Delete test pre-signals
            print("\n[2] Deleting test pre-signals...")
            result = await session.execute(
                text("""
                    DELETE FROM "PreSignal"
                    WHERE token_address LIKE '0xTEST%'
                    OR token_address LIKE '0xtest%'
                """)
            )
            pre_signal_count = result.rowcount
            print(f"✓ Deleted {pre_signal_count} test pre-signals")

            # Delete test tokens
            print("\n[3] Deleting test tokens...")
            result = await session.execute(
                text("""
                    DELETE FROM "Token"
                    WHERE token_address LIKE '0xTEST%'
                    OR token_address LIKE '0xtest%'
                    OR symbol IN ('TEST', 'TSIG', 'TPRE')
                """)
            )
            token_count = result.rowcount
            print(f"✓ Deleted {token_count} test tokens")

            # Commit all deletions
            await session.commit()

            print("\n" + "="*60)
            print("✓ Cleanup completed successfully!")
            print(f"  Total items removed: {signal_count + pre_signal_count + token_count}")
            print("="*60)
            return True

    except Exception as e:
        print(f"\n✗ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_db()


if __name__ == "__main__":
    success = asyncio.run(cleanup_test_data())
    sys.exit(0 if success else 1)
