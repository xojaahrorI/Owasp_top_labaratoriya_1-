#!/usr/bin/env bash
# NestMarket - Linux uchun bitta buyruq bilan o'rnatish va ishga tushirish.
#
# Ishlatish:
#   chmod +x start.sh
#   ./start.sh
#
# Bu skript: virtualenv yaratadi (agar yo'q bo'lsa), kerakli paketlarni
# o'rnatadi, migratsiyalarni bajaradi, boshlang'ich ma'lumotlarni yuklaydi
# (agar hali yuklanmagan bo'lsa) va serverni ishga tushiradi.

set -e

cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="venv"
HOST="${NESTMARKET_HOST:-127.0.0.1}"
PORT="${NESTMARKET_PORT:-8000}"

echo "==> NestMarket ishga tushirilmoqda..."

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Virtual muhit yaratilmoqda ($VENV_DIR)..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> Kutubxonalar o'rnatilmoqda..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> Migratsiyalar tayyorlanmoqda..."
python manage.py makemigrations shop --noinput
python manage.py migrate --noinput

echo "==> Boshlang'ich ma'lumotlar tekshirilmoqda (seed_lab)..."
python manage.py seed_lab

echo ""
echo "==> Server ishga tushmoqda: http://$HOST:$PORT/"
echo "==> To'xtatish uchun Ctrl+C bosing."
echo ""

exec python manage.py runserver "$HOST:$PORT"
