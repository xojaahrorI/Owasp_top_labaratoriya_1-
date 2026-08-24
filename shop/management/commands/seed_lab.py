import base64
import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from shop.models import (
    Profile, Category, Product, Review, Coupon, Order, OrderItem,
    SupportTicket, TicketMessage, AuditLog,
)
from shop.flags import CHALLENGES

FLAG_A01 = CHALLENGES["a01"]["flag"]
FLAG_A09 = CHALLENGES["a09"]["flag"]

CATEGORIES = ["Electronics", "Home & Kitchen", "Fashion", "Sports & Outdoors", "Books", "Beauty & Care"]

ADJECTIVES = ["Premium", "Compact", "Wireless", "Portable", "Classic", "Eco", "Pro", "Ultra", "Everyday", "Smart"]
NOUNS = {
    "Electronics": ["Headphones", "Bluetooth Speaker", "USB-C Hub", "Webcam", "Power Bank", "Mechanical Keyboard", "Smartwatch", "Router"],
    "Home & Kitchen": ["Coffee Maker", "Blender", "Non-stick Pan", "Air Fryer", "Cutlery Set", "Storage Jar Set", "Toaster", "Kettle"],
    "Fashion": ["Cotton T-Shirt", "Denim Jacket", "Running Shoes", "Leather Belt", "Wool Scarf", "Backpack", "Sunglasses", "Baseball Cap"],
    "Sports & Outdoors": ["Yoga Mat", "Water Bottle", "Camping Tent", "Resistance Bands", "Hiking Backpack", "Jump Rope", "Cycling Gloves", "Sports Towel"],
    "Books": ["Notebook Set", "Planner 2026", "Sketchbook", "Bookmark Pack", "Desk Calendar", "Pen Set"],
    "Beauty & Care": ["Face Cream", "Shampoo Bar", "Electric Trimmer", "Makeup Brush Set", "Hair Dryer", "Skincare Kit"],
}
ACCENTS = ["#38bdf8", "#f97316", "#22c55e", "#a855f7", "#ef4444", "#0ea5e9", "#eab308", "#14b8a6"]

REVIEW_SNIPPETS = [
    "Juda mamnunman, tez yetib keldi va sifati yaxshi.",
    "Narxiga yarasha, lekin qadoqlash yaxshiroq bo'lishi mumkin edi.",
    "Ikkinchi marta buyurtma qildim, hammasi yaxshi.",
    "Kutilganidan yaxshiroq chiqdi, tavsiya qilaman.",
    "O'rtacha, ba'zi joylari kutilganidek emas.",
    "Yetkazib berish biroz kechikdi, lekin mahsulot o'zi yaxshi.",
    "Do'stimga ham tavsiya qildim, u ham mamnun bo'ldi.",
    "Narxi biroz baland, lekin sifati mos keladi.",
    "Rangi rasmda ko'rsatilganidek chiqmadi, biroz xafa bo'ldim.",
    "Mukammal! Aynan kutganimdek.",
]

CUSTOMER_NAMES = [
    "j.tursunov", "malika_y", "aziz.k", "n.sharipova", "b.rustamov", "d.karimova",
    "s.abdullayev", "f.nazarova", "o.yusupov", "z.rahimova", "t.mirzayev", "l.qodirova",
]

TICKET_SUBJECTS = [
    "Buyurtmam qachon yetib keladi?", "Mahsulot noto'g'ri keldi", "Pul qaytarish so'rovi",
    "Hisobimga kira olmayapman", "Yetkazib berish manzilini o'zgartirish",
    "Kupon ishlamayapti", "Mahsulot sifatiga shikoyat", "Buyurtmani bekor qilish",
]

AUDIT_ACTIONS = [
    "logged in", "updated product stock", "processed order", "replied to support ticket",
    "exported sales report", "updated shipping status", "reviewed new customer signup",
    "adjusted product price", "archived old ticket", "ran scheduled backup",
]


