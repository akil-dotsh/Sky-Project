# Author: Akil Hossain
# Student ID: 20270054

from django.shortcuts import render

# Temporary view used to preview and test the dashboard UI template in the browser.
def test_ui(request):
    return render(request, "dashboard/test_ui.html")
