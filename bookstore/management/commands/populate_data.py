from django.core.management.base import BaseCommand
from bookstore.models import Author, Category, Book
from decimal import Decimal
from datetime import date
from django.core.files.base import ContentFile
import requests
import io

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):

        authors_data = [
            {
                'name': 'George Orwell', 
                'bio': 'English novelist and essayist known for his dystopian novels.',
                'placeholder': 'https://via.placeholder.com/300x300?text=George+Orwell'
            },
            {
                'name': 'Jane Austen', 
                'bio': 'English novelist known for her social commentary and wit.',
                'placeholder': 'https://via.placeholder.com/300x300?text=Jane+Austen'
            },
            {
                'name': 'Stephen King', 
                'bio': 'American author of horror, supernatural fiction.',
                'placeholder': 'https://via.placeholder.com/300x300?text=Stephen+King'
            },
        ]
        
        authors = []
        for author_data in authors_data:
            placeholder_url = author_data.pop('placeholder')
            author, created = Author.objects.get_or_create(
                name=author_data['name'],
                defaults=author_data
            )
            authors.append(author)
            if created:
                self.stdout.write(f"Created author: {author.name}")


        # Create Categories
        categories_data = [
            'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 
            'Mystery', 'Romance', 'Thriller', 'Biography'
        ]
        
        categories = []
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(name=cat_name)
            categories.append(category)
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create Books
        books_data = [
            {
                'title': '1984',
                'author': authors[0],
                'price': Decimal('15.99'),
                'isbn': '9780451524935',
                'stock_quantity': 50,
                'categories': ['Fiction', 'Science Fiction']
            },
            {
                'title': 'Pride and Prejudice',
                'author': authors[1],
                'price': Decimal('12.99'),
                'isbn': '9780141439518',
                'stock_quantity': 30,
                'categories': ['Fiction', 'Romance']
            },
            {
                'title': 'The Shining',
                'author': authors[2],
                'price': Decimal('18.99'),
                'isbn': '9780307743657',
                'stock_quantity': 25,
                'categories': ['Fiction', 'Thriller']
            },
        ]
        
        for book_data in books_data:
            category_names = book_data.pop('categories')
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults=book_data
            )
            if created:
                for cat_name in category_names:
                    category = Category.objects.get(name=cat_name)
                    book.categories.add(category)
                self.stdout.write(f"Created book: {book.title}")

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
