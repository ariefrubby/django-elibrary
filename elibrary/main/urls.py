from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("book-detail/<int:book_id>/", views.book_detail_view, name="book_detail"),
    path('book/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path("upload/", views.upload_view, name="upload"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path('toggle_favorite/<int:book_id>/', views.toggle_favorite, name='toggle_favorite'),
    path("delete_book/<int:book_id>/", views.delete_book, name="delete_book"),
    path("preview-book/<int:book_id>/", views.preview_book, name="preview_book"),
    path('analyze_keywords/<int:book_id>/', views.analyze_keywords, name='analyze_keywords'),
]