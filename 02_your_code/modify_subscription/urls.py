from django.contrib import admin
from django.urls import path
from. import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('subscription/upgrade/<str:subscription_id>/<str:subscription_level>', views.upgrade_subscription),
    path('subscription/downgrade/<str:subscription_id>/<str:subscription_level>', views.downgrade_subscription),
    path('subscription/features/<str:subscription_id>', views.customize_features)
]