class Command(BaseCommand):
    help = "NestMarket lab uchun realistik hajmdagi boshlang'ich ma'lumotlarni yaratadi."

    def handle(self, *args, **options):
        random.seed(1337)
        self.stdout.write("Tozalanmoqda va qayta urug'lanmoqda...")

        # ------------------------------------------------------------- Users
        admin_user, _ = self._get_or_create_user("admin_ops", "R7#kLp9!qXz2", "admin",
                                                   "Operations administrator account.")
        support_user, _ = self._get_or_create_user("support_helpdesk", "support123", "support",
                                                     "Shared customer support inbox account.")
        staff_user, _ = self._get_or_create_user("staff_manager", "Mn4$wTr8!lKp", "staff",
                                                   "Warehouse & catalog staff account.")

        customers = []
        for uname in CUSTOMER_NAMES:
            u, _ = self._get_or_create_user(uname, "password123", "customer", "")
            customers.append(u)

        # -------------------------------------------------------- Categories
        categories = {}
        for name in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, slug=slugify(name))
            categories[name] = cat

        # ---------------------------------------------------------- Products
        products = []
        pid = 0
        for cat_name, nouns in NOUNS.items():
            for noun in nouns:
                for adj in random.sample(ADJECTIVES, 2):
                    pid += 1
                    name = f"{adj} {noun}"
                    slug = slugify(f"{name}-{pid}")
                    price = round(random.uniform(9.99, 199.99), 2)
                    product, _ = Product.objects.get_or_create(
                        slug=slug,
                        defaults=dict(
                            name=name, category=categories[cat_name], price=price,
                            stock=random.randint(0, 120),
                            description=f"{name} - kundalik foydalanish uchun mo'ljallangan, "
                                        f"{cat_name.lower()} bo'limidagi ommabop tanlovlardan biri.",
                            accent=random.choice(ACCENTS),
                            created_at=timezone.now() - timedelta(days=random.randint(1, 300)),
                        ),
                    )
                    products.append(product)
        self.stdout.write(f"{len(products)} ta mahsulot tayyor.")

        # ----------------------------------------------------------- Reviews
        if not Review.objects.exists():
            for _ in range(60):
                Review.objects.create(
                    product=random.choice(products),
                    user=random.choice(customers),
                    rating=random.randint(3, 5),
                    text=random.choice(REVIEW_SNIPPETS),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 200)),
                )
        self.stdout.write("Sharhlar tayyor.")

        # ---------------------------------------------------------- Coupons
        Coupon.objects.get_or_create(code="WELCOME10", defaults=dict(discount_percent=10, active=True, single_use=True))
        Coupon.objects.get_or_create(code="SUMMER15", defaults=dict(discount_percent=15, active=True, single_use=True))
        Coupon.objects.get_or_create(code="FREESHIP", defaults=dict(discount_percent=3, active=True, single_use=False))

        # ------------------------------------------------------------ Orders
        if Order.objects.count() < 100:
            for i in range(120):
                buyer = random.choice(customers)
                created = timezone.now() - timedelta(days=random.randint(0, 180), hours=random.randint(0, 23))
                order = Order.objects.create(
                    user=buyer,
                    created_at=created,
                    status=random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
                    shipping_address=f"{random.randint(1,120)}-uy, {random.randint(1,40)}-mavze, Toshkent",
                    tracking_code=f"NM-{random.randint(100000,999999)}",
                    total=0,
                )
                n_items = random.randint(1, 4)
                total = 0
                for it_product in random.sample(products, n_items):
                    qty = random.randint(1, 3)
                    OrderItem.objects.create(order=order, product=it_product, quantity=qty, unit_price=it_product.price)
                    total += float(it_product.price) * qty
                order.total = round(total, 2)
                order.save()

                # Bir nechta buyurtmalarga "internal note" qo'shamiz - noise
                # sifatida, flag bilan bog'liq emas.
                if random.random() < 0.08:
                    order.internal_notes = random.choice([
                        "Customer requested gift wrap.",
                        "Fragile - handle with care.",
                        "Repeat customer - priority packing.",
                        "Address confirmed by phone.",
                    ])
                    order.save()

            # A01 uchun maxsus buyurtma - admin_ops nomiga, 120 tadan
            # keyin (o'rta diapazonda) yaratiladi, IDOR orqali topiladi.
            admin_order = Order.objects.create(
                user=admin_user,
                created_at=timezone.now() - timedelta(days=45),
                status="delivered",
                shipping_address="Head office - internal procurement",
                tracking_code=f"NM-{random.randint(100000,999999)}",
                total=249.99,
            )
            OrderItem.objects.create(order=admin_order, product=random.choice(products), quantity=1, unit_price=249.99)
            encoded_note = base64.b64encode(
                f"internal-audit-code:{FLAG_A01}".encode()
            ).decode()
            admin_order.internal_notes = f"[base64] {encoded_note}"
            admin_order.save()

        self.stdout.write(f"{Order.objects.count()} ta buyurtma tayyor (jumladan 1 ta admin buyurtmasi).")

        # ----------------------------------------------------- Support tickets
        if not SupportTicket.objects.exists():
            for i in range(10):
                buyer = random.choice(customers)
                ticket = SupportTicket.objects.create(
                    user=buyer, subject=random.choice(TICKET_SUBJECTS),
                    status=random.choice(["open", "closed"]),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 90)),
                )
                TicketMessage.objects.create(
                    ticket=ticket, sender_name=buyer.username,
                    body="Salom, iltimos yordam bering.", is_staff=False,
                )
                if random.random() < 0.6:
                    TicketMessage.objects.create(
                        ticket=ticket, sender_name=support_user.username,
                        body="Salom! Murojaatingiz ko'rib chiqilmoqda, tez orada javob beramiz.",
                        is_staff=True,
                    )
        self.stdout.write("Support tiketlari tayyor.")

        # --------------------------------------------------------- Audit logs
        if AuditLog.objects.count() < 100:
            actors = [admin_user.username, staff_user.username, support_user.username, "system"]
            for i in range(150):
                AuditLog.objects.create(
                    actor=random.choice(actors),
                    action=random.choice(AUDIT_ACTIONS),
                    target=f"order#{random.randint(1,150)}" if random.random() < 0.5 else f"product#{random.randint(1,60)}",
                    meta="",
                    created_at=timezone.now() - timedelta(days=random.randint(0, 90), minutes=random.randint(0, 1000)),
                )
            # A09 flag - 150 ta oddiy yozuv orasida bitta "muhim" yozuv
            AuditLog.objects.create(
                actor="system",
                action="exported internal audit trail",
                target="archive-2025-11.tar.gz",
                meta=f"checksum-token={FLAG_A09}",
                created_at=timezone.now() - timedelta(days=12, hours=3),
            )
        self.stdout.write("Audit-log yozuvlari tayyor.")

        self.stdout.write(self.style.SUCCESS(
            "\nSeed muvaffaqiyatli yakunlandi.\n"
            "Demo hisoblar:\n"
            "  customer  -> istalgan customer login (masalan j.tursunov) / password123\n"
            "  (boshqa hisoblarni ochiq bermaymiz - ularni topish laboratoriyaning bir qismi)\n"
        ))

    @staticmethod
    def _get_or_create_user(username, password, role, bio):
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
        Profile.objects.get_or_create(user=user, defaults=dict(role=role, bio=bio, avatar_seed=username))
        return user, created
