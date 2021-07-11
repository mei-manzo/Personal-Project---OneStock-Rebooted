from django.urls import path     
from . import views
urlpatterns = [
    path('', views.index),
    path('success', views.success),
    path('check_registration', views.check_registration),
    path('check_login', views.check_login),
    path('logout', views.logout),
    path('feed/<int:id>', views.feed_parser),
    path('stats', views.stats),
    path('profile', views.profile),
    path('check_stock_name', views.check_stock),
    path('rm-stock/<int:id>', views.remove_stock),
    path('buy_sell', views.buy_sell),
]