from django.urls import path, include
from . import views

urlpatterns = [
    path('index', views.index, name="index"),
    path('report', views.report, name="report"),
    path('notification', views.notification, name="notification"),
    path('', views.auth_page, name="auth_page"),
    path('logout/', views.logout_user, name="logout"),

    # PWA URLs (avoids clashing with root URL)
    path('', include('pwa.urls')),  # still works because it only serves /manifest.json, /serviceworker.js etc.
]
