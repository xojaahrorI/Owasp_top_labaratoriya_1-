import base64
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .models import AuditLog, LabProgress
from .flags import CHALLENGES

FLAG_A03 = CHALLENGES["a03"]["flag"]
FLAG_A09 = CHALLENGES["a09"]["flag"]

# Manbasi: shop/static/shop/js/analytics.min.js.map ichida "sizib chiqqan" token
INTERNAL_CONFIG_TOKEN = "nm_int_8f2a1c9d4e77"


def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Disallow: /backups/\n"
        "Disallow: /staff/\n"
        "Sitemap: /sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")


def backups_listing(request):
    body = """
    <div class="container py-5">
      <div class="card">
        <div class="card-body">
          <h4>Index of /backups/</h4>
          <ul>
            <li><a href="/static/shop/downloads/db_backup_2025-11-03.zip">db_backup_2025-11-03.zip</a></li>
          </ul>
        </div>
      </div>
    </div>
    """
    return HttpResponse(body)


def api_internal_events(request):
    # Analytics "beacon" endpointi - haqiqiy funksiyani taqlid qiladi,
    # zaiflik bilan bog'liq emas (decoy/realizm uchun).
    return JsonResponse({"status": "ok"})


def api_internal_config(request):
    """
    A03 - Software Supply Chain Failures zanjirining ikkinchi qadami:
    source-map orqali sizib chiqqan tokenni bilgan har kim bu ichki
    konfiguratsiya endpointidan foydalanishi mumkin.
    """
    token = request.GET.get("token", "")
    if token != INTERNAL_CONFIG_TOKEN:
        return JsonResponse({"error": "invalid or missing token"}, status=403)
    return JsonResponse({
        "service": "nestmarket-analytics",
        "version": "2.3.1",
        "dependency": "leftpad-utils@1.2.0",
        "advisory": "This pinned version matches a known supply-chain compromise advisory.",
        "flag": FLAG_A03,
    })


def api_internal_audit_log(request):
    """
    A09 - Security Logging & Alerting Failures: bu endpoint faqat admin
    panel JS kodi tomonidan chaqirilishi kerak edi, lekin @login_required
    yoki boshqa hech qanday autentifikatsiya tekshiruvi qo'yilmagan.
    """
    logs = list(
        AuditLog.objects.order_by("-created_at").values("actor", "action", "target", "meta", "created_at")[:200]
    )
    return JsonResponse({"count": len(logs), "results": logs}, safe=False,
                         json_dumps_params={"default": str})


# ---------------------------------------------------------------------------
# Progress / flag tekshirish - "Xavfsizlik bo'yicha o'z-o'zini baholash"
# nomli, realistik niqoblangan bo'lim sifatida.
# ---------------------------------------------------------------------------

@login_required
def progress_view(request):
    solved = set(LabProgress.objects.filter(user=request.user).values_list("category", flat=True))
    challenges = []
    for key, c in CHALLENGES.items():
        challenges.append({
            "key": key, "code": c["code"], "title": c["title"],
            "difficulty": c["difficulty"], "solved": key in solved,
        })
    challenges.sort(key=lambda c: c["code"])

    if request.method == "POST":
        category = request.POST.get("category", "")
        flag = request.POST.get("flag", "").strip()
        c = CHALLENGES.get(category)
        if c and flag == c["flag"]:
            LabProgress.objects.get_or_create(user=request.user, category=category)
            messages.success(request, f"✅ To'g'ri! {c['code']} yechildi.")
        else:
            messages.error(request, "❌ Noto'g'ri flag.")
        return redirect("progress")

    return render(request, "shop/progress.html", {
        "challenges": challenges,
        "solved_count": len(solved),
    })


@login_required
def hint_api(request, category, level):
    c = CHALLENGES.get(category)
    if not c:
        return JsonResponse({"error": "unknown"}, status=404)
    level = max(1, min(3, int(level)))
    return JsonResponse({"level": level, "hint": c["hints"][level - 1]})
