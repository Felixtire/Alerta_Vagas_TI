import asyncio

import requests
import os
import smtplib
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import telegram

# Load environment variables
load_dotenv()

# Configuration
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_TO = os.getenv('EMAIL_TO')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
JOB_KEYWORDS = os.getenv('JOB_KEYWORDS', 'TI,JOVEM APRENDIZ TI,ESTÁGIO TI,PROFESSOR/MONITOR DE INFORMÁTICA').split(',')
LOCATION = os.getenv('LOCATION', 'Brasília,DF')
RADIUS = int(os.getenv('RADIUS', 10))
MAX_AGE = int(os.getenv('MAX_AGE', 7))



# File to store seen job IDs to avoid duplicates
SEEN_JOBS_FILE = 'seen_jobs.json'

def load_seen_jobs():
    """Load previously seen job IDs from file"""
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_jobs(seen_jobs):
    """Save seen job IDs to file"""
    with open(SEEN_JOBS_FILE, 'w') as f:
        json.dump(list(seen_jobs), f)

def fetch_jobs():
    """Fetch jobs from Adzuna API"""
    all_jobs = []
    
    for keyword in JOB_KEYWORDS:
        url = f"https://api.adzuna.com/v1/api/jobs/br/search/1"
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'what': keyword.strip(),
            'where': LOCATION,
            'distance': RADIUS,
            'max_days_old': MAX_AGE,
            'sort_by': 'date',
            'content-type': 'application/json'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data:
                for job in data['results']:
                    all_jobs.append({
                        'id': job.get('id'),
                        'title': job.get('title'),
                        'company': job.get('company', {}).get('display_name'),
                        'location': job.get('location', {}).get('display_name'),
                        'description': job.get('description', '')[:200] + '...',
                        'redirect_url': job.get('redirect_url'),
                        'created': job.get('created')
                    })
        except Exception as e:
            print(f"Error fetching jobs for keyword '{keyword}': {e}")
    
    return all_jobs

def is_new_job(job_id, seen_jobs):
    """Check if job is new"""
    return job_id not in seen_jobs

def send_email_notification(job):
    """Send email notification about a new job"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = f"Nova vaga: {job['title']}"

    body = f"""
    Nova vaga encontrada!

    Título: {job['title']}
    Empresa: {job['company']}
    Localização: {job['location']}
    Descrição: {job['description']}
    Link: {job['redirect_url']}
    Data de publicação: {job['created']}

    Este é um alerta automático do Job Alert.
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_TO, text)
        server.quit()
        print(f"Email notification sent for job: {job['title']}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_telegram_notification(job):
    """Send Telegram notification about a new job"""
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        
        message = f"""Nova vaga de TI em Brasília!

{job['title']}
{job['company']}
{job['location']}

{job['description']}

Mais info: {job['redirect_url']}"""
        
        async def send_message():
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        
        asyncio.run(send_message())
        print(f"Telegram notification sent for job: {job['title']}")
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def send_telegram_no_jobs_notification():
    """Send Telegram notification when no new jobs are found"""
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        message = "Verificação concluída: nenhuma nova vaga encontrada neste período."
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(f"Telegram notification sent: no new jobs")
        return True
    except Exception as e:
        print(f"Error sending Telegram no-jobs message: {e}")
        return False

def main():
    """Main function to run the job alert system"""
    print("Iniciando Job Alert...")
    
    # Load seen jobs
    seen_jobs = load_seen_jobs()
    print(f"Carregados {len(seen_jobs)} trabalhos já vistos")
    
    # Fetch current jobs
    jobs = fetch_jobs()
    print(f"Encontrados {len(jobs)} trabalhos no total")
    
    new_jobs_count = 0
    
    # Process each job
    for job in jobs:
        if job['id'] and is_new_job(job['id'], seen_jobs):
            print(f"Nova vaga encontrada: {job['title']}")
            
            # Send notifications
            email_sent = send_email_notification(job)
            telegram_sent = send_telegram_notification(job)
            
            if email_sent or telegram_sent:
                seen_jobs.add(job['id'])
                new_jobs_count += 1
    
    # Save updated seen jobs
    save_seen_jobs(seen_jobs)
    
    print(f"Processo concluído. {new_jobs_count} novas vagas encontradas e notificadas.")
    if new_jobs_count == 0:
        send_telegram_no_jobs_notification()

if __name__ == "__main__":
    main()