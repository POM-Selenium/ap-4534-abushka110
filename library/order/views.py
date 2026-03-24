from django.shortcuts import render, redirect
from .models import Order
from book.models import Book
from django.utils import timezone

def all_orders(request):
    if request.user.role == 1:
        orders = Order.get_all()
        return render(request, 'order/all_orders.html', {'orders': orders})

def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order/my_orders.html', {'orders': orders})

def create_order(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        plated_end_at = request.POST.get('plated_end_at')
        book = Book.get_by_id(book_id)
        
        Order.create(user=request.user, book=book, plated_end_at=plated_end_at)
        return redirect('my_orders')
    
    books = Book.get_all()
    return render(request, 'order/create_order.html', {'books': books})

def close_order(request, order_id):
    if request.user.role == 1:
        order = Order.get_by_id(order_id)
        if order:
            order.update(end_at=timezone.now())
        return redirect('all_orders')