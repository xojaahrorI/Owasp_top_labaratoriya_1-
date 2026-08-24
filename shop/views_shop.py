import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from decimal import Decimal

from .models import Product, Category, Review, Profile, Order, OrderItem, Coupon, AuditLog


def home(request):
    featured = Product.objects.order_by('?')[:8]
    categories = Category.objects.all()
    return render(request, "shop/home.html", {"featured": featured, "categories": categories})


def product_list(request):
    products = Product.objects.select_related("category").all()
    q = request.GET.get("category")
    if q:
        products = products.filter(category__slug=q)
    sort = request.GET.get("sort")
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    else:
        products = products.order_by("-created_at")
    categories = Category.objects.all()
    return render(request, "shop/product_list.html", {
        "products": products, "categories": categories, "active_category": q, "sort": sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.select_related("user").order_by("-created_at")

    if request.method == "POST" and request.user.is_authenticated:
        rating = int(request.POST.get("rating", 5))
        text = request.POST.get("text", "").strip()
        if text:
            Review.objects.create(product=product, user=request.user, rating=rating, text=text)
            messages.success(request, "Sharh qo'shildi.")
            return redirect("product_detail", slug=slug)

    return render(request, "shop/product_detail.html", {"product": product, "reviews": reviews})


def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0")
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            continue
        line_total = product.price * qty
        total += line_total
        items.append({"product": product, "qty": qty, "line_total": line_total})
    return render(request, "shop/cart.html", {"items": items, "total": total})


def cart_add(request, product_id):
    cart = request.session.get("cart", {})
    key = str(product_id)
    qty = int(request.POST.get("qty", 1)) if request.method == "POST" else 1
    cart[key] = cart.get(key, 0) + qty
    request.session["cart"] = cart
    request.session.modified = True
    messages.success(request, "Savatchaga qo'shildi.")
    return redirect(request.META.get("HTTP_REFERER", "/products/"))


def cart_remove(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        email = request.POST.get("email", "").strip()
        if not username or not password:
            messages.error(request, "Barcha maydonlarni to'ldiring.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Bu foydalanuvchi nomi band.")
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user, role="customer", avatar_seed=username)
            login(request, user)
            messages.success(request, "Xush kelibsiz!")
            return redirect("home")
    return render(request, "shop/register.html")


def login_view(request):
    # ATAYLAB ZAIF (A07): urinishlar sonini cheklovchi hech qanday
    # mexanizm (rate limiting / lockout) yo'q.
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        request.session["login_attempts"] = request.session.get("login_attempts", 0) + 1
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Login yoki parol noto'g'ri.")
    return render(request, "shop/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")
