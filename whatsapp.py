from fastapi import FastAPI, BackgroundTasks
from twilio.rest import Client
import requests
import json
import schedule
import time
import threading

app = FastAPI()

# Twilio Credentials
account_sid = "ACd19fd2ff9d8f453a8ee18185ae6eeeba"
auth_token = "ffae13ffb6ff5787cbf323f7dfa4542d"
client = Client(account_sid, auth_token)

# Supabase Credentials
SUPABASE_URL = "https://nizvcdssajfpjtncbojx.supabase.co/rest/v1"
HEADERS = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

PORTAL_URL = "www.ishanya_if.com"
CONTACT_EMAIL = "feedback@ishanya_if.com"

def fetch_students():
    response = requests.get(f"{SUPABASE_URL}/students?select=*", headers=HEADERS)
    return {s["student_id"]: s for s in response.json()} if response.ok else {}

def fetch_reports(endpoint):
    response = requests.get(f"{SUPABASE_URL}/{endpoint}?select=*", headers=HEADERS)
    return response.json() if response.ok else []

def send_whatsapp_message(contact_number, content_sid, content_variables):
    if contact_number:
        print(f"Sending message to: {contact_number}")
        client.messages.create(
            from_="whatsapp:+14155238886",
            to=f"whatsapp:+91{contact_number}",
            content_sid=content_sid,
            content_variables=json.dumps(content_variables),
        )

def mark_report_as_sent(report_id, endpoint):
    requests.patch(
        f"{SUPABASE_URL}/{endpoint}",
        params={"id": f"eq.{report_id}"},
        headers=HEADERS,
        json={"is_sent": True},
    )

def send_notifications():
    students = fetch_students()
    general_reports = fetch_reports("general_reporting")
    performance_records = fetch_reports("performance_records")

    for report in general_reports:
        if not report["is_sent"]:
            student = students.get(report["student_id"], {})
            send_whatsapp_message(
                student.get("contact_number"),
                "HX895190623c17969cf9d312f3cc1e8032",
                {"1": student.get("first_name", "") + " " + student.get("last_name", ""),
                 "2": report["quarter"],
                 "3": PORTAL_URL, "4": CONTACT_EMAIL},
            )
            mark_report_as_sent(report["id"], "general_reporting")

    for report in performance_records:
        if not report["is_sent"]:
            student = students.get(report["student_id"], {})
            send_whatsapp_message(
                student.get("contact_number"),
                "HX4e1ad86b20b3e67748521409301fb221",
                {"1": student.get("first_name", "") + " " + student.get("last_name", ""),
                 "2": report["quarter"],
                 "3": PORTAL_URL, "4": CONTACT_EMAIL},
            )
            mark_report_as_sent(report["id"], "performance_records")

def send_weekly_reminders():
    students = fetch_students()
    for student in students.values():
        if student["contact_number"] == "9818851259":  # Limiting due to Twilio free tier
            send_whatsapp_message(
                student["contact_number"],
                "HX697007461b8ab833db277340a2cc03c9",
                {"1": student["first_name"] + " " + student["last_name"],
                 "2": "Samiddhi", "3": PORTAL_URL, "4": CONTACT_EMAIL},
            )

def scheduler_thread():
    schedule.every(5).minutes.do(send_notifications)
    schedule.every().sunday.at("10:00").do(send_weekly_reminders)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in a separate thread
threading.Thread(target=scheduler_thread, daemon=True).start()

@app.get("/send_notifications")
def trigger_notifications(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_notifications)
    return {"message": "Notifications are being sent in the background."}

@app.get("/send_weekly_reminders")
def trigger_weekly_reminders(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_weekly_reminders)
    return {"message": "Weekly reminders are being sent in the background."}
