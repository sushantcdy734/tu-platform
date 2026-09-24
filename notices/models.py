from django.db import models
from django.conf import settings


class Notice(models.Model):
    """
    A notice / announcement posted at one of three scopes:
      - tu         → visible to all authenticated users
      - college    → visible to users of a specific college
      - department → visible to users of a specific department
    """
    SCOPE_CHOICES = [
        ('tu', 'TU-wide'),
        ('college', 'College-wide'),
        ('department', 'Department'),
    ]

    title = models.CharField(max_length=300)
    body = models.TextField()
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='college')

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notices',
        help_text='Required for college and department notices.',
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notices',
        help_text='Required only for department notices.',
    )

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notices_posted',
    )

    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_scope_display()}] {self.title}'

    @staticmethod
    def visible_to(user):
        """
        Return the queryset of notices a given user can see.
        Called from views. Enforces the multi-tenant rules.
        """
        if not user.is_authenticated:
            return Notice.objects.none()

        # TU admins see everything
        if user.is_tu_admin:
            return Notice.objects.filter(is_published=True)

        qs = Notice.objects.filter(is_published=True)

        # Everyone in a college sees: TU-wide + their college's notices + their department's notices
        if user.college:
            department_ids = []
            if hasattr(user, 'teacher_profile') and user.teacher_profile.department:
                department_ids.append(user.teacher_profile.department_id)
            if hasattr(user, 'student_profile') and user.student_profile.program:
                department_ids.append(user.student_profile.program.department_id)

            return qs.filter(
                models.Q(scope='tu') |
                models.Q(scope='college', college=user.college) |
                models.Q(scope='department', department_id__in=department_ids)
            ).distinct()

        # Fallback: only TU-wide notices
        return qs.filter(scope='tu')