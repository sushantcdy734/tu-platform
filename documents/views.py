from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import DocumentRequest


def _visible(user):
    """Only same-college requests visible; TU admin sees all."""
    if user.is_tu_admin:
        return DocumentRequest.objects.all()
    if user.college:
        return DocumentRequest.objects.filter(college=user.college)
    return DocumentRequest.objects.none()


@login_required
def document_list(request):
    qs = _visible(request.user)
    if request.user.is_student:
        qs = qs.filter(student=request.user)

    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)

    return render(request, 'documents/list.html', {
        'requests': qs,
        'status_choices': DocumentRequest.STATUS_CHOICES,
        'current_status': status,
    })


@login_required
def document_create(request):
    if not request.user.is_student:
        messages.error(request, 'Only students can request documents.')
        return redirect('document_list')

    if not request.user.college:
        messages.error(request, 'You need to be part of a college first.')
        return redirect('document_list')

    if request.method == 'POST':
        doc_type = request.POST.get('document_type', '')
        purpose = request.POST.get('purpose', '').strip()
        try:
            copies = max(1, int(request.POST.get('copies', 1)))
        except (TypeError, ValueError):
            copies = 1

        if not doc_type or not purpose:
            messages.error(request, 'Document type and purpose are required.')
            return render(request, 'documents/create.html', {
                'type_choices': DocumentRequest.DOCUMENT_TYPES,
                'form_data': request.POST,
            })

        req = DocumentRequest.objects.create(
            college=request.user.college,
            student=request.user,
            document_type=doc_type,
            purpose=purpose,
            copies=copies,
        )
        messages.success(request, f'Request #{req.id} submitted.')
        return redirect('document_detail', pk=req.id)

    return render(request, 'documents/create.html', {
        'type_choices': DocumentRequest.DOCUMENT_TYPES,
    })


@login_required
def document_detail(request, pk):
    req = get_object_or_404(DocumentRequest, pk=pk)

    if not request.user.is_tu_admin:
        if request.user.college != req.college:
            messages.error(request, 'Access denied.')
            return redirect('document_list')
        if request.user.is_student and req.student != request.user:
            messages.error(request, 'You can only view your own requests.')
            return redirect('document_list')

    if request.method == 'POST':
        if request.user.is_student:
            messages.error(request, 'Only staff can update requests.')
            return redirect('document_detail', pk=pk)

        new_status = request.POST.get('status', '').strip()
        note = request.POST.get('admin_note', '').strip()

        if new_status and new_status in dict(DocumentRequest.STATUS_CHOICES):
            req.status = new_status
            if new_status == 'ready' and not req.ready_at:
                req.ready_at = timezone.now()
            if new_status == 'delivered' and not req.delivered_at:
                req.delivered_at = timezone.now()

        req.admin_note = note
        req.handled_by = request.user
        req.save()

        messages.success(request, f'Request #{req.id} updated.')
        return redirect('document_detail', pk=pk)

    return render(request, 'documents/detail.html', {
        'req': req,
        'status_choices': DocumentRequest.STATUS_CHOICES,
    })