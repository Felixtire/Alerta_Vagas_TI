# Job Alert TI

Este projeto verifica periodicamente vagas de TI em Brasília usando a API da Adzuna e envia notificações por e-mail e Telegram.

## Funcionalidades
- Busca vagas de TI com palavras-chave definidas
- Evita duplicatas usando arquivo seen_jobs.json
- Envia notificações por e-mail (SMTP)
- Envia notificações por Telegram (bot)
- Agendamento automático a cada 3 horas via cron job do Hermes
- Notifica quando nenhuma nova vaga é encontrada

## Configuração
1. Copie `.env.example` para `.env` e preencha com suas credenciais reais:
   - ADZUNA_APP_ID e ADZUNA_APP_KEY (https://developer.adzuna.com/)
   - EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_TO
   - TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute manualmente: `python job_alert/main.py`
4. O cron job já está configurado para rodar a cada 3 horas.

## Dependências
- requests
- python-dotenv
- python-telegram-bot

## Aviso de segurança
O arquivo `.env` contém credenciais sensíveis e está listado no `.gitignore`. Nunca o commitre no repositório.

