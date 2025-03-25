from twilio.rest import Client
import requests
import time
import schedule
import json

#Twilio Creds
account_sid = 'ACd19fd2ff9d8f453a8ee18185ae6eeeba'
auth_token = '1332612db25cac29cc64c166736c253b'
client = Client(account_sid, auth_token)

#SUPABASE_CREDS
url =  "https://nizvcdssajfpjtncbojx.supabase.co/rest/v1"
headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5penZjZHNzYWpmcGp0bmNib2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MTU0ODksImV4cCI6MjA1ODE5MTQ4OX0.5b2Yzfzzzz-C8S6iqhG3SinKszlgjdd4NUxogWIxCLc',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}


portal_url = "www.ishanya_if.com"
contact_email = "feedback@ishanya_if.com"

students = requests.get('https://nizvcdssajfpjtncbojx.supabase.co/rest/v1/students?select=*', headers=headers)
parents = requests.get('https://nizvcdssajfpjtncbojx.supabase.co/rest/v1/students?select=*', headers=headers)
general_reports = requests.get('https://nizvcdssajfpjtncbojx.supabase.co/rest/v1/general_reporting?select=*', headers=headers)
performance_records = requests.get('https://nizvcdssajfpjtncbojx.supabase.co/rest/v1/performance_records?select=*', headers=headers)
student_dict = {s['student_id']: s for s in students.json()}

print(general_reports.json())
def send_notifications():
  for item in general_reports.json():
    if not item['is_sent']:
      student = student_dict.get(item['student_id'], {})
      contact_number = student.get('contact_number')
      s_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
      qtr = item['quarter']

      if contact_number:
        print(f"Sending message to: {contact_number}")

        message = client.messages.create(
          from_='whatsapp:+14155238886',  
          to=f'whatsapp:+91{contact_number}',    
          content_sid='HX895190623c17969cf9d312f3cc1e8032',  
          content_variables= json.dumps({'1':s_name,'2':qtr,'3':portal_url,'4':contact_email})
        )
        
        params = {
            'id': f"eq.{item['id']}",
        }

        json_data = {
            'is_sent': True,
        }

        response = requests.patch(
            'https://nizvcdssajfpjtncbojx.supabase.co/rest/v1/general_reporting',
            params=params,
            headers=headers,
            json=json_data,
        )
          
  
  for item in performance_records.json():
    if not item['is_sent']:
      contact_number = student_dict.get(1, {}).get('contact_number')
      f_name = student_dict.get(1, {}).get('first_name')
      l_name = student_dict.get(1, {}).get('last_name')
      s_name = f"{f_name} {l_name}"
      qtr = item['quarter']
      
      
      if contact_number:
        print(f"Sending message to: {contact_number}")
        
        message = client.messages.create(
        from_='whatsapp:+14155238886',  
        to=f'whatsapp:+91{contact_number}',    
        content_sid='HX4e1ad86b20b3e67748521409301fb221',  
        content_variables= json.dumps({1:s_name,2:qtr,3:portal_url,4:contact_email})
        )
        
        params = {
            'id': f"eq.{item['id']}",
        }

        json_data = {
            'is_sent': True,
        }

        response = requests.patch(
            'https://nizvcdssajfpjtncbojx.supabase.co/rest/v1/general_reporting',
            params=params,
            headers=headers,
            json=json_data,
        )
      


def send_weekly_reminders():
  for item in students.json(): 
    #CHECK SINCE FREE TWILIO 
    if item['contact_number'] == "9818851259":
      message = client.messages.create(
        from_='whatsapp:+14155238886',  
        to=f'whatsapp:+91{item['contact_number']}',    
        content_sid='HX697007461b8ab833db277340a2cc03c9',  
        content_variables= json.dumps({1:f"{item['first_name']} {item['last_name']}",2:"Samiddhi",3:portal_url,4:contact_email})
      )


send_notifications()


schedule.every(5).minutes.do(send_notifications)
schedule.every().sunday.at("10:00").do(send_weekly_reminders) 
print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(60)