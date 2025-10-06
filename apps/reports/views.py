from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def generate(request, id):
    """Generate PDF report"""
    return HttpResponse("Report generation coming soon")

@login_required
def download(request, id):
    """Download PDF report"""
    return HttpResponse("Report download coming soon")
