# your_app/management/commands/populate_data.py
# python manage.py populate_db
from django.core.management.base import BaseCommand
from oldbookapp.models import Category, Books
from .data import categories, books  # Importing from data.py
from datetime import datetime

class Command(BaseCommand):
    help = 'Seed the database with initial category and book data'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Books.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING('All existing data has been deleted.'))

        # Seed Category data
        for category_name in categories:
            category, created = Category.objects.get_or_create(category=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category "{category_name}" created'))
            else:
                self.stdout.write(self.style.WARNING(f'Category "{category_name}" already exists'))

        # Seed Books data
        for book_data in books:
            category = Category.objects.get(category=book_data['category'])
            book, created = Books.objects.get_or_create(
                ISBN=book_data['ISBN'],
                defaults={
                    'Book_Title': book_data['Book_Title'],
                    'Book_Author': book_data['Book_Author'],
                    'Description': book_data['Description'],
                    'Year_Of_Publication': book_data['Year_Of_Publication'],
                    'Publisher': book_data['Publisher'],
                    'Image_URL': book_data['Image_URL'],
                    'category': category,
                    'price':book_data['price'],
                    'created_at': datetime.fromisoformat(book_data['created_at'])  # Convert string to datetime
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Book "{book_data["Book_Title"]}" created'))
            else:
                self.stdout.write(self.style.WARNING(f'Book "{book_data["Book_Title"]}" already exists'))
