from django.urls import path

from . import views_shop, views_orders, views_account, views_staff, views_api, views_support, views_search

urlpatterns = [
    path('', views_shop.home, name='home'),
    path('products/', views_shop.product_list, name='product_list'),
    path('products/<slug:slug>/', views_shop.product_detail, name='product_detail'),
    path('search/', views_search.search_view, name='search'),

    path('cart/', views_shop.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views_shop.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views_shop.cart_remove, name='cart_remove'),

    path('checkout/', views_orders.checkout_view, name='checkout'),
    path('orders/', views_orders.order_list, name='order_list'),
    path('orders/<int:order_id>/', views_orders.order_detail, name='order_detail'),

    path('register/', views_shop.register_view, name='register'),
    path('login/', views_shop.login_view, name='login'),
    path('logout/', views_shop.logout_view, name='logout'),

    path('account/profile/', views_account.profile_view, name='profile'),
    path('account/security/', views_account.security_view, name='security'),
    path('account/security/reset/<str:username>/<str:token>/', views_account.security_reset_confirm, name='security_reset_confirm'),
    path('account/wishlist/import/', views_account.wishlist_import, name='wishlist_import'),

    path('staff/', views_staff.staff_home, name='staff_home'),
    path('staff/reports/', views_staff.staff_reports, name='staff_reports'),

    path('support/', views_support.ticket_list, name='ticket_list'),
    path('support/new/', views_support.ticket_create, name='ticket_create'),
    path('support/<int:ticket_id>/', views_support.ticket_detail, name='ticket_detail'),
    path('support/inbox/', views_support.support_inbox, name='support_inbox'),

    path('backups/', views_api.backups_listing, name='backups_listing'),
    path('robots.txt', views_api.robots_txt, name='robots_txt'),

    path('api/v1/internal/events/', views_api.api_internal_events, name='api_events'),
    path('api/v1/internal/config/', views_api.api_internal_config, name='api_config'),
    path('api/v1/internal/audit-log/', views_api.api_internal_audit_log, name='api_audit_log'),

    path('account/progress/', views_api.progress_view, name='progress'),
    path('hint/<str:category>/<int:level>/', views_api.hint_api, name='hint'),
]
