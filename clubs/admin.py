from django.contrib import admin
from .models import Club, Membership, ClubAnnouncement


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    autocomplete_fields = ['user']
    readonly_fields = ['requested_at', 'reviewed_at']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'college', 'coordinator',
                    'member_count', 'pending_count', 'is_active']
    list_filter = ['category', 'is_active', 'college']
    search_fields = ['name', 'description']
    autocomplete_fields = ['coordinator', 'created_by']
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'club', 'role', 'status', 'requested_at', 'reviewed_by']
    list_filter = ['status', 'role', 'club']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'club__name']
    autocomplete_fields = ['user', 'club', 'reviewed_by']


@admin.register(ClubAnnouncement)
class ClubAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'posted_by', 'created_at']
    list_filter = ['club']
    search_fields = ['title', 'body']
    autocomplete_fields = ['club', 'posted_by']