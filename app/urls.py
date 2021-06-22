from django.urls import path

from . import views

urlpatterns = [
    path('books/start_generation/', views.start_book_generation),
    path('books/<int:task_id>/status/', views.get_book_generation_status),
    path('books/<int:task_id>/', views.get_book)
]
