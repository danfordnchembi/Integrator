from django.urls import path
from UserManagement.views import main
from Core import views as core_views


urlpatterns = [
    path('', main.get_login_page, name='login_page'),
    path('password/', main.change_password, name='change_password'),
    path('user', main.authenticate_user, name='authenticate_user'),
    path('accounts/login/', main.change_password, name='login_required_page'),
    path('logout', main.logout_view, name='logout'),
    path('upload_cpt_codes', core_views.upload_cpt_codes, name='upload_cpt_codes'),
    path('download_cpt_codes_as_csv', core_views.download_cpt_codes_as_csv, name='download_cpt_codes_as_csv'),

]