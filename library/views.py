from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Book, BookIssue, LibrarySettings


def _get_settings(college):
    """Get or create library settings for a college."""
    s, _ = LibrarySettings.objects.get_or_create(college=college)
    return s


def _visible_books(user):
    if user.is_tu_admin:
        return Book.objects.all()
    if user.college:
        return Book.objects.filter(college=user.college)
    return Book.objects.none()


@login_required
def book_list(request):
    """Browse / search the catalog."""
    books = _visible_books(request.user)

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(isbn__icontains=q) |
            Q(publisher__icontains=q)
        )
    if category:
        books = books.filter(category=category)

    return render(request, 'library/list.html', {
        'books': books,
        'q': q,
        'category': category,
        'category_choices': Book.CATEGORY_CHOICES,
    })


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not request.user.is_tu_admin and request.user.college != book.college:
        messages.error(request, 'Access denied.')
        return redirect('book_list')

    # Show history to staff only
    is_staff_view = request.user.is_tu_admin or request.user.is_college_admin or request.user.is_staff
    issues = book.issues.select_related('borrower').order_by('-issued_at') if is_staff_view else []

    # My active issue for this book?
    my_issue = BookIssue.objects.filter(
        book=book, borrower=request.user, status='issued'
    ).first()

    return render(request, 'library/detail.html', {
        'book': book,
        'issues': issues,
        'my_issue': my_issue,
        'is_staff_view': is_staff_view,
    })


@login_required
def my_books(request):
    """Student/teacher's borrowed books."""
    issues = BookIssue.objects.filter(borrower=request.user).select_related('book')

    active = issues.filter(status='issued')
    history = issues.exclude(status='issued')

    return render(request, 'library/my_books.html', {
        'active': active,
        'history': history,
    })


@login_required
def issue_book(request, pk):
    """Staff issues a book to a borrower."""
    if not (request.user.is_tu_admin or request.user.is_college_admin or request.user.is_staff):
        messages.error(request, 'Only library staff can issue books.')
        return redirect('book_list')

    book = get_object_or_404(Book, pk=pk)
    if not request.user.is_tu_admin and request.user.college != book.college:
        messages.error(request, 'Access denied.')
        return redirect('book_list')

    if not book.is_available:
        messages.error(request, 'No copies available right now.')
        return redirect('book_detail', pk=pk)

    settings_obj = _get_settings(book.college)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            borrower = User.objects.get(username=username)
        except Exception:
            messages.error(request, 'No user found with that username.')
            return redirect('issue_book', pk=pk)

        # Check max books limit
        active_count = BookIssue.objects.filter(borrower=borrower, status='issued').count()
        if active_count >= settings_obj.max_books_per_user:
            messages.error(request, f'{borrower.username} has reached the limit of {settings_obj.max_books_per_user} books.')
            return redirect('issue_book', pk=pk)

        # Create issue
        BookIssue.objects.create(
            book=book,
            borrower=borrower,
            issued_by=request.user,
            due_date=timezone.now().date() + timedelta(days=settings_obj.loan_days),
        )
        messages.success(request, f'Issued "{book.title}" to {borrower.username}.')
        return redirect('book_detail', pk=pk)

    return render(request, 'library/issue.html', {'book': book})


@login_required
def return_book(request, pk, issue_id):
    """Staff returns a book (calculates fine)."""
    if not (request.user.is_tu_admin or request.user.is_college_admin or request.user.is_staff):
        messages.error(request, 'Only library staff can process returns.')
        return redirect('book_list')

    issue = get_object_or_404(BookIssue, pk=issue_id, book_id=pk)
    if issue.status != 'issued':
        messages.error(request, 'This book is already returned or marked lost.')
        return redirect('book_detail', pk=pk)

    if request.method == 'POST':
        settings_obj = _get_settings(issue.book.college)
        issue.returned_at = timezone.now()
        issue.status = 'returned'
        issue.fine_amount = issue.calculate_fine(settings_obj.fine_per_day)
        issue.save()
        messages.success(request, f'Book returned. Fine: Rs. {issue.fine_amount}')
        return redirect('book_detail', pk=pk)

    return redirect('book_detail', pk=pk)


@login_required
def overdue_list(request):
    """Staff sees all overdue books."""
    if not (request.user.is_tu_admin or request.user.is_college_admin or request.user.is_staff):
        messages.error(request, 'Only staff can view overdue books.')
        return redirect('book_list')

    qs = BookIssue.objects.filter(status='issued').select_related('book', 'borrower')
    if not request.user.is_tu_admin:
        qs = qs.filter(book__college=request.user.college)

    overdue = [i for i in qs if i.is_overdue]

    return render(request, 'library/overdue.html', {
        'overdue': overdue,
    })