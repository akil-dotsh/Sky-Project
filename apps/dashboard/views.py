from django.shortcuts import render

# Create your views here.
def staff_dashboard(request):
    return render(request, "dashboard/staff_dashboard.html")

def management_dashboard(request):
    return render(request,"dashboard/management_dashboard.html")