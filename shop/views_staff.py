from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Order, Product, User, AuditLog
from .flags import CHALLENGES

FLAG_A08 = CHALLENGES["a08"]["code"]  # placeholder, real flag injected in template context below
FLAG_A08_REAL = CHALLENGES["a08"]["flag"]


def _is_staff(user):
    return user.is_authenticated and hasattr(user, "profile") and user.profile.role in ("staff", "admin")


@login_required
def staff_home(request):
    # To'g'ri himoyalangan (decoy emas) - faqat role=staff/admin kira oladi.
    if not _is_staff(request.user):
        messages.error(request, "Ushbu bo'limga faqat xodimlar kira oladi.")
        return redirect("home")

    order_count = Order.objects.count()
    product_count = Product.objects.count()
    user_count = User.objects.count()
    return render(request, "shop/staff_home.html", {
        "order_count": order_count, "product_count": product_count, "user_count": user_count,
    })


@login_required
def staff_reports(request):
    if not _is_staff(request.user):
        messages.error(request, "Ushbu bo'limga faqat xodimlar kira oladi.")
        return redirect("home")

    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:10]
    return render(request, "shop/staff_reports.html", {
        "recent_orders": recent_orders,
        "flag": FLAG_A08_REAL,
    })
