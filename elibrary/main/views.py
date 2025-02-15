import re
import shutil
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .utils import extract_keywords
from .forms import CustomUserCreationForm, CustomAuthenticationForm, BookUploadForm
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from .models import Book, BookPage
from django.db.models import Q
from django.contrib import messages
import pymupdf
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

def register_view(request):
    print("register_view accessed")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    print("login_view accessed")
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = CustomAuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def home_view(request):
    query = request.GET.get("q", "")
    show_favorites = request.GET.get("favorites") == "true"

    if show_favorites:
        books = request.user.favorites.all()
    else:
         books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(desc__icontains=query) |
            Q(year__icontains=query)
        )
    paginator = Paginator(books, 5)
    page_number = request.GET.get("page")
    books_page = paginator.get_page(page_number)

    context = {
        "books": books_page,
        "show_favorites": show_favorites,
        "query": query,
    }
    return render(request, "home.html", context)

@login_required(login_url="login")
def profile_view(request):
    return render(request, "profile.html")

@login_required(login_url="login")
def profile_edit_view(request):
    if request.method == "POST":
        user = request.user
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        photo = request.FILES.get("photo")

        if name:
            user.name = name
        if email:
            user.email = email

        if photo:
            file_extension = os.path.splitext(photo.name)[1]  # Get file extension
            new_filename = f"{user.id}{file_extension}"

            if user.photo and user.photo.name != "default_profile.png":
                old_photo_path = os.path.join(settings.MEDIA_ROOT, user.photo.name)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)

            user.photo.save(new_filename, ContentFile(photo.read()), save=False)

        user.save()
        messages.success(request, "Profil berhasil diperbarui.")
        return redirect("profile")

    return render(request, "profile_edit.html")

def process_pdf(pdf_path, book_title):
    book_folder = os.path.join(settings.MEDIA_ROOT, f'books/{book_title}')
    os.makedirs(book_folder, exist_ok=True)

    doc = pymupdf.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):  
        page = doc[page_num]
        pix = page.get_pixmap()
        image_filename = f"page_{page_num + 1}.png"
        image_path = os.path.join(book_folder, image_filename)

        with open(image_path, "wb") as f:
            f.write(pix.tobytes("png"))

        image_paths.append(image_path)

    return image_paths

@login_required(login_url="login")
def upload_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        desc = request.POST.get("desc")
        author = request.POST.get("author")
        year = request.POST.get("year")
        pdf = request.FILES.get("pdf")
        genre = request.POST.get("genre")

        if pdf:
            pdf_name = f"{title.replace(' ', '_')}.pdf"
            pdf_path = f"books/pdfs/{pdf_name}"

            if default_storage.exists(pdf_path):
                default_storage.delete(pdf_path)

            saved_pdf_path = default_storage.save(pdf_path, ContentFile(pdf.read()))
            book = Book.objects.create(
                title=title, desc=desc, author=author, year=year, pdf=saved_pdf_path, genre=genre,
            )

            doc = pymupdf.open(default_storage.path(book.pdf.name))
            book_folder = f"books/pages/{title.replace(' ', '_')}"
            os.makedirs(os.path.join(default_storage.location, book_folder), exist_ok=True)

            new_images = []
            for page_num in range(len(doc)):
                pix = doc[page_num].get_pixmap()
                image_filename = f"{book_folder}/page_{page_num + 1}.png"
                image_path = default_storage.save(image_filename, ContentFile(pix.tobytes("png")))

                new_page = BookPage(book=book, image=image_path, page_number=page_num + 1)
                new_page.save()
                new_images.append(image_path)

            book.cover_image = new_images[0] if new_images else None
            book.total_pages = len(new_images)
            book.save()

            return redirect("home")

    return render(request, "upload.html")

def toggle_favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if book in request.user.favorites.all():
        request.user.favorites.remove(book)
        favorited = False
    else:
        request.user.favorites.add(book)
        favorited = True

    return JsonResponse({"favorited": favorited})

