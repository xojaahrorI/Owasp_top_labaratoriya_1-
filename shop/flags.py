"""
DIQQAT: bu fayl - o'qituvchi/administrator uchun "javob kaliti".
Saytning o'zida flaglar hech qachon shu ko'rinishda (ochiq FLAG{...} deb)
darhol ko'rsatilmaydi - ular Base64/split/business-logic natijasi sifatida
turli joylarda yashiringan. Qayerda va qanday yashiringani haqida
vulnlab README.md faylida (o'qituvchi bo'limi) yozilgan.

Har bir toifa uchun 3 bosqichli yordam (hint):
  1-daraja - faqat funksional yo'nalish (OWASP nomi aytilmaydi)
  2-daraja - OWASP toifasi aytiladi
  3-daraja - texnika/usul aytiladi (aniq URL/parametr aytilmaydi)
"""

DIFFICULTY = {
    "a02": "Easy", "a07": "Easy", "a09": "Easy",
    "a01": "Medium", "a04": "Medium", "a05": "Medium", "a06": "Medium", "a10": "Medium",
    "a03": "Hard", "a08": "Hard",
}

CHALLENGES = {
    "a01": {
        "code": "A01:2025", "title": "Broken Access Control",
        "difficulty": DIFFICULTY["a01"],
        "flag": "FLAG{a01_idor_admin_order_exposed_9f3d}",
        "hints": [
            "Buyurtma tarixi sahifasida faqat o'zingizning buyurtmalaringiz ko'rinadi. Lekin buyurtma tafsiloti sahifasi qanday ochilishini (URL tuzilishini) diqqat bilan kuzating.",
            "Bu — Broken Access Control (A01:2025) turkumiga oid.",
            "Buyurtma ID'si server tomonida sizga tegishli ekanligi tekshirilmasligi mumkin (IDOR). ID raqamlarini tizimli tarzda sinab ko'ring - ayniqsa admin/xodim hisobiga tegishli bo'lishi mumkin bo'lgan diapazonda.",
        ],
    },
    "a02": {
        "code": "A02:2025", "title": "Security Misconfiguration",
        "difficulty": DIFFICULTY["a02"],
        "flag": "FLAG{a02_leaked_backup_sql_dump_77ab}",
        "hints": [
            "Saytni tekshirishni har doim standart fayllardan (robots.txt, .well-known va h.k.) boshlash foydali odat.",
            "Bu — Security Misconfiguration (A02:2025) turkumiga oid.",
            "robots.txt faylidagi Disallow qatorlariga qarab, deploy paytida qoldirilgan zaxira (backup) fayllarni qidiring.",
        ],
    },
    "a03": {
        "code": "A03:2025", "title": "Software Supply Chain Failures",
        "difficulty": DIFFICULTY["a03"],
        "flag": "FLAG{a03_source_map_leaked_internal_token_44c1}",
        "hints": [
            "Frontend qanday JS fayllar va kutubxonalarni yuklashini (Network/Sources panel) ko'rib chiqing.",
            "Bu — Software Supply Chain Failures (A03:2025) turkumiga oid.",
            "Ba'zi JS fayllar uchun source-map (.map) fayllari ham serverga qoldirilgan bo'lishi mumkin - ular original (minifikatsiya qilinmagan) kodni va ba'zan maxfiy tokenlarni oshkor qiladi. Topilgan tokenni tegishli ichki API bilan sinab ko'ring.",
        ],
    },
    "a04": {
        "code": "A04:2025", "title": "Cryptographic Failures",
        "difficulty": DIFFICULTY["a04"],
        "flag": "FLAG{a04_predictable_reset_token_admin_takeover}",
        "hints": [
            "Parolni tiklash (forgot password) funksiyasi qanday token generatsiya qilishini o'ylab ko'ring - u chindan ham tasodifiymi?",
            "Bu — Cryptographic Failures (A04:2025) turkumiga oid.",
            "Token oddiy, kuchsiz algoritm (masalan taxmin qilinadigan 'salt' + foydalanuvchi nomi) asosida quriladi. 'Salt' qiymati sahifa manbasida (view-source yoki JS fayllarida) qoldirilgan bo'lishi mumkin.",
        ],
    },
    "a05": {
        "code": "A05:2025", "title": "Injection",
        "difficulty": DIFFICULTY["a05"],
        "flag": "FLAG{a05_union_based_sqli_employee_table}",
        "hints": [
            "Mahsulot qidiruv maydoni orqa tomonda qanday so'rov yuborishini o'ylab ko'ring.",
            "Bu — Injection (A05:2025) turkumiga oid.",
            "Klassik UNION-based SQL Injection: avval ustunlar sonini ORDER BY orqali aniqlang, so'ng UNION SELECT bilan boshqa (mahsulotlarga aloqasi bo'lmagan) jadvaldan ma'lumot torting.",
        ],
    },
    "a06": {
        "code": "A06:2025", "title": "Insecure Design",
        "difficulty": DIFFICULTY["a06"],
        "flag": "FLAG{a06_coupon_stacking_negative_total}",
        "hints": [
            "Checkout paytida promo-kod qo'llash tugmasini bir necha marta bosib ko'ring - tizim buni qanday boshqaradi?",
            "Bu — Insecure Design (A06:2025) turkumiga oid.",
            "Tizim bitta kuponni bir nechta marta qo'llashning oldini serverda to'g'ri olmagan bo'lishi mumkin (faqat frontendda tugma yashiriladi). Umumiy summani nolga yoki manfiyga tushiring.",
        ],
    },
    "a07": {
        "code": "A07:2025", "title": "Authentication Failures",
        "difficulty": DIFFICULTY["a07"],
        "flag": "FLAG{a07_bruteforce_support_account_weak_pw}",
        "hints": [
            "Login formasi noto'g'ri urinishlar sonini cheklaydimi? Va barcha akkauntlar kuchli parolga egami?",
            "Bu — Authentication Failures (A07:2025) turkumiga oid.",
            "Support (qo'llab-quvvatlash) xodimi hisobi eng ko'p tarqalgan zaif parollardan biriga ega bo'lishi mumkin. Cheklovsiz brute-force qilib ko'ring.",
        ],
    },
    "a08": {
        "code": "A08:2025", "title": "Software and Data Integrity Failures",
        "difficulty": DIFFICULTY["a08"],
        "flag": "FLAG{a08_insecure_deserialization_role_escalation}",
        "hints": [
            "Profil sozlamalarini 'zaxira fayl'dan tiklash (import/restore) funksiyasi bormi? U faylni qanday o'qiydi?",
            "Bu — Software and Data Integrity Failures (A08:2025) turkumiga oid.",
            "Fayl formati ishonchsiz manbadan (sizning brauzeringizdan) kelgan ma'lumotni xavfsiz tekshirmasdan deserializatsiya qiladi. Foydalanuvchi rolini o'zgartiradigan maydonni payload ichiga qo'shib ko'ring - keyin yuqori huquq talab qiladigan bo'limlarga kirishga urinib ko'ring.",
        ],
    },
    "a09": {
        "code": "A09:2025", "title": "Security Logging & Alerting Failures",
        "difficulty": DIFFICULTY["a09"],
        "flag": "FLAG{a09_unauthenticated_internal_audit_api}",
        "hints": [
            "Sayt frontendida ishlatiladigan ichki API endpointlarni (Network panel, XHR/fetch so'rovlari) kuzatib ko'ring.",
            "Bu — Security Logging & Alerting Failures (A09:2025) turkumiga oid.",
            "Admin panelning statistik/audit ma'lumotlarini yuklaydigan ichki API endpoint autentifikatsiyasiz ham javob berishi mumkin - to'g'ridan-to'g'ri so'rov yuboring.",
        ],
    },
    "a10": {
        "code": "A10:2025", "title": "Mishandling of Exceptional Conditions",
        "difficulty": DIFFICULTY["a10"],
        "flag": "FLAG{a10_unhandled_exception_leaks_token}",
        "hints": [
            "Checkout yoki savatcha hisob-kitoblarida g'ayrioddiy/chegaraviy qiymatlar (juda katta son, bo'sh savat + kupon va h.k.) bilan sinab ko'ring.",
            "Bu — Mishandling of Exceptional Conditions (A10:2025) turkumiga oid.",
            "Ma'lum bir kombinatsiya kutilmagan server xatosini keltirib chiqaradi va xato sahifasida ichki texnik ma'lumotlar (shu jumladan maxfiy token) ko'rsatiladi.",
        ],
    },
}


def get_challenge(code):
    return CHALLENGES.get(code)
