from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User
from colleges.models import College, District


def register_view(request):
    """Public signup page. Students and teachers can self-register.
    College admins are created by TU Admins via the admin panel."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'student')
        college_id = request.POST.get('college', '')

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email:
            errors.append('Email is required.')
        if password1 != password2:
            errors.append('Passwords do not match.')
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters.')
        if role not in ('student', 'teacher'):
            errors.append('Invalid role. Only students and teachers can self-register.')
        if not college_id:
            errors.append('Please select a college.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already taken.')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'auth/register.html', {
                'districts': District.objects.all(),
                'colleges': College.objects.filter(status='active'),
                'form_data': request.POST,
            })

        # Create user
        try:
            college = College.objects.get(id=college_id, status='active')
        except College.DoesNotExist:
            messages.error(request, 'Invalid college.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            college=college,
        )

        login(request, user)
        messages.success(request, f'Welcome to TU Platform, {user.get_full_name() or user.username}!')
        return redirect('home')

    return render(request, 'auth/register.html', {
        'districts': District.objects.all(),
        'colleges': College.objects.filter(status='active'),
    })


def login_view(request):
    """Custom login page for students, teachers, college admins, TU admins."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'auth/login.html')

        # Try username first, then email
        user = authenticate(request, username=username, password=password)
        if user is None:
            try:
                u = User.objects.get(Q(username=username) | Q(email=username.lower()))
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'auth/login.html')


def logout_view(request):
    """Log out and return to landing page."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')