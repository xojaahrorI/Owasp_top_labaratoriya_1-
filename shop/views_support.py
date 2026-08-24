from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import SupportTicket, TicketMessage
from .flags import CHALLENGES

FLAG_A07 = CHALLENGES["a07"]["flag"]


@login_required
def ticket_list(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by("-created_at")
    is_support = hasattr(request.user, "profile") and request.user.profile.role in ("support", "staff", "admin")
    return render(request, "shop/ticket_list.html", {"tickets": tickets, "is_support": is_support})


@login_required
def ticket_create(request):
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        if subject and body:
            ticket = SupportTicket.objects.create(user=request.user, subject=subject)
            TicketMessage.objects.create(ticket=ticket, sender_name=request.user.username, body=body)
            messages.success(request, "Murojaatingiz yuborildi.")
            return redirect("ticket_list")
    return render(request, "shop/ticket_create.html")


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, pk=ticket_id)
    is_support = hasattr(request.user, "profile") and request.user.profile.role in ("support", "staff", "admin")
    if ticket.user != request.user and not is_support:
        messages.error(request, "Bu murojaatga kirish huquqingiz yo'q.")
        return redirect("ticket_list")

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            TicketMessage.objects.create(
                ticket=ticket, sender_name=request.user.username,
                is_staff=is_support, body=body,
            )
            return redirect("ticket_detail", ticket_id=ticket.id)

    msgs = ticket.messages.order_by("created_at")
    return render(request, "shop/ticket_detail.html", {"ticket": ticket, "msgs": msgs})


@login_required
def support_inbox(request):
    """
    Faqat 'support' (yoki yuqori) rolidagi xodimlar ko'ra oladigan umumiy
    navbat - A07 zanjirining maqsadi: zaif parolli support hisobiga
    brute-force orqali kirib, shu yerga yetib kelish.
    """
    is_support = hasattr(request.user, "profile") and request.user.profile.role in ("support", "staff", "admin")
    if not is_support:
        messages.error(request, "Faqat support xodimlari uchun.")
        return redirect("ticket_list")

    tickets = SupportTicket.objects.select_related("user").order_by("-created_at")
    return render(request, "shop/support_inbox.html", {"tickets": tickets, "flag": FLAG_A07})
