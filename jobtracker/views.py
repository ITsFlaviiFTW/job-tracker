from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
from .forms import RegisterForm, JobApplicationForm
from .models import JobApplication
from xhtml2pdf import pisa
from datetime import date
import csv
import requests

#DEMO imports
from django.contrib.auth import login as _login, authenticate
from django.conf import settings 



#==================DEMO STUFF======================
def auto_demo_login(view_func):
    def _wrapped(request, *args, **kwargs):
        if getattr(settings, 'DEMO_MODE', False) and not request.user.is_authenticated:
            user = authenticate(request, username='demo', password='demo')
            _login(request, user)
        if getattr(settings, 'DEMO_MODE', False) and not request.user.is_authenticated:
            user = authenticate(request, username='demo', password='demo')
            if user is not None:               # ← only log in if we got a real User
                _login(request, user)
        return view_func(request, *args, **kwargs)
    return _wrapped




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


@auto_demo_login       
@login_required
def dashboard(request):
    # only this user’s jobs
    qs = JobApplication.objects.filter(user=request.user)

    # count per status
    job_counts = qs.values('status').annotate(total=Count('status'))
    status_data = {item['status']: item['total'] for item in job_counts}

    # overall totals
    total_jobs     = qs.count()
    total_offers   = status_data.get('offer', 0)
    total_rejected = status_data.get('rejected', 0)

    # chart data
    labels = list(status_data.keys())
    data   = list(status_data.values())

    return render(request, 'jobtracker/dashboard.html', {
        'labels':         labels,
        'data':           data,
        'total_jobs':     total_jobs,
        'total_offers':   total_offers,
        'total_rejected': total_rejected,
    })


@auto_demo_login       
@login_required
def job_list(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            messages.success(request, "Job added successfully.")
            return redirect('job_list')  # Redirect to clear form on reload
    else:
        form = JobApplicationForm()

    status_filter = request.GET.get('status')
    sort_order    = request.GET.get('sort',  'desc')
    search_query  = request.GET.get('search','')
    page_number   = request.GET.get('page',  1)

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
        'form':          form,
        'status_filter': status_filter,
        'sort_order':    sort_order,
        'search_query':  search_query,
        'page_obj':      page_obj,
    })


@auto_demo_login       
@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user     # assigns owner
            job.save()

             # AJAX response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'id'           : job.pk,
                    'company'      : job.company,
                    'position'     : job.position,
                    'status'       : job.get_status_display(),
                    'status_key'   : job.status,
                    'applied_date' : job.applied_date.strftime('%B %-d, %Y'),
                    'notes'        : job.notes or '',
                    'resume_url'   : job.resume.url if job.resume else '',
                })
            # normal fallback
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
    # only allow deleting your own
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted.")
        return redirect('job_list')

    return render(request, 'jobtracker/job_confirm_delete.html', {'job': job})



# AJAX EDITING
@login_required
@require_http_methods(["GET"])
def job_detail_json(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    return JsonResponse({
        'id'           : job.pk,
        'company'      : job.company,
        'position'     : job.position,
        'status_key'   : job.status,
        'status'       : job.get_status_display(),
        'applied_date' : job.applied_date.strftime('%Y-%m-%d'),
        'notes'        : job.notes or '',
        'resume_url'   : job.resume.url if job.resume else '',
    })

@login_required
@require_http_methods(["POST"])
def job_update_ajax(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    form = JobApplicationForm(request.POST, request.FILES, instance=job)

    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    job = form.save()

    return JsonResponse({
        'id'           : job.pk,
        'company'      : job.company,
        'position'     : job.position,
        'status_key'   : job.status,
        'status'       : job.get_status_display(),
        'applied_date' : job.applied_date.strftime('%B %d, %Y'),  # ✅ Fixed format
        'notes'        : job.notes or '',
        'resume_url'   : job.resume.url if job.resume else '',
    })



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


# Jobs API searcher
@auto_demo_login       
@login_required
def explore_jobs(request):
    jobs = []
    try:
        response = requests.get("https://remotive.com/api/remote-jobs?category=software-dev", timeout=5)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])
    except Exception as e:
        print("[ERROR]", e)

    #Filtering
    search = request.GET.get("search", "").lower()
    location = request.GET.get("location", "").lower()

    if search:
        jobs = [job for job in jobs if search in job["title"].lower() or search in job["company_name"].lower()]
    if location:
        jobs = [job for job in jobs if location in job["candidate_required_location"].lower()]


    # Pagination for API searcher
    paginator = Paginator(jobs, 12)  # Show 10 jobs per page
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "jobtracker/explore_jobs.html", {
        "page_obj": page_obj,
        "jobs": page_obj.object_list,
    })


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def save_remote_job(request):
    title   = request.POST.get("title")
    company = request.POST.get("company")
    job = JobApplication.objects.create(
        user=request.user,
        position=title,
        company=company,
        applied_date=date.today(),
        status="Applied"  # or any default status you prefer
    )
    return JsonResponse({"status": "saved", "id": job.id})




