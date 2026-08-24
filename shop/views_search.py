from django.shortcuts import render

from .models import Product
from .injection_db import ensure_seeded, run_vulnerable_search


def search_view(request):
    query = request.GET.get("q", "").strip()
    results = []
    error = None

    if query:
        ensure_seeded(Product.objects.select_related("category").all())
        rows, error = run_vulnerable_search(query)
        results = [
            {"name": r[0], "description": r[1], "price": r[2], "category": r[3]}
            for r in rows
        ]

    return render(request, "shop/search.html", {"query": query, "results": results, "error": error})
