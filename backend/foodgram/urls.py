from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse


def index(request):
    return HttpResponse("""
        <html>
        <head>
            <title>Foodgram</title>
        </head>
        <body>
            <h1>Добро пожаловать в Foodgram!</h1>
            <p>Это главная страница вашего проекта.</p>
            <p>Перейдите в <a href="/api/">API</a> или
            <a href="/admin/">админку</a>.</p>
        </body>
        </html>
    """)


urlpatterns = [
    path("", index, name="index"),
    path("api/", include("api.urls", namespace="api")),
    # Убираем эту строчку:  path("api/", include("users.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls.authtoken")),
]
