from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Author


@login_required(login_url='login')
def author_list(request):
    """Show all authors (admin only)."""
    # Check if user is librarian (admin)
    if request.user.role != 1:
        return render(request, 'error.html',
                    {'error': 'You do not have permission to access this page'}, status=403)
    
    authors = Author.objects.all()
    context = {'authors': authors}
    return render(request, 'author/author_list.html', context)


@login_required(login_url='login')
def create_author(request):
    """Create a new author (admin only)."""
    # Check if user is librarian (admin)
    if request.user.role != 1:
        return render(request, 'error.html',
                    {'error': 'You do not have permission to access this page'}, status=403)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        surname = request.POST.get('surname', '')
        patronymic = request.POST.get('patronymic', '')
        
        # Validation
        if not name or not surname or not patronymic:
            return render(request, 'author/create_author.html',
                        {'error': 'All fields are required'})
        
        if len(name) > 20 or len(surname) > 20 or len(patronymic) > 20:
            return render(request, 'author/create_author.html',
                        {'error': 'Field length should not exceed 20 characters'})
        
        author = Author.create(name=name, surname=surname, patronymic=patronymic)
        
        if author:
            return redirect('authors')
        else:
            return render(request, 'author/create_author.html',
                        {'error': 'Failed to create author'})
    
    return render(request, 'author/create_author.html')


@login_required(login_url='login')
def delete_author(request, author_id):
    """Remove an author if not attached to any book (admin only)."""
    # Check if user is librarian (admin)
    if request.user.role != 1:
        return render(request, 'error.html',
                    {'error': 'You do not have permission to access this page'}, status=403)
    
    author = get_object_or_404(Author, id=author_id)
    
    if request.method == 'POST':
        # Check if author has books
        if author.books.exists():
            return render(request, 'error.html',
                        {'error': 'Cannot delete author with books'}, status=400)
        
        author.delete()
        return redirect('authors')
    
    context = {'author': author}
    return render(request, 'author/delete_author.html', context)
