import pandas as pd
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import psutil
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def fetch_updates_from_api(api_url):
    response = requests.get(api_url)
    updates = pd.DataFrame(response.json())
    return updates

def update_catalog(catalog_file, updates):
    catalog = pd.read_csv(catalog_file)
    updated_catalog = pd.concat([catalog, updates]).drop_duplicates(subset=['id'], keep='last')
    updated_catalog.to_csv(catalog_file, index=False)
    return updated_catalog

def generate_pdf(catalog, pdf_file):
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    y = height - 30

    for index, row in catalog.iterrows():
        c.drawString(30, y, f"{row['id']}: {row['name']} - {row['description']}")
        y -= 20
        if y < 30:
            c.showPage()
            y = height - 30

    c.save()

def send_email(to_address, subject, body, attachment):
    from_address = "your_email@example.com"
    password = "your_password"

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment, "rb") as attachment_file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {attachment}")
        msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_address, password)
        server.sendmail(from_address, to_address, msg.as_string())

def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_info.percent,
        "disk_usage": disk_usage.percent
    }

def log_metrics():
    while True:
        metrics = get_system_metrics()
        with open('system_health.log', 'a') as log_file:
            log_file.write(f"CPU Usage: {metrics['cpu_usage']}%, Memory Usage: {metrics['memory_usage']}%, Disk Usage: {metrics['disk_usage']}%\n")
        time.sleep(60)

if __name__ == "__main__":
    # Step 1: Fetch updates from API and update the catalog
    api_url = 'https://api.example.com/updates'
    updates = fetch_updates_from_api(api_url)
    catalog_file = 'catalog.csv'
    updated_catalog = update_catalog(catalog_file, updates)
    
    # Step 2: Generate the PDF report
    pdf_file = 'catalog.pdf'
    generate_pdf(updated_catalog, pdf_file)
    
    # Step 3: Send the email with the PDF attached
    send_email("recipient@example.com", "Updated Catalog", "Please find the updated catalog attached.", pdf_file)
    
    # Step 4: Start logging system health metrics
    log_metrics()
