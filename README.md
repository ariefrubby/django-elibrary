# Django E-Library

## 📌 Project Description
This is a **Django-based E-Library** website that allows users to:
- **Upload books** (PDFs) with metadata.
- **Extract text** from PDFs.
- **Analyze keywords** from book content.
- **Mark books as favorites**.
- **Search for books** by title, description, or genre.
- **View book pages** as images.

---

## 🚀 Getting Started
Follow these steps to run the project locally.

### **1️⃣ Clone the Repository**
```sh
 git clone https://github.com/ariefrubby/django-elibrary.git
 cd django-library
```

### **2️⃣ Create a Virtual Environment**
```sh
python -m venv venv
```
> **For macOS/Linux users:**
> ```sh
> source venv/bin/activate
> ```
> **For Windows users:**
> ```sh
> venv\Scripts\activate
> ```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Set Up the Database**
```sh
python manage.py makemigrations
python manage.py migrate
```

### **5️⃣ Create a Superuser (For Admin Panel)**
```sh
python manage.py createsuperuser
```
Enter your **username, email, and password** when prompted.

### **6️⃣ Run the Development Server**
```sh
python manage.py runserver
```
Your project will be accessible at: **`http://127.0.0.1:8000/`**

---

## 🛠 Features
- **User Authentication** (Login/Registration)
- **Book Upload with Cover Image Extraction**
- **PDF Text Extraction**
- **Keyword Analysis Using TF-IDF**
- **Favorite Books Management**
- **Pagination & Search Functionality**

---

---

## 🔑 Admin Panel Access
- Open **`http://127.0.0.1:8000/admin/`**
- Login with the **superuser** credentials you created earlier.

---

## 📝 Notes
- If you encounter **missing dependencies**, install them manually:
  ```sh
  pip install django pymupdf scikit-learn nltk Sastrawi
  ```
- If using **SQLite**, the database file is `db.sqlite3`. For a fresh start, delete it and re-run migrations.
- Make sure **Media Files** (uploaded books & images) are correctly configured in `settings.py`:
  ```python
  MEDIA_URL = '/media/'
  MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  ```
