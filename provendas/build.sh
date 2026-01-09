#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala as dependências
pip install -r requirements.txt

# Coleta os arquivos estáticos (CSS, Imagens do AdminLTE) para o WhiteNoise servir
python manage.py collectstatic --no-input

# Aplica as migrações no banco de dados da nuvem
python manage.py migrate

# Cria um superusuário padrão se não existir (opcional, remova se preferir criar manualmente)
# python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None"