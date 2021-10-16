"""Integrator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.get_index_page, name=''),
    path('import_icd10_codes/', core_views.import_icd_10_codes, name="import_icd10_codes"),
    path('import_cpt_codes/', core_views.import_cpt_codes, name="import_cpt_codes"),

    path('send_services_received/', core_views.send_services_received_payload, name="send_services_received"),
    path('send_revenue_received/', core_views.send_revenue_received_payload, name="send_revenue_received"),
    path('send_bed_occupancy/', core_views.send_bed_occupancy_payload, name="send_bed_occupancy"),
    path('send_death_outside_facility/', core_views.send_death_by_disease_outside_facility_payload,
         name="send_death_outside_facility"),
    path('send_death_in_facility/', core_views.send_death_by_disease_in_facility_payload, name="send_death_in_facility"),
    path('download_cpt_codes_as_csv', core_views.download_cpt_codes_as_csv, name='download_cpt_codes_as_csv'),
    path('upload_cpt_codes', core_views.upload_cpt_codes, name='upload_cpt_codes'),
]
