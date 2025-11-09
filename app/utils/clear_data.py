"""
Clear All Table Data (Keep Structure)
--------------------------------------
⚠️ WARNING: This will delete ALL data from all tables.
Tables and structure will remain intact.

Usage:
    $ python -m app.utils.clear_data
    OR
    $ python app/utils/clear_data.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from app.core.database import Base, engine
from app.models import (ActivityLog, AIRecommendation, Comment, Concept,
                        LearningConcept, Notification, Project, ProjectMember,
                        RefreshToken, Roadmap, RoadmapStep, StudySession, Task,
                        User, UserProgress)


def clear_all_tables():
    """
    Truncate all tables while preserving their structure.
    Uses CASCADE to handle foreign key constraints.
    """
    print("🗑️  Clearing all table data...")

    # Get all table names from metadata
    tables = list(Base.metadata.tables.keys())

    if not tables:
        print("❌ No tables found in metadata.")
        return

    print(f"📋 Found {len(tables)} tables to clear:")
    for table in sorted(tables):
        print(f"   - {table}")

    # Use raw SQL to truncate all tables with CASCADE
    # This handles foreign key constraints automatically
    with engine.begin() as conn:  # begin() auto-commits
        # For PostgreSQL: disable triggers temporarily to avoid FK issues
        try:
            conn.execute(text("SET session_replication_role = 'replica';"))
        except Exception:
            # Not PostgreSQL or feature not available, continue anyway
            pass

        # Truncate all tables in one command (PostgreSQL supports this)
        try:
            # Try truncating all at once (PostgreSQL)
            table_list = ", ".join(f'"{table}"' for table in tables)
            conn.execute(text(f"TRUNCATE TABLE {table_list} CASCADE;"))
            print(f"   ✅ Cleared all {len(tables)} tables")
        except Exception:
            # Fallback: truncate one by one
            print("   ⚠️  Truncating tables individually...")
            for table in tables:
                try:
                    conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
                    print(f"   ✅ Cleared: {table}")
                except Exception as e:
                    print(f"   ⚠️  Error clearing {table}: {e}")

        # Re-enable triggers
        try:
            conn.execute(text("SET session_replication_role = 'origin';"))
        except Exception:
            pass

    # Reset sequences (for auto-increment IDs if any)
    # PostgreSQL sequences are usually UUID-based, but reset anyway
    with engine.connect() as conn:
        try:
            # Get all sequences (PostgreSQL specific)
            result = conn.execute(
                text(
                    """
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
            """
                )
            )
            sequences = [row[0] for row in result]

            if sequences:
                print(f"\n🔄 Resetting {len(sequences)} sequences...")
                with conn.begin():
                    for seq in sequences:
                        try:
                            conn.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1;"))
                        except Exception:
                            # Some sequences might not be resettable, that's okay
                            pass
        except Exception:
            # Sequences might not exist or be relevant, that's fine
            pass

    print("\n✅ All table data cleared successfully!")
    print("📊 Tables are empty but structure is intact.")


if __name__ == "__main__":
    print("\n🚨 CLEARING ALL TABLE DATA 🚨")
    print("⚠️  This will delete ALL data but keep table structure.\n")

    confirm = input("Type 'CLEAR' to continue: ")
    if confirm.strip().upper() == "CLEAR":
        clear_all_tables()
        print("\n🎯 Ready to repopulate with new data!\n")
    else:
        print("❌ Cancelled — no changes made.")
