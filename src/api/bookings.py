from fastapi.exceptions import HTTPException  # noqa: F401
from fastapi import APIRouter, Body
from src.schemas.bookings import BookingAddRequest, BookingAdd, BookingBulkRequest
from src.api.dependencies import DBDep, UserDep
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/")
async def get_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me")
async def get_my_booking(db: DBDep, user_id: UserDep):
    return await db.bookings.get_filtered(user_id=user_id)


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
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    hotel_id = room.hotel_id
    price: int = room.price
    booking = await db.bookings.add(
        BookingAdd(
            **booking_data.model_dump(),
            hotel_id=hotel_id,
            user_id=user_id,
            price=price,
        )
    )
    await db.commit()
    return {"status": "OK", "data": booking}


@router.post("/bulk")
async def create_bookings_bulk(db: DBDep, bookings_data: list[BookingBulkRequest]):
    valid_user_ids = {u.id for u in await db.users.get_all()}
    valid_hotel_ids = {h.id for h in await db.hotels.get_filtered()}
    valid_room_ids = {r.id for r in await db.rooms.get_all()}

    valid = [
        BookingAdd(**b.model_dump())
        for b in bookings_data
        if b.user_id in valid_user_ids
        and b.hotel_id in valid_hotel_ids
        and b.room_id in valid_room_ids
    ]

    if valid:
        await db.bookings.add_bulk(valid)
        await db.commit()

    return {"inserted": len(valid), "skipped": len(bookings_data) - len(valid)}


@router.get("/timeline", response_class=HTMLResponse)
async def bookings_timeline(db: DBDep):
    """
    Visual timeline of all bookings.
    Open in browser: http://localhost:8000/bookings/timeline
    """
    bookings = await db.bookings.get_all()

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
    groups_js = ",".join(
        [f'{{id: {rid}, content: "Room {rid}"}}' for rid in room_ids[:50]]
    )

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
