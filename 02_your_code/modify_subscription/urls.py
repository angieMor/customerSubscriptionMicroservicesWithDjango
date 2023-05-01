from django.contrib import admin
from django.urls import path
from. import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('subscription/upgrade/<str:subscription_id>', views.upgrade_subscription),
    path('subscription/downgrade/<str:subscription_id>', views.downgrade_subscription)
]
