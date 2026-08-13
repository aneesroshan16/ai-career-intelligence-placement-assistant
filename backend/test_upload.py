import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.modules.resumes.service import ResumeService
from app.modules.users.models import User, StudentProfile  # noqa: F401

async def main():
    async with AsyncSessionLocal() as db:
        service = ResumeService(db)
        res = await db.execute(text("SELECT id FROM users LIMIT 1"))
        row = res.fetchone()
        if not row:
            print("No users in db")
            return
        user_id = str(row[0])
        try:
            print("Uploading and processing real resume...")
            file_path = "data/uploads/13446ce4719d4d198db3174f079f28d2_RESUME_SYED_ANEES_ROSHAN (1).pdf"
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            parsed = await service.upload_and_process(
                user_id=user_id,
                filename="RESUME_SYED_ANEES_ROSHAN.pdf",
                content_type="application/pdf",
                file_bytes=file_bytes
            )
            print("SUCCESS! Parsed data:")
            print(parsed)
        except Exception as e:
            print("FAILED:", e)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
