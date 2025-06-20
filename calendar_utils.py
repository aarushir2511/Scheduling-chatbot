from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Google API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = "primary"  # Don't change if using your main calendar

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=creds)
    return service

def get_free_slots(duration_minutes=60, days=7):
    service = get_calendar_service()

    now = datetime.utcnow()
    end_time = now + timedelta(days=days)

    print(f"📆 Checking for free slots between {now} and {end_time}...")

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    print("📅 DEBUG: Events fetched from calendar:")
    for e in events:
        start_time = e["start"].get("dateTime", e["start"].get("date", "Unknown"))
        end_time = e["end"].get("dateTime", e["end"].get("date", "Unknown"))
        print(f"  🔸 {e.get('summary', 'No title')} | {start_time} → {end_time}")

    busy_times = []
    for event in events:
        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        if start and end:
            busy_times.append((datetime.fromisoformat(start), datetime.fromisoformat(end)))

    free_slots = []
    current_start = now

    for start, end in busy_times:
        print("⏳ DEBUG: Busy from", start, "to", end)
        if current_start + timedelta(minutes=duration_minutes) <= start:
            free_slots.append(current_start)
            print("✅ FREE SLOT FOUND:", current_start)
        current_start = max(current_start, end)

    # Catch time after last event
    if current_start + timedelta(minutes=duration_minutes) <= end_time:
        free_slots.append(current_start)
        print("✅ FREE SLOT FOUND (after last event):", current_start)

    print("🧠 Total free slots found:", len(free_slots))
    return free_slots

def create_event(start_time, duration_minutes=60, summary="Scheduled Meeting"):
    service = get_calendar_service()
    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"✅ Event created: {event_result.get('htmlLink')}")
