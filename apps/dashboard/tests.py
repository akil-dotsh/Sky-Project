from django.test import TestCase
from django.shortcuts import render

# Create your tests here.
def test_ui(request):
    return render(request,"dashboard/test_ui.html")
