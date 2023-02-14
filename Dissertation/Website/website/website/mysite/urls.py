from django.urls import path
from website.mysite import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("add-image", views.addImage, name="add-image"),
    path("image-search", views.imageSearch, name="image-search"),
    path("delete-image", views.deleteImage, name="delete-image")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)