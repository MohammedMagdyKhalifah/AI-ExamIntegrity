from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import proctor_required


@proctor_required
def proctor_dashboard(request):
    """
    Renders the proctor dashboard page.
    """
    return render(request, 'proctor/proctor_dashboard.html')