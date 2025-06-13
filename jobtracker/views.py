from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
from .forms import RegisterForm, JobApplicationForm
from .models import JobApplication
from xhtml2pdf import pisa
import csv



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'jobtracker/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('job_list')
        else:
            return render(request, 'jobtracker/login.html', {'error': 'Invalid username or password'})
    return render(request, 'jobtracker/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def dashboard(request):
    job_counts = JobApplication.objects.values('status').annotate(total=Count('status'))
    status_data = {status['status']: status['total'] for status in job_counts}

    total_jobs = JobApplication.objects.count()
    total_offers = status_data.get('offer', 0)
    total_rejected = status_data.get('rejected', 0)

    labels = list(status_data.keys())
    data = list(status_data.values())

    return render(request, 'jobtracker/dashboard.html', {
        'labels': labels,
        'data': data,
        'total_jobs': total_jobs,
        'total_offers': total_offers,
        'total_rejected': total_rejected,
    })



@login_required
def job_list(request):
    status_filter = request.GET.get('status')
    sort_order    = request.GET.get('sort',  'desc')
    search_query  = request.GET.get('search','')
    page_number   = request.GET.get('page',  1)

    #  Only this user’s jobs
    qs = JobApplication.objects.filter(user=request.user)

    if status_filter:
        qs = qs.filter(status=status_filter)

    if search_query:
        qs = qs.filter(
            Q(company__icontains=search_query) |
            Q(position__icontains=search_query)
        )

    qs = qs.order_by('applied_date' if sort_order=='asc' else '-applied_date')

    paginator = Paginator(qs, 10)
    page_obj  = paginator.get_page(page_number)

    return render(request, 'jobtracker/job_list.html', {
        'jobs':          page_obj,
        'status_filter': status_filter,
        'sort_order':    sort_order,
        'search_query':  search_query,
        'page_obj':      page_obj,
    })

@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user     # 🚩 assign owner
            job.save()
            messages.success(request, "Job added successfully.")
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    return render(request, 'jobtracker/job_form.html', {'form': form})

@login_required
def job_update(request, pk):
    #  only allow editing your own
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect('job_list')
    else:
        form = JobApplicationForm(instance=job)

    return render(request, 'jobtracker/job_form.html', {'form': form})

@login_required
def job_delete(request, pk):
    # 🚩 only allow deleting your own
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted.")
        return redirect('job_list')

    return render(request, 'jobtracker/job_confirm_delete.html', {'job': job})





# CSV export
@login_required
def export_csv(request):
    # Generate CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_applications.csv"'

    writer = csv.writer(response)
    writer.writerow(['Company', 'Position', 'Status', 'Applied Date', 'Notes', 'Resume URL'])
    for job in JobApplication.objects.all():
        writer.writerow([
            job.company,
            job.position,
            job.get_status_display(),
            job.applied_date.isoformat(),
            job.notes or '',
            request.build_absolute_uri(job.resume.url) if job.resume else ''
        ])
    return response

# PDF export
@login_required
def export_pdf(request):
    jobs = JobApplication.objects.all()
    # Build base URL (e.g. http://127.0.0.1:8000)
    domain = request.build_absolute_uri('/')[:-1]  # strip trailing slash

    # Render HTML with domain in context
    html = render_to_string(
        'jobtracker/pdf_template.html',
        {'jobs': jobs, 'domain': domain}
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="job_applications.pdf"'

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

