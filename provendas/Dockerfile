# Usa Python 3.11 (versão estável compatível com seu código)
FROM python:3.11-slim

# Evita arquivos .pyc e buffer de logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para PostgreSQL e outros pacotes
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do projeto
COPY . .

# Coleta os arquivos estáticos (CSS/JS) para o Whitenoise servir
RUN python manage.py collectstatic --noinput

# Expõe a porta 8080 (padrão do Cloud Run)
EXPOSE 8080

# Comando para iniciar o servidor Gunicorn
# Substitua 'provendas.wsgi:application' se o nome da pasta principal não for 'provendas'
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "provendas.wsgi:application"]