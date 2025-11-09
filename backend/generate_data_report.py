
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from datetime import datetime

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user import User
from app.models.post import Post
from app.models.claim import Claim
from app.models.category import Category
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.rating import Rating

# It's better to use the config for the database URL
# from app.config import settings
# DATABASE_URL = settings.ASYNC_DATABASE_URL
DATABASE_URL = "sqlite+aiosqlite:///../lostandfound.db"

async def generate_report():
    """
    Connects to the database, counts records in each table, and generates a report.
    """
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with AsyncSession(engine) as session:
        report_lines = [f"Database Data Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
        total_records = 0

        models_to_check = {
            "Users": User,
            "Posts": Post,
            "Claims": Claim,
            "Categories": Category,
            "Comments": Comment,
            "Notifications": Notification,
            "Ratings": Rating,
        }

        for name, model in models_to_check.items():
            try:
                result = await session.execute(select(model))
                count = len(result.scalars().all())
                report_lines.append(f"- {name}: {count} records")
                total_records += count
            except Exception as e:
                report_lines.append(f"- {name}: Error counting records - {e}")

        report_lines.append(f"\nTotal records across all tables: {total_records}")

        report_content = "\n".join(report_lines)
        print(report_content)

        # Save the report to a file
        with open("../DATA_ANALYSIS_REPORT.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print("\nReport saved to DATA_ANALYSIS_REPORT.md")
        
        return total_records

async def main():
    """
    Main function to run the report generation.
    """
    await generate_report()

if __name__ == "__main__":
    asyncio.run(main())
