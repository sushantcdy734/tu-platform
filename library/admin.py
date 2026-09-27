from django.contrib import admin
from .models import Book, BookIssue, LibrarySettings


class BookIssueInline(admin.TabularInline):
    model = BookIssue
    extra = 0
    autocomplete_fields = ['borrower']
    readonly_fields = ['issued_at', 'returned_at']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'college',
                    'total_copies', 'available_copies', 'shelf_location']
    list_filter = ['category', 'college']
    search_fields = ['title', 'author', 'isbn', 'publisher']
    inlines = [BookIssueInline]

    def available_copies(self, obj):
        return obj.available_copies
    available_copies.short_description = 'Available'


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'borrower', 'status', 'issued_at', 'due_date',
                    'returned_at', 'fine_amount', 'fine_paid']
    list_filter = ['status', 'fine_paid', 'book__college']
    search_fields = ['book__title', 'borrower__username', 'borrower__first_name']
    autocomplete_fields = ['book', 'borrower', 'issued_by']
    readonly_fields = ['issued_at']


@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
    list_display = ['college', 'loan_days', 'fine_per_day', 'max_books_per_user']
    search_fields = ['college__name']