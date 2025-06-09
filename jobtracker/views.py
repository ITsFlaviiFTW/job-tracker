from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from .forms import RegisterForm, JobApplicationForm
from .models import JobApplication

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
def job_list(request):
    jobs = JobApplication.objects.all()
    return render(request, 'jobtracker/job_list.html', {'jobs': jobs})

@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    return render(request, 'jobtracker/job_form.html', {'form': form})

@login_required
def job_update(request, pk):
    job = get_object_or_404(JobApplication, pk=pk)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobApplicationForm(instance=job)
    return render(request, 'jobtracker/job_form.html', {'form': form})