def book_detail_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    return render(request, "book_detail.html", {"book": book})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        book.title = request.POST.get("title")
        book.desc = request.POST.get("desc")
        book.author = request.POST.get("author")
        book.year = request.POST.get("year")
        book.genre = request.POST.get("genre", book.genre)

        new_pdf = request.FILES.get("pdf")

        if new_pdf:
            if book.pdf:
                default_storage.delete(book.pdf.path)

            pdf_name = f"{book.title.replace(' ', '_')}.pdf"
            pdf_path = f"books/pdfs/{pdf_name}"

            if default_storage.exists(pdf_path):
                default_storage.delete(pdf_path)

            book.pdf = default_storage.save(pdf_path, ContentFile(new_pdf.read()))

            old_images = BookPage.objects.filter(book=book)
            for img in old_images:
                default_storage.delete(img.image.path)
            old_images.delete()

            doc = pymupdf.open(default_storage.path(book.pdf.name))
            new_images = []
            book_folder = f"books/pages/{book.title.replace(' ', '_')}"
            os.makedirs(os.path.join(default_storage.location, book_folder), exist_ok=True)

            for page_num in range(len(doc)):
                pix = doc[page_num].get_pixmap()
                image_filename = f"{book_folder}/page_{page_num + 1}.png"
                image_path = default_storage.save(image_filename, ContentFile(pix.tobytes("png")))

                new_page = BookPage(book=book, image=image_path, page_number=page_num + 1)
                new_page.save()
                new_images.append(image_path)

            book.cover_image = new_images[0] if new_images else None
            book.total_pages = len(new_images)

        if "cover_image" in request.FILES:
            if book.cover_image:
                default_storage.delete(book.cover_image.path)
            book.cover_image = request.FILES["cover_image"]

        book.save()
        return redirect("book_detail", book_id=book.id)

    return render(request, "edit_book.html", {"book": book})

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        if book.pdf:
            default_storage.delete(book.pdf.name)

        pages = BookPage.objects.filter(book=book)
        for page in pages:
            default_storage.delete(page.image.name)
        pages.delete()

        book_folder = f"books/pages/{book.title.replace(' ', '_')}"
        folder_path = default_storage.path(book_folder)
        if default_storage.exists(folder_path):
            shutil.rmtree(folder_path)

        book.delete()

        return redirect("home")

    return redirect("book_detail", book_id=book.id)

def preview_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    pages = list(book.pages.order_by("page_number"))
    page_number = int(request.GET.get("page", 1))
    total_pages = len(pages)

    if page_number < 1:
        page_number = 1
    elif page_number > total_pages:
        page_number = total_pages

    current_page = pages[page_number - 1] 

    return render(request, "preview_book.html", {
        "book": book,
        "current_page": current_page,
        "page_number": page_number,
        "total_pages": total_pages,
    })

english_stopwords = set(stopwords.words("english"))
factory = StopWordRemoverFactory()
indonesian_stopwords = set(factory.get_stop_words())
combined_stopwords = english_stopwords.union(indonesian_stopwords)

def filter_keywords(text):
    words = re.findall(r'\w+', text)
    filtered_words = [word for word in words if word.lower() not in combined_stopwords]
    return " ".join(filtered_words)


def analyze_keywords(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Re-extract text every time the function is called
    if not book.pdf or not os.path.exists(book.pdf.path):
        return JsonResponse({"error": "No PDF file available."}, status=400)

    try:
        doc = pymupdf.open(book.pdf.path)
        text = "\n".join(page.get_text("text") for page in doc).strip()
    except Exception as e:
        return JsonResponse({"error": f"Failed to process PDF: {str(e)}"}, status=500)

    # If the PDF contains no text (e.g., scanned book)
    if not text:
        book.extracted_text = ""  # Save as empty string
        book.save()
        return JsonResponse({"keywords": []})  # Return empty list safely

    # Save the newly extracted text
    book.extracted_text = text
    book.save()

    # Filter text
    cleaned_text = filter_keywords(text).strip()

    if not cleaned_text:
        cleaned_text = "word_not_found"

    # TF-IDF Processing
    vectorizer = TfidfVectorizer(max_features=5)
    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned_text])
        keywords = vectorizer.get_feature_names_out()
    except ValueError:
        keywords = ["word_not_found"]  # Prevent errors

    return JsonResponse({"keywords": list(keywords)})