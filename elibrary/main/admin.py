from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Book  # Import your model

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "year", "genre")
    search_fields = ("title", "author", "genre")

admin.site.register(User, UserAdmin)