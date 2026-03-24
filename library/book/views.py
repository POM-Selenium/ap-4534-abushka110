from django.shortcuts import render, get_object_or_404
from .models import Book
from order.models import Order
from django.db.models import Q

def book_list(request):
    query = request.GET.get('search')
    if query:
        books = Book.objects.filter(
            Q(name__icontains=query) | 
            Q(authors__surname__icontains=query)
        ).distinct()
    else:
        books = Book.get_all()
    
    return render(request, 'book/book_list.html', {'books': books})

def book_detail(request, book_id):
    book = Book.get_by_id(book_id)
    return render(request, 'book/book_detail.html', {'book': book})

def user_books(request, user_id):
    if request.user.is_authenticated and request.user.role == 1:
        orders = Order.objects.filter(user_id=user_id, end_at__isnull=True)
        return render(request, 'book/user_books.html', {'orders': orders})
    else:
        return render(request, 'book/user_books.html', {'orders': []})
