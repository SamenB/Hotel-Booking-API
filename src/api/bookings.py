from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import APIRouter, Body
from src.schemas.bookings import BookingAddRequest, BookingBulkRequest
from src.api.dependencies import DBDep, UserDep
from fastapi.responses import HTMLResponse
from src.exeptions import (
    ObjectNotFoundException,
    AllRoomsAreBookedException,
    ObjectAlreadyExistsException,
    DatabaseException,
)
from src.services.bookings import BookingService
from loguru import logger


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/")
async def get_bookings(db: DBDep):
    try:
        return await BookingService(db).get_all_bookings()
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/me")
async def get_my_booking(db: DBDep, user_id: UserDep):
    try:
        return await BookingService(db).get_my_bookings(user_id)
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.post("")
async def create_booking(
    user_id: UserDep,
    db: DBDep,
    booking_data: BookingAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Luxury",
                "value": {
                    "room_id": 4,
                    "check_in_date": "2025-12-19",
                    "check_out_date": "2025-12-20",
                },
            },
            "2": {
                "summary": "Standard",
                "value": {
                    "room_id": 4,
                    "check_in_date": "2025-12-20",
                    "check_out_date": "2025-12-21",
                },
            },
        }
    ),
):
    try:
        booking = await BookingService(db).create_booking(booking_data, user_id)
    except ObjectNotFoundException:
        logger.warning("Room not found: room_id={}", booking_data.room_id)
        raise HTTPException(status_code=400, detail="Room not found")
    except AllRoomsAreBookedException:
        logger.warning(
            "All rooms booked: room_id={}, dates={}-{}",
            booking_data.room_id,
            booking_data.check_in_date,
            booking_data.check_out_date,
        )
        raise HTTPException(status_code=409, detail="All rooms are booked")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return {"status": "OK", "data": booking}


@router.post("/bulk")
async def create_bookings_bulk(db: DBDep, bookings_data: list[BookingBulkRequest]):
    try:
        result = await BookingService(db).create_bookings_bulk(bookings_data)
    except ObjectAlreadyExistsException:
        raise HTTPException(status_code=409, detail="One or more bookings already exist")
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    return result


@router.get("/timeline", response_class=HTMLResponse)
async def bookings_timeline(db: DBDep):
    """
    Visual timeline of all bookings.
    Open in browser: http://localhost:8000/bookings/timeline
    """
    try:
        bookings = await BookingService(db).get_bookings_timeline()
    except DatabaseException:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    items_js = ",".join(
        [
            f'''{{
            id: {b.id},
            content: "Room {b.room_id}",
            start: "{b.check_in_date}",
            end: "{b.check_out_date}",
            group: {b.room_id},
            title: "User: {b.user_id}, Hotel: {b.hotel_id}, Price: {b.price}"
        }}'''
            for b in bookings
        ]
    )

    room_ids = sorted(set(b.room_id for b in bookings))
    groups_js = ",".join([f'{{id: {rid}, content: "Room {rid}"}}' for rid in room_ids[:50]])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bookings Timeline</title>
        <script src="https://unpkg.com/vis-timeline@7.7.3/standalone/umd/vis-timeline-graph2d.min.js"></script>
        <link href="https://unpkg.com/vis-timeline@7.7.3/styles/vis-timeline-graph2d.min.css" rel="stylesheet" />
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
            h1 {{ color: #00d4ff; margin-bottom: 20px; }}
            #timeline {{ background: #16213e; border-radius: 10px; }}
            .vis-item {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 6px; color: white; }}
            .vis-item.vis-selected {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
            .stats {{ margin-bottom: 20px; padding: 15px; background: #16213e; border-radius: 10px; display: flex; gap: 30px; }}
            .stat {{ text-align: center; }}
            .stat-value {{ font-size: 2em; color: #00d4ff; font-weight: bold; }}
            .stat-label {{ color: #888; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>🗓️ Bookings Timeline</h1>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(bookings)}</div>
                <div class="stat-label">Total Bookings</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(room_ids)}</div>
                <div class="stat-label">Rooms</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(set(b.user_id for b in bookings))}</div>
                <div class="stat-label">Users</div>
            </div>
        </div>
        <div id="timeline"></div>
        <script>
            var items = new vis.DataSet([{items_js}]);
            var groups = new vis.DataSet([{groups_js}]);
            var container = document.getElementById('timeline');
            var options = {{
                stack: true,
                showCurrentTime: true,
                zoomMin: 1000 * 60 * 60 * 24,
                zoomMax: 1000 * 60 * 60 * 24 * 365,
                orientation: 'top'
            }};
            var timeline = new vis.Timeline(container, items, groups, options);
        </script>
    </body>
    </html>
    """
    return html
