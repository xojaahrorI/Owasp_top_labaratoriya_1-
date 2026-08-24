from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("support", "Support Agent"),
        ("staff", "Staff"),
        ("admin", "Administrator"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    avatar_seed = models.CharField(max_length=40, default="default")
    # Faqat staff/admin uchun to'ldiriladigan ichki maydon - odatiy holatda
    # profil sahifasida ko'rsatilmaydi, lekin views.py'dagi tekshiruv
    # yetarli emas (A01 mavzusi bilan bog'liq).
    internal_notes = models.TextField(blank=True)
    reset_token = models.CharField(max_length=64, blank=True)
    reset_token_created = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    accent = models.CharField(max_length=7, default="#38bdf8")  # placeholder rasm rangi
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.user.username}"


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveSmallIntegerField(default=10)
    active = models.BooleanField(default=True)
    single_use = models.BooleanField(default=True)

    def __str__(self):
        return self.code


ORDER_STATUS = [
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
    ("cancelled", "Cancelled"),
]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="pending")
    shipping_address = models.CharField(max_length=255)
    tracking_code = models.CharField(max_length=40, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_applied = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    coupon_apply_count = models.PositiveSmallIntegerField(default=0)
    # Faqat xodimlar ko'rishi kerak bo'lgan ichki eslatma - buyurtma
    # tafsiloti sahifasida egalik tekshiruvi yetarli emasligi sababli
    # istalgan login qilgan foydalanuvchi buni ko'rishi mumkin (A01).
    internal_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.quantity * self.unit_price


class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default="open")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject


class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender_name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


class AuditLog(models.Model):
    actor = models.CharField(max_length=100)
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True)
    meta = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.created_at} {self.actor} {self.action}"


class ApiToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens")
    token = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)


class LabProgress(models.Model):
    """Har bir foydalanuvchi uchun qaysi toifa flagi topilganini saqlaydi."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lab_progress")
    category = models.CharField(max_length=10)  # a01..a10
    solved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "category")
