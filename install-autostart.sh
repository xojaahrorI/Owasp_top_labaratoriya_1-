#!/usr/bin/env bash
# NestMarket - tizim yuklanganda/kirilganda avtomatik ishga tushishi uchun
# systemd (user-level) xizmatini o'rnatadi.
#
# Ishlatish:
#   chmod +x install-autostart.sh
#   ./install-autostart.sh
#
# Buni o'chirish uchun:
#   systemctl --user disable --now nestmarket.service

set -e

cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
UNIT_FILE="$UNIT_DIR/nestmarket.service"

mkdir -p "$UNIT_DIR"

# Avval venv borligiga ishonch hosil qilamiz (yo'q bo'lsa start.sh orqali yaratiladi)
if [ ! -d "$PROJECT_DIR/venv" ]; then
  echo "==> Birinchi marta ishga tushirish uchun ./start.sh avtomatik chaqirilmoqda..."
  echo "==> (Ctrl+C bosing, server ishga tushgach - venv tayyor bo'ladi.)"
  "$PROJECT_DIR/start.sh" &
  SETUP_PID=$!
  sleep 15
  kill "$SETUP_PID" 2>/dev/null || true
fi

cat > "$UNIT_FILE" << EOF
[Unit]
Description=NestMarket OWASP Top 10:2025 Lab
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/manage.py runserver 127.0.0.1:8000
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now nestmarket.service

echo ""
echo "==> O'rnatildi! NestMarket endi tizimga har kirganingizda avtomatik ishga tushadi."
echo "==> Manzil: http://127.0.0.1:8000/"
echo ""
echo "Foydali buyruqlar:"
echo "  systemctl --user status nestmarket.service    # holatni ko'rish"
echo "  systemctl --user stop nestmarket.service       # to'xtatish"
echo "  systemctl --user disable --now nestmarket.service  # avtomatik ishga tushishni bekor qilish"
echo ""
echo "Eslatma: bu xizmat faqat siz tizimga kirganingizda (login) ishga tushadi."
echo "Agar login qilmasdan ham (kompyuter yoqilishi bilan) ishlashini xohlasangiz:"
echo "  sudo loginctl enable-linger \$USER"
