from django.db import models


class District(models.Model):
    """
    A district or location where a college is located.
    Examples: Kathmandu, Bhaktapur, Lalitpur, Pokhara, Chitwan.
    """
    name = models.CharField(max_length=100, unique=True)
    province = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class College(models.Model):
    """
    A college affiliated with Tribhuvan University.

    Every college is a "tenant" — its users, departments, students,
    teachers, notices, library, etc. all belong to this college.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True, help_text='Short unique code, e.g. KCT')
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name='colleges',
    )
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    principal_name = models.CharField(max_length=150, blank=True)
    established_date = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to='college_logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'