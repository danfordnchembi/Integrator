from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig
import xlwt
from Core import views as core_views
import requests
import json
from decouple import config
from django.contrib.auth.models import User


hdr_authentication_url = config("HDR_AUTHENTICATION_URL")

def get_login_page(request):
    return render(request, 'UserManagement/Auth/Login.html')


@login_required(login_url='/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(request.META['HTTP_REFERER'])

        else:
            messages.error(request, 'Please correct the error below.')
            return redirect(request.META['HTTP_REFERER'])
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'UserManagement/Auth/ChangePassword.html', {
            'form': form
        })


@login_required(login_url='/')
def logout_view(request):
    logout(request)
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))



def authenticate_user(request):

    username = request.POST['username']
    password = request.POST['password']

    url = hdr_authentication_url

    login_object = {"username": username, "password":password}
    login_json_object = json.dumps(login_object)

    response = requests.post(url, data=login_json_object,headers={'User-Agent': 'XY', 'Content-type': 'application/json'} )
    status = response.status_code

    if status == 200:
        # return core_views.get_index_page(request)
        add_or_update_user(username, password)
        return redirect('/index')
    else:
        messages.success(request, 'User name or Password is wrong')
        return render(request, 'UserManagement/Auth/Login.html')


def add_or_update_user(username, password):
    instance = User.objects.filter(username=username)
    instance.delete()

    user = User.objects.create_user(username=username,
                                        password= password, is_staff=True, is_superuser=True)
    user.save()


