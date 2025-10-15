from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def index(request):
    return render(request, 'index.html')
@login_required
def report(request):
    return render(request, 'report.html')
@login_required
def notification(request):
    return render(request, 'notification.html')

def logout_user(request):
    logout(request)
    return redirect("/")  # send user back to homepage after logout

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def auth_page(request):
    alert = False  # default: no alert

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")  # dashboard
        else:
            alert = True  # trigger alert in template

    # Pass 'alert' to template context
    return render(request, "homepage.html", {"alert": alert})




