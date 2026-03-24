from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser


def register(request):
    """Register a new user as either a librarian or guest."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        middle_name = request.POST.get('middle_name', '')
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = int(request.POST.get('role', 0))  # 0 = visitor, 1 = librarian
        
        # Validation
        if not email or not password:
            return render(request, 'authentication/register.html', 
                        {'error': 'Email and password are required'})
        
        if password != password_confirm:
            return render(request, 'authentication/register.html',
                        {'error': 'Passwords do not match'})
        
        if CustomUser.objects.filter(email__iexact=email).exists():
            return render(request, 'authentication/register.html',
                        {'error': 'Email already exists'})
        
        # Create user
        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                role=role,
                is_active=True
            )
            login(request, user)
            return redirect('home')
        except Exception as e:
            return render(request, 'authentication/register.html',
                        {'error': str(e)})
    
    return render(request, 'authentication/register.html')


def login_view(request):
    """Login view for guests/users."""
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            return render(request, 'authentication/login.html',
                        {'error': 'Email and password are required'})
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'authentication/login.html',
                        {'error': 'Invalid email or password'})
    
    return render(request, 'authentication/login.html')


@login_required(login_url='login')
def logout_view(request):
    """Logout view for authorized users."""
    logout(request)
    return redirect('home')


def home(request):
    """Home page."""
    return render(request, 'home.html')


def user_list(request):
    """Display list of all users (admin only)."""
    if request.user.role == 1:
        users = CustomUser.objects.all()
        return render(request, 'authentication/user_list.html', {'users': users})
    return render(request, 'authentication/user_list.html', {'users': []})


def user_detail(request, user_id):
    """Display details of a specific user (admin only)."""
    if request.user.role == 1:
        object_user = CustomUser.get_by_id(user_id)
        return render(request, 'authentication/user_detail.html', {'object_user': object_user})
    return render(request, 'authentication/user_detail.html', {'object_user': None})
