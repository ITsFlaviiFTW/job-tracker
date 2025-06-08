from django.shortcuts import render, redirect
from .models import JobApplication
from .forms import JobApplicationForm

def job_list(request):
    jobs = JobApplication.objects.all()
    return render(request, 'jobtracker/job_list.html', {'jobs': jobs})

def job_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    return render(request, 'jobtracker/job_form.html', {'form': form})
