def cart_summary(request):
    cart = request.session.get("cart", {})
    count = sum(cart.values()) if cart else 0
    return {"cart_count": count}
