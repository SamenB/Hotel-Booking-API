# src/tasks/tasks.py
from PIL import Image
from pathlib import Path
from src.tasks.celery_app import celery_instance
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import update
from src.models.hotels import HotelsOrm
from src.config import settings
import asyncio


def run_async(coro):
    """Safely run async code in sync Celery task"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_instance.task
def process_hotel_image(hotel_id: int, temp_file_path: str):
    file_path = Path(temp_file_path)
    output_dir = Path("static/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with Image.open(file_path) as img:
            # Save original version in WebP format
            original_name = f"{hotel_id}_original.webp"
            img.save(output_dir / original_name, format="WEBP")
            
            # Create and save a thumbnail (400x400)
            img.thumbnail((400, 400))
            thumb_name = f"{hotel_id}_thumb.webp"
            img.save(output_dir / thumb_name, format="WEBP")

        # Update the database with new image paths
        async def update_db():
            engine = create_async_engine(settings.DB_URL)
            async_session = async_sessionmaker(engine, expire_on_commit=False)
            
            async with async_session() as session:
                image_urls = [
                    f"/static/images/{original_name}", 
                    f"/static/images/{thumb_name}"
                ]
                stmt = (
                    update(HotelsOrm)
                    .where(HotelsOrm.id == hotel_id)
                    .values(images=image_urls)
                )
                await session.execute(stmt)
                await session.commit()
                
            await engine.dispose()
        
        run_async(update_db())
    
    finally:
        file_path.unlink(missing_ok=True)