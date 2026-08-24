import random
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import Product, Order, OrderItem, Coupon, AuditLog
from .flags import CHALLENGES

FLAG_A06 = CHALLENGES["a06"]["flag"]
FLAG_A10 = CHALLENGES["a10"]["flag"]
INTERNAL_SESSION_TOKEN = FLAG_A10  # ataylab shu nom bilan - xato sahifasida sizib chiqadi


@login_required
def checkout_view(request):
    cart = request.session.get("cart", {})
    items = []
    subtotal = Decimal("0")
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            continue
        line_total = product.price * qty
        subtotal += line_total
        items.append({"product": product, "qty": qty, "line_total": line_total})

    # Kuponni checkout sessiyasida saqlaymiz - "Qo'llash" tugmasi bir necha
    # marta bosilishi mumkin.
    applied_codes = request.session.get("checkout_coupons", [])
    discount_percent_total = 0

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "apply_coupon":
            code = request.POST.get("coupon_code", "").strip().upper()
            try:
                coupon = Coupon.objects.get(code=code, active=True)
                # ATAYLAB ZAIF DIZAYN (A06): kupon avval qo'llanganmi degan
                # tekshiruv faqat frontendda (JS bilan tugmani disable qilish)
                # amalga oshirilgan - serverda bir xil kodni qayta-qayta
                # qo'llashning oldi olinmagan.
                applied_codes.append(code)
                request.session["checkout_coupons"] = applied_codes
                messages.success(request, f"Kupon qo'llandi: {code} (-{coupon.discount_percent}%)")
            except Coupon.DoesNotExist:
                messages.error(request, "Bunday kupon topilmadi yoki faol emas.")
            return redirect("checkout")

        elif action == "clear_coupons":
            request.session["checkout_coupons"] = []
            return redirect("checkout")

        elif action == "place_order":
            if not items:
                messages.error(request, "Savatcha bo'sh.")
                return redirect("cart")

            for code in applied_codes:
                try:
                    c = Coupon.objects.get(code=code, active=True)
                    discount_percent_total += c.discount_percent
                except Coupon.DoesNotExist:
                    pass

            address = request.POST.get("address", "").strip()
            if not address:
                messages.error(request, "Yetkazib berish manzilini kiriting.")
                return redirect("checkout")

            # A10 - Mishandling of Exceptional Conditions:
            # foydalanuvchi manzil maydoniga o'ta katta chegirma imitatsiya
            # qilish uchun maxsus "override_discount" so'rov parametrini
            # yuborishi mumkin - bu ATAYLAB tekshirilmagan bo'lib, kutilmagan
            # turdagi/qiymatdagi kirim serverda ushlanmagan istisno (exception)
            # hosil qiladi.
            raw_override = request.POST.get("override_discount", "")
            try:
                if raw_override:
                    discount_percent_total += int(raw_override)

                total = subtotal * (Decimal(100 - discount_percent_total) / Decimal(100))

                order = Order.objects.create(
                    user=request.user,
                    status="pending",
                    shipping_address=address,
                    tracking_code=f"NM-{random.randint(100000,999999)}",
                    total=total if total > 0 else Decimal("0.00"),
                    coupon_apply_count=len(applied_codes),
                )
                for it in items:
                    OrderItem.objects.create(
                        order=order, product=it["product"], quantity=it["qty"],
                        unit_price=it["product"].price,
                    )

                request.session["cart"] = {}
                request.session["checkout_coupons"] = []

                if total <= 0:
                    order.internal_notes = (
                        f"AUTO-FLAG (business logic bypass detected): {FLAG_A06}"
                    )
                    order.save()
                    messages.success(
                        request,
                        f"Buyurtma #{order.id} yaratildi. Umumiy summa: ${total:.2f} "
                        f"(tizim bu buyurtmani 'bepul' sifatida qayta ishladi).",
                    )
                else:
                    messages.success(request, f"Buyurtma #{order.id} muvaffaqiyatli yaratildi!")
                return redirect("order_detail", order_id=order.id)

            except (InvalidOperation, ValueError, OverflowError) as e:
                # ATAYLAB YOMON XATO BOSHQARUVI: to'liq texnik ma'lumot
                # foydalanuvchiga to'g'ridan-to'g'ri ko'rsatiladi.
                debug_html = f"""
                <div class="container py-5">
                  <div class="alert alert-danger">
                    <h4>500 - Internal Server Error</h4>
                    <p>Checkout hisob-kitobida kutilmagan xatolik yuz berdi.</p>
                    <pre style="white-space:pre-wrap;">
Exception: {type(e).__name__}: {e}
Request data: override_discount={raw_override!r}, coupons={applied_codes}
subtotal={subtotal}, discount_percent_total(before error)={discount_percent_total}

--- Internal session debug state ---
INTERNAL_SESSION_TOKEN = {INTERNAL_SESSION_TOKEN!r}
                    </pre>
                  </div>
                  <a href="/checkout/">&larr; Checkout'ga qaytish</a>
                </div>
                """
                return HttpResponse(debug_html, status=500)

    for code in applied_codes:
        try:
            c = Coupon.objects.get(code=code, active=True)
            discount_percent_total += c.discount_percent
        except Coupon.DoesNotExist:
            pass

    total = subtotal * (Decimal(100 - discount_percent_total) / Decimal(100))
    if total < 0:
        total = Decimal("0.00")

    return render(request, "shop/checkout.html", {
        "items": items, "subtotal": subtotal, "applied_codes": applied_codes,
        "discount_percent_total": discount_percent_total, "total": total,
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "shop/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    # ATAYLAB ZAIF (A01 - Broken Access Control): buyurtma faqat
    # login talab qiladi, lekin buyurtma haqiqatan ham so'rov yuboruvchi
    # foydalanuvchiga tegishli ekanligi HECH QACHON tekshirilmaydi.
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "shop/order_detail.html", {"order": order})
