from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
import pymupdf

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email.split("@")[0])  # Auto-generate username
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='default_profile.png')
    favorites = models.ManyToManyField('Book', related_name="users_favorited", blank=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    username = models.CharField(max_length=150, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Book(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField()
    author = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)
    pdf = models.FileField(upload_to="books/pdfs/", null=True, blank=True)
    cover_image = models.ImageField(upload_to="books/covers/", blank=True, null=True)
    total_pages = models.PositiveIntegerField(default=0)
    favorited_by = models.ManyToManyField(User, related_name="favorite_books", blank=True)
    extracted_text = models.TextField(blank=True, null=True)

    def extract_text_from_pdf(self):
        if not self.pdf:
            return ""

        text = ""
        doc = pymupdf.open(self.pdf.path)
        for page in doc:
            text += page.get_text("text") + "\n"
        
        return text

    def save(self, *args, **kwargs):
        if not self.extracted_text and self.pdf:
            self.extracted_text = self.extract_text_from_pdf()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BookPage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="pages")
    image = models.ImageField(upload_to="books/pages/", blank=True, null=True)
    page_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('book', 'page_number')

    def __str__(self):
        return f"{self.book.title} - Page {self.page_number}"
