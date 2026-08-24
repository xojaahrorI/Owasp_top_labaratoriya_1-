import base64
import hashlib
import pickle
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Profile
from .flags import CHALLENGES

FLAG_A04 = CHALLENGES["a04"]["flag"]

# ATAYLAB ZAIF (A04 - Cryptographic Failures): parolni tiklash tokeni
# kuchli tasodifiy generator (secrets.token_urlsafe) o'rniga oddiy,
# taxmin qilinadigan MD5(username + fixed salt) orqali quriladi.
# "Salt" qiymati esa view-source orqali topsa bo'ladigan HTML izohida
# tasodifan qoldirilgan (templates/shop/security.html'ga qarang).
RESET_SALT = "nestmarket_2024"


def _make_reset_token(username: str) -> str:
    return hashlib.md5(f"{username}:{RESET_SALT}".encode()).hexdigest()


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": "customer"})
    if request.method == "POST":
        profile.phone = request.POST.get("phone", "")
        profile.bio = request.POST.get("bio", "")
        profile.save()
        messages.success(request, "Profil yangilandi.")
        return redirect("profile")
    return render(request, "shop/profile.html", {"profile": profile})


def security_view(request):
    """Parolni tiklash so'rovi (forgot password) sahifasi."""
    reset_link = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        try:
            user = User.objects.get(username=username)
            token = _make_reset_token(username)
            profile, _ = Profile.objects.get_or_create(user=user, defaults={"role": "customer"})
            profile.reset_token = token
            profile.reset_token_created = timezone.now()
            profile.save()
            # Real hayotda bu link email orqali yuboriladi; demo/lab
            # maqsadida to'g'ridan-to'g'ri ekranda ko'rsatamiz.
            reset_link = f"/account/security/reset/{username}/{token}/"
            messages.info(request, "Agar hisob mavjud bo'lsa, tiklash havolasi yuborildi (demo uchun pastda ko'rsatilgan).")
        except User.DoesNotExist:
            messages.info(request, "Agar hisob mavjud bo'lsa, tiklash havolasi yuborildi.")
    return render(request, "shop/security.html", {"reset_link": reset_link, "salt_hint": RESET_SALT})


def security_reset_confirm(request, username, token):
    user = get_object_or_404(User, username=username)
    expected = _make_reset_token(username)

    if token != expected:
        return render(request, "shop/security_reset.html", {"valid": False, "username": username})

    if request.method == "POST":
        new_password = request.POST.get("password", "")
        if len(new_password) >= 4:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Parol muvaffaqiyatli yangilandi. Endi tizimga kiring.")
            return redirect("login")
        messages.error(request, "Parol juda qisqa.")

    is_privileged = hasattr(user, "profile") and user.profile.role in ("admin", "staff")
    flag_note = None
    if is_privileged:
        flag_note = FLAG_A04

    return render(request, "shop/security_reset.html", {
        "valid": True, "username": username, "is_privileged": is_privileged, "flag_note": flag_note,
    })


# ---------------------------------------------------------------------------
# A08 - Software and Data Integrity Failures: sozlamalarni ".nmbak" fayldan
# tiklash (import) funksiyasi.
# ---------------------------------------------------------------------------

EXAMPLE_EXPORT_SNIPPET = """import pickle, base64

# Bu - "Sozlamalarni eksport qilish" tugmasi yaratadigan namunaviy fayl formati.
settings_obj = {
    "username": "sizning_loginingiz",
    "bio": "...",
    "role": "customer",   # <-- bu maydonni o'zgartirib ko'ring
}

data = base64.b64encode(pickle.dumps(settings_obj)).decode()
with open("profile_backup.nmbak", "w") as f:
    f.write(data)
"""


@login_required
def wishlist_import(request):
    result_message = None
    result_kind = "info"

    if request.method == "POST":
        raw = request.POST.get("payload", "").strip()
        try:
            decoded = pickle.loads(base64.b64decode(raw))
        except Exception as e:
            decoded = None
            result_message = f"Faylni o'qib bo'lmadi: {e}"
            result_kind = "danger"

        if decoded is not None and isinstance(decoded, dict):
            # ATAYLAB ZAIF: import qilingan ma'lumotdagi "role" maydoniga
            # hech qanday tekshiruvsiz ishoniladi va bevosita profilga
            # yoziladi - foydalanuvchi o'z huquqini o'zi oshirib olishi
            # mumkin (privilege escalation via insecure deserialization).
            profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": "customer"})
            if "bio" in decoded:
                profile.bio = str(decoded["bio"])[:500]
            if "role" in decoded and decoded["role"] in ("customer", "support", "staff", "admin"):
                profile.role = decoded["role"]
            profile.save()
            result_message = f"Sozlamalar tiklandi: {decoded}"
            result_kind = "success"
        elif decoded is not None:
            result_message = f"Kutilmagan format: {decoded!r}"
            result_kind = "warning"

    return render(request, "shop/wishlist_import.html", {
        "example": EXAMPLE_EXPORT_SNIPPET,
        "result_message": result_message,
        "result_kind": result_kind,
    })
