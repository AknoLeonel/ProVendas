#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# --- COMANDO MÁGICO PARA CRIAR ADMIN ---
# Cria um superusuário 'admin' com senha 'admin123' se não existir
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@exemplo.com', 'admin123')"