from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Book(models.Model):
    """A book in the library catalog."""
    CATEGORY_CHOICES = [
        ('textbook', 'Textbook'),
        ('reference', 'Reference'),
        ('fiction', 'Fiction'),
        ('nonfiction', 'Non-Fiction'),
        ('journal', 'Journal'),
        ('magazine', 'Magazine'),
        ('other', 'Other'),
    ]

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='books',
    )
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, blank=True, help_text='ISBN-10 or ISBN-13')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='textbook')
    publisher = models.CharField(max_length=200, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    total_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True, help_text='e.g. "A-12"')
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        unique_together = [['college', 'isbn']] if False else []

    def __str__(self):
        return f'{self.title} — {self.author}'

    @property
    def issued_count(self):
        return self.issues.filter(status='issued').count()

    @property
    def available_copies(self):
        return max(0, self.total_copies - self.issued_count)

    @property
    def is_available(self):
        return self.available_copies > 0


class BookIssue(models.Model):
    """A book issued to a student or teacher."""
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_issues',
    )

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='books_issued',
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')

    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)

    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.book.title} → {self.borrower.username} ({self.status})'

    @property
    def days_overdue(self):
        if self.status == 'returned' and self.returned_at:
            return max(0, (self.returned_at.date() - self.due_date).days)
        if self.status == 'issued':
            return max(0, (timezone.now().date() - self.due_date).days)
        return 0

    @property
    def is_overdue(self):
        return self.status == 'issued' and self.days_overdue > 0

    def calculate_fine(self, rate_per_day=5):
        """Fine = Rs. 5 per day overdue by default."""
        return self.days_overdue * rate_per_day

    @property
    def status_color(self):
        if self.status == 'returned':
            return 'success'
        if self.status == 'lost':
            return 'danger'
        if self.is_overdue:
            return 'danger'
        return 'primary'


class LibrarySettings(models.Model):
    """Per-college library config."""
    college = models.OneToOneField(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='library_settings',
    )
    loan_days = models.PositiveIntegerField(default=14, help_text='Default loan period')
    fine_per_day = models.PositiveIntegerField(default=5, help_text='Fine in Rs per overdue day')
    max_books_per_user = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f'Library settings — {self.college.code}'