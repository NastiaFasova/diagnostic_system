from django.contrib import messages
from django.shortcuts import render, redirect
from members.forms import RegistrationForm
from django.contrib.auth import authenticate, login, logout

from members.models import Diagnose


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if request.POST["password1"] != request.POST["password2"]:
            messages.error(request, "Ваші паролі не співпадають. Перевірте правильність введення")
            return redirect('register')
        if request.POST["username"] is None or request.POST["first_name"] is None or request.POST["last_name"] is None\
            or request.POST["email"] is None or request.POST["gender"] is None or request.POST["birthday"] is None \
                or request.POST["password1"] is None \
                or request.POST["password2"] is None:
            messages.error(request, "Заповніть усі поля реєстрації.")
            return redirect('register')
        if len(request.POST["password1"]) < 6:
            messages.error(request, "Пароль повинен містити мінімум 6 символів")
            return redirect('register')
        user = authenticate(request, username=request.POST["username"], password=request.POST["password1"])
        if user is not None:
            messages.error(request, "Користувач вже зареєстрований")
            return redirect('register')
        if form.is_valid():
            form.save()
            messages.success(request, "Ви успішно зареєструвались")
            return redirect('login_user')  # Redirect to login page after successful registration
        else:
            messages.error(request, "Ви не змогли зареєструватись успішно. Спробуйте ще раз")
            return redirect('register')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('request-form')
        else:
            messages.error(request, "Користувача із вказаними даними не знайдено.")
            return redirect('login_user')
    else:
        return render(request, "authenticate/login.html")


def logout_user(request):
    logout(request)
    return render(request, "expert_form.html")


def home(request):
    diagnoses = Diagnose.objects.filter(user=request.user)
    return render(request, "home.html", {'diagnoses': diagnoses})
