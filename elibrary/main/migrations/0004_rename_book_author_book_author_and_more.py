# Generated by Django 5.1.6 on 2025-02-14 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_user_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='book_author',
            new_name='author',
        ),
        migrations.RemoveField(
            model_name='book',
            name='book_cover',
        ),
        migrations.RemoveField(
            model_name='book',
            name='keyword',
        ),
        migrations.RemoveField(
            model_name='book',
            name='page_amount',
        ),
        migrations.RemoveField(
            model_name='book',
            name='uploaded_file',
        ),
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='books/covers/'),
        ),
        migrations.AddField(
            model_name='book',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='books/pdfs/'),
        ),
        migrations.AlterField(
            model_name='bookpage',
            name='image',
            field=models.ImageField(upload_to='books/pages/'),
        ),
    ]
