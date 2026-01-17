from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.urls import reverse

urlpatterns = [
    path("admin/", admin.site.urls),

    # 🔥 THIS LINE CONNECTS THE ATTENDANCE APP
    path("attendance/", include("attendance.urls")),

    # 🔁 ROOT → STUDENT DASHBOARD
    path("", lambda request: redirect(reverse("student_dashboard"))),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
