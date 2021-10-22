import json
import requests
from Core import models as core_models
from django.db import connection, connections
from decouple import config
from django.http import HttpResponse
from django.shortcuts import render, redirect
import pyodbc
import csv
from Core import forms as core_forms
from Core import tables as core_tables
from django.core.files.storage import FileSystemStorage
from django_tables2 import RequestConfig
from .models import Query, PayloadConfig
from datetime import datetime
# from celery import Celery

# app = Celery()

him_services_received_url = config('HIM_SERVICES_RECEIVED_URL')
him_bed_occupancy_url = config('HIM_BED_OCCUPANCY_URL')
him_revenue_received_url = config('HIM_REVENUE_RECEIVED_URL')
him_death_by_disease_in_facility_url = config('HIM_DEATH_BY_DISEASE_IN_FACILITY_URL')
him_death_by_disease_outside_facility_url = config('HIM_DEATH_BY_DISEASE_OUTSIDE_FACILITY_URL')

source_username = config('SOURCE_DB_USER')
source_password = config('SOURCE_DB_PASSWORD')
source_dsn = config('SOURCE_DB_NAME')


him_username = config('HIM_USERNAME')
him_password = config('HIM_PASSWORD')

org_name = config('ORGANISATION_NAME')
facility_hfr_code = config('FACILITY_HFR_CODE')


# Create your views here.
def get_index_page(request):
    cpt_code = core_models.CPTCode.objects.all()
    cpt_code_mappings_table = core_tables.CPTCodeMappingTable(cpt_code)
    cpt_code_mapping_import_form = core_forms.CPTCodeMappingImportForm()
    cpt_code_mapping_form = core_forms.CPTCodesMappingForm()
    RequestConfig(request, paginate={"per_page": 50}).configure(cpt_code_mappings_table)

    return render(request,'Core/index.html', {"organisation_name": org_name, "facility_hfr_code":facility_hfr_code,
                                              "cpt_code_mappings_table": cpt_code_mappings_table,
                                              "cpt_code_mapping_import_form":cpt_code_mapping_import_form,
                                              "cpt_code_mapping_form":cpt_code_mapping_form
                                              })

# @app.task
def import_icd_10_codes(request):
    icd10_url = "https://him-dev.moh.go.tz:5000/get-all-icd10-codes"
    icd10_payload = requests.get(icd10_url)
    data = json.loads(icd10_payload.content)

    for x in data:

        query = core_models.ICD10CodeCategory.objects.filter(hdr_local_id=x["id"]).first()

        if query is None:
            # # insert category
            instance_category = core_models.ICD10CodeCategory()
            instance_category.hdr_local_id = x["id"]
            instance_category.description = x["description"]
            instance_category.save()
        else:
            query.description = x["description"]
            query.save()

        sub_categories = x["sub_category"]

        for sub_category in sub_categories:
            sub_category_id = sub_category["id"]
            sub_category_name = sub_category['description']

            query = core_models.ICD10CodeSubCategory.objects.filter(hdr_local_id=sub_category_id).first()

            if query is None:
                # # insert sub category
                last_category = core_models.ICD10CodeCategory.objects.all().last()

                instance_sub_category = core_models.ICD10CodeSubCategory()
                instance_sub_category.hdr_local_id = sub_category_id
                instance_sub_category.description = sub_category_name
                instance_sub_category.category_id = last_category.id
                instance_sub_category.save()
            else:
                query.description = sub_category_name
                query.save()

            sub_sub_categories = sub_category['code']


            # loop through the sub sub categories
            for sub_sub_category in sub_sub_categories:
                icd_10_id = sub_sub_category["id"]
                icd_10_code = sub_sub_category["code"]
                icd_10_description = sub_sub_category["description"]

                query = core_models.ICD10Code.objects.filter(hdr_local_id=icd_10_id).first()

                if query is None:
                    # # insert icd code
                    instance_icd_code = core_models.ICD10Code()
                    last_sub_category = core_models.ICD10CodeSubCategory.objects.all().last()
                    instance_icd_code.sub_category_id =  last_sub_category.id
                    instance_icd_code.hdr_local_id = icd_10_id
                    instance_icd_code.code = icd_10_code
                    instance_icd_code.description = icd_10_description
                    instance_icd_code.save()
                else:
                    query.code=icd_10_code
                    query.description = icd_10_description
                    query.save()

                icd_sub_code_array = sub_sub_category["sub_code"]

                for y in icd_sub_code_array:
                    icd_10_sub_code_id = y["id"]
                    icd_10_sub_code = y["sub_code"]
                    icd_10_sub_code_description = y["description"]

                    query = core_models.ICD10SubCode.objects.filter(hdr_local_id=icd_10_sub_code_id).first()

                    if query is None:
                        # # insert icd sub code
                        instance_icd_sub_code = core_models.ICD10SubCode()

                        last_code = core_models.ICD10Code.objects.all().last()
                        instance_icd_sub_code.code_id = last_code.id
                        instance_icd_sub_code.hdr_local_id = icd_10_sub_code_id
                        instance_icd_sub_code.sub_code = icd_10_sub_code
                        instance_icd_sub_code.description = icd_10_sub_code_description
                        instance_icd_sub_code.save()
                    else:
                        query.sub_code = icd_10_sub_code
                        query.description = icd_10_sub_code_description
                        query.save()

    return HttpResponse("ICD10 codes uploaded to your system")

# @app.task
def import_cpt_codes(request):
    cpt_url = "https://him-dev.moh.go.tz:5000/get-all-cpt-codes"
    cpt_payload = requests.get(cpt_url)
    data = json.loads(cpt_payload.content)

    print(data)

    for x in data:
        # # insert category
        print(x["id"])
        query = core_models.CPTCodeCategory.objects.filter(hdr_local_id=x["id"]).first()

        if query is None:
            instance_category = core_models.CPTCodeCategory()
            instance_category.hdr_local_id = x["id"]
            instance_category.description = x["description"]
            instance_category.save()
        else:
            query.description = x["description"]
            query.save()

        sub_categories = x["sub_category"]

        for sub_category in sub_categories:
            sub_category_id = sub_category["id"]
            sub_category_description = sub_category['description']

            query = core_models.CPTCodeSubCategory.objects.filter(hdr_local_id=sub_category_id).first()
            last_category = core_models.CPTCodeCategory.objects.all().last()

            if query is None:
                # insert sub category
                instance_sub_category = core_models.CPTCodeSubCategory()
                instance_sub_category.hdr_local_id = sub_category_id
                instance_sub_category.description = sub_category_description
                instance_sub_category.category_id = last_category.id
                instance_sub_category.save()
            else:
                query.description = sub_category_description
                query.save()

            codes = sub_category['code']

            # loop through the sub sub categories
            for code in codes:
                code_id = code["id"]
                code_local_id = code["code"]
                code_description = code['description']

                query = core_models.CPTCode.objects.filter(hdr_local_id=code_id).first()
                last_sub_category = core_models.CPTCodeSubCategory.objects.all().last()

                if query is None:
                    # # insert icd code
                    instance_cpt_code = core_models.CPTCode()
                    instance_cpt_code.sub_category_id = last_sub_category.id
                    instance_cpt_code.hdr_local_id = code_id
                    instance_cpt_code.code = code_local_id
                    instance_cpt_code.description = code_description
                    instance_cpt_code.save()
                else:
                    query.code = code_local_id
                    query.description = code_description
                    query.save()

    return HttpResponse("CPT codes uploaded to your system")

# @app.task
def send_services_received_payload(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]

        message_type = "SVCREC"

        last_response = None

        queries = Query.objects.filter(message_type = message_type)
        payload_config = PayloadConfig.objects.filter(message_type = message_type).first()

        chunk_size = payload_config.chunk_size

        for query in queries:
            sql = query.sql_statement
            conditional_field = query.condition_field
            date_format = query.date_format

            transaction_status = False #Transaction is still pending

            format_sql = sql.replace(";", "")

            initial_chunk_size = 0

            while transaction_status is False:
                sql_limit = str(initial_chunk_size) + "," + str(chunk_size)

                final_sql_statement = format_sql + " WHERE 1=1 AND " + "" + conditional_field + "" + " >= '" + "" + convert_date_formats(
                    date_from,date_format) + "" + "' AND " + "" + conditional_field + "" + " <= '" + "" + convert_date_formats(
                    date_to, date_format) + "" "' LIMIT("+sql_limit+")"

                print(final_sql_statement)

                if config("EMR_NAME") == "Jeeva" or config("EMR_NAME") == "MediPro":
                    dsn_conn = pyodbc.connect('DSN=' + source_dsn + ';UID=' + source_username + ';PASSWORD=' + source_password + '')

                    cursor = dsn_conn.cursor()

                    cursor.execute('''''' + final_sql_statement + '''''')

                    row = cursor.fetchall()
                    print(row)

                else:
                    cursor = connection.cursor()

                    with connections['data'].cursor() as cursor:
                        cursor.execute('''''' + final_sql_statement + '''''')

                    row = cursor.fetchall()

                services_received = row

                service_received_items = []

                for service_received in services_received:
                    formatted_tuple = tuple(service_received)

                    dept_id = formatted_tuple[0]
                    dept_name = formatted_tuple[1]
                    patient_id = formatted_tuple[2]
                    gender = formatted_tuple[3]
                    dob = str(formatted_tuple[4])
                    med_svc_code = formatted_tuple[5]
                    icd_10_code = formatted_tuple[6]
                    service_date = str(formatted_tuple[7])
                    service_provider_ranking_id = str(formatted_tuple[8])
                    visit_type = formatted_tuple[9]

                    service_received_object = {"deptName": dept_name, "deptId": dept_id, "patId": patient_id,
                                               "gender": gender, "dob": dob, "medSvcCode":med_svc_code, "icd10Code": icd_10_code,
                                               "serviceDate":service_date,"serviceProviderRankingId": service_provider_ranking_id, "visitType":visit_type}
                    print(service_received_object)
                    service_received_items.append(service_received_object)

                payload = {
                    "messageType": message_type,
                    "orgName": org_name,
                    "facilityHfrCode": facility_hfr_code,
                    "items": service_received_items
                }

                json_payload = json.dumps(payload)

                response = requests.post(him_services_received_url, auth=(him_username, him_password), data=json_payload,
                                         headers={'User-Agent': 'XY', 'Content-type': 'application/json'})

                last_response = response

                initial_chunk_size += chunk_size
                chunk_size += chunk_size

                if final_sql_statement.count() > 0:
                    transaction_status = False
                else:
                    transaction_status = True

        if last_response.status_code == 200:
            return HttpResponse("Service received data uploaded")
        elif last_response.status_code == 401:
            return HttpResponse("Unauthorized access")
        else:
            return HttpResponse("General Failed")

# @app.task
def send_bed_occupancy_payload(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]

        message_type = "BEDOCC"
        queries = Query.objects.filter(message_type=message_type)
        last_response = None

        for query in queries:
            sql = query.sql_statement
            conditional_field = query.condition_field
            date_format = query.date_format

            format_sql = sql.replace(";", "")

            final_sql_statement = format_sql + " WHERE 1=1 AND " + "" + conditional_field + "" + " >= '"+ "" + convert_date_formats(
                date_from,date_format) + "" + "' AND " + "" + conditional_field + "" + " <= '" + "" + convert_date_formats(date_to, date_format) + "" "'"

            print(final_sql_statement)

            if config("EMR_NAME") == "Jeeva" or config("EMR_NAME") == "MediPro":
                dsn_conn = pyodbc.connect('DSN=' + source_dsn + ';UID=' + source_username + ';PASSWORD=' + source_password + '')
                cursor = dsn_conn.cursor()

                cursor.execute('''''' + final_sql_statement + '''''')

                row = cursor.fetchall()

            else:
                cursor = connection.cursor()

                with connections['data'].cursor() as cursor:
                    cursor.execute('''''' + final_sql_statement + '''''')

                    row = cursor.fetchall()

            bed_occupancies = row

            bed_occupancy_items = []

            for bed_occupancy in bed_occupancies:
                formatted_tuple = tuple(bed_occupancy)

                ward_id = formatted_tuple[0]
                ward_name = formatted_tuple[1]
                patient_id = formatted_tuple[2]
                admission_date = str(formatted_tuple[3])
                discharge_date = str(formatted_tuple[4])

                bed_occupancy_object = {"wardId": ward_id, "wardName": ward_name, "patId": patient_id,
                                        "admissionDate": admission_date, "dischargeDate": discharge_date}

                bed_occupancy_items.append(bed_occupancy_object)


            payload = {
                "messageType": message_type,
                "orgName": org_name,
                "facilityHfrCode": facility_hfr_code,
                "items": bed_occupancy_items
            }

            json_payload = json.dumps(payload)

            response = requests.post(him_bed_occupancy_url, auth=(him_username, him_password), data=json_payload,
                                     headers={'User-Agent': 'XY', 'Content-type': 'application/json'})

            last_response = response

        if last_response.status_code == 200:
            return HttpResponse("Bed Occupancy data uploaded")
        elif last_response.status_code == 401:
            return HttpResponse("Unauthorized access")
        else:
            return HttpResponse("failed")

# @app.task
def send_revenue_received_payload(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]

        message_type = "REV"
        queries = Query.objects.filter(message_type=message_type)

        last_response = None

        for query in queries:
            sql = query.sql_statement
            conditional_field = query.condition_field
            date_format = query.date_format

            format_sql = sql.replace(";", "")
            print("date is", convert_date_formats(date_from, date_format))
            final_sql_statement = format_sql + " WHERE 1=1 AND " + "" + conditional_field + "" + " >= '" + "" + convert_date_formats(
                date_from,
                date_format) + "" + "' AND " + "" + conditional_field + "" + " <= '" + "" + convert_date_formats(
                date_to, date_format) + "" "'"
            print(final_sql_statement)

            if config("EMR_NAME") == "Jeeva" or config("EMR_NAME") == "MediPro":
                dsn_conn = pyodbc.connect('DSN=' + source_dsn + ';UID=' + source_username + ';PASSWORD=' + source_password + '')
                cursor = dsn_conn.cursor()

                cursor.execute('''''' + final_sql_statement + '''''')

                row = cursor.fetchall()

            else:
                cursor = connection.cursor()

                with connections['data'].cursor() as cursor:
                    cursor.execute('''''' + final_sql_statement + '''''')

                    row = cursor.fetchall()

            revenue_received = row

            revenue_received_items = []

            for revenue in revenue_received:
                formatted_tuple = tuple(revenue)

                system_trans_id = str(formatted_tuple[0])
                transaction_date = str(formatted_tuple[1])
                patient_id = str(formatted_tuple[2])
                gender = formatted_tuple[3]
                dob = str(formatted_tuple[4])
                med_svc_code = formatted_tuple[5]
                payer_id = str(formatted_tuple[6])
                exemption_category_id = str(formatted_tuple[7])
                billed_amount = int(formatted_tuple[8])
                waived_amount = int(formatted_tuple[9])
                service_provider_ranking_id = str(formatted_tuple[10])

                revenue_received_object = {"systemTransId": system_trans_id, "transactionDate": transaction_date, "patId": patient_id,
                                           "gender": gender, "dob": dob, "medSvcCode": med_svc_code, "payerId": payer_id,
                                           "exemptionCategoryId": exemption_category_id, "billedAmount": billed_amount,
                                           "waivedAmount": waived_amount, "serviceProviderRankingId": service_provider_ranking_id}

                revenue_received_items.append(revenue_received_object)

            payload = {
                "messageType": message_type,
                "orgName": org_name,
                "facilityHfrCode": facility_hfr_code,
                "items": revenue_received_items
            }

            json_payload = json.dumps(payload)

            response = requests.post(him_revenue_received_url, auth=(him_username, him_password), data=json_payload,
                                     headers={'User-Agent': 'XY', 'Content-type': 'application/json'})

            last_response = response

        if last_response.status_code == 200:
            return HttpResponse("Revenue received data uploaded")
        elif last_response.status_code == 401:
            return HttpResponse("Unauthorized access")
        else:
            return HttpResponse("failed")

# @app.task
def send_death_by_disease_in_facility_payload(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]

        message_type = "DDC"
        queries = Query.objects.filter(message_type=message_type)
        last_response = None

        for query in queries:
            sql = query.sql_statement
            conditional_field = query.condition_field
            date_format = query.date_format

            format_sql = sql.replace(";", "")
            print("date is", convert_date_formats(date_from, date_format))
            final_sql_statement = format_sql + " WHERE 1=1 AND " + "" + conditional_field + "" + " >= '" + "" + convert_date_formats(
                date_from,
                date_format) + "" + "' AND " + "" + conditional_field + "" + " <= '" + "" + convert_date_formats(
                date_to, date_format) + "" "'"

            print(final_sql_statement)

            if config("EMR_NAME") == "Jeeva" or config("EMR_NAME") == "MediPro":
                dsn_conn = pyodbc.connect('DSN=' + source_dsn + ';UID=' + source_username + ';PASSWORD=' + source_password + '')
                cursor = dsn_conn.cursor()

                cursor.execute('''''' + final_sql_statement + '''''')

                row = cursor.fetchall()

            else:
                cursor = connection.cursor()

                with connections['data'].cursor() as cursor:
                    cursor.execute('''''' + final_sql_statement + '''''')

                    row = cursor.fetchall()

            death_by_disease_in_facility = row

            death_in_facility_items = []

            for death in death_by_disease_in_facility:
                formatted_tuple = tuple(death)

                ward_id = str(formatted_tuple[0])
                ward_name = str(formatted_tuple[1])
                patient_id = str(formatted_tuple[2])
                first_name = str(formatted_tuple[3])
                middle_name = str(formatted_tuple[4])

                if str(formatted_tuple[5]) != "":
                    last_name = str(formatted_tuple[5])
                else:
                    last_name = "-"

                icd_10_code = str(formatted_tuple[6])
                gender = formatted_tuple[7]
                dob = str(formatted_tuple[8])
                date_death_occured = formatted_tuple[9]


                death_in_facility_object = {"wardId": ward_id, "wardName": ward_name,
                                            "patId": patient_id,"firstName":first_name, "middleName":middle_name,
                                            "lastName":last_name,
                                            "icd10Code": icd_10_code, "gender": gender, "dob": dob,
                                            "dateDeathOccurred": date_death_occured}

                death_in_facility_items.append(death_in_facility_object)

            payload = {
                "messageType": message_type,
                "orgName": org_name,
                "facilityHfrCode": facility_hfr_code,
                "items": death_in_facility_items
            }

            json_payload = json.dumps(payload)

            response = requests.post(him_death_by_disease_in_facility_url, auth=(him_username, him_password), data=json_payload,
                                     headers={'User-Agent': 'XY', 'Content-type': 'application/json'})

            last_response = response

        if last_response.status_code == 200:
            return HttpResponse("Death in facility data uploaded")
        elif last_response.status_code == 401:
            return HttpResponse("Unauthorized access")
        else:
            return HttpResponse("failed")

# @app.task
def send_death_by_disease_outside_facility_payload(request):
    if request.method == "POST":
        date_from = request.POST["date_from"]
        date_to = request.POST["date_to"]

        message_type = "DDCOUT"
        queries = Query.objects.filter(message_type=message_type)
        last_response = None

        for query in queries:
            sql = query.sql_statement
            conditional_field = query.condition_field
            date_format = query.date_format

            format_sql = sql.replace(";", "")
            print("date is", convert_date_formats(date_from, date_format))
            final_sql_statement = format_sql + " WHERE 1=1 AND " + "" + conditional_field + "" + " >= " + "" + convert_date_formats(
                date_from,
                date_format) + "" + " AND " + "" + conditional_field + "" + " <= " + "" + convert_date_formats(date_to,
                                                                                                               date_format) + ""
            print(final_sql_statement)

            if config("EMR_NAME") == "Jeeva" or config("EMR_NAME") == "MediPro":
                dsn_conn = pyodbc.connect('DSN=' + source_dsn + ';UID=' + source_username + ';PASSWORD=' + source_password + '')
                cursor = dsn_conn.cursor()

                cursor.execute('''''' + final_sql_statement + '''''')

                row = cursor.fetchall()

            else:
                cursor = connection.cursor()

                with connections['data'].cursor() as cursor:
                    cursor.execute('''''' + final_sql_statement + '''''')

                    row = cursor.fetchall()

            death_by_disease_outside_facility = row

            death_outside_facility_items = []

            for death in death_by_disease_outside_facility:
                formatted_tuple = tuple(death)

                death_id = str(formatted_tuple[0])
                place_of_death_id = str(formatted_tuple[1])
                icd_10_code = str(formatted_tuple[3])
                gender = formatted_tuple[4]
                dob = str(formatted_tuple[5])
                date_death_occured = formatted_tuple[6]

                death_in_facility_object = {"deathId": death_id, "placeOfDeathId": place_of_death_id,
                                            "icd10Code": icd_10_code,
                                            "gender": gender, "dob": dob, "dateDeathOccurred": date_death_occured}

                death_outside_facility_items.append(death_in_facility_object)

            payload = {
                "messageType": message_type,
                "orgName": org_name,
                "facilityHfrCode": facility_hfr_code,
                "items": death_outside_facility_items
            }

            json_payload = json.dumps(payload)

            response = requests.post(him_death_by_disease_outside_facility_url, auth=(him_username, him_password), data=json_payload,
                                     headers={'User-Agent': 'XY', 'Content-type': 'application/json'})

            last_response = response

        if last_response.status_code == 200:
            return HttpResponse("Death outside facility data uploaded")
        elif last_response.status_code == 401:
            return HttpResponse("Unauthorized access")
        else:
            return HttpResponse("Failed")


def download_cpt_codes_as_csv(request):
    queryset = core_models.CPTCode.objects.all()
    opts = queryset.model._meta
    model = queryset.model
    response = HttpResponse(content_type='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=CPTCodesMappings.csv'
    # the csv writer
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    # field_names.append('local_code')
    # Write a first row with header information
    writer.writerow(field_names)

    # Write data rows
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response


def upload_cpt_codes(request):
    if request.method == "POST":
        cpt_codes_import_form = core_forms.CPTCodeMappingImportForm(request.POST, request.FILES)
        if cpt_codes_import_form.is_valid():
            cpt_codes_import_form.full_clean()

            file = cpt_codes_import_form.cleaned_data['file']

            if not file.name.endswith('.csv'):
                pass
            else:
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_path = fs.path(filename)
                update_cpt_code_entries(file_path, fs, file)
        return redirect(request.META['HTTP_REFERER'])


def update_cpt_code_entries(file_path, fs, file):

    with open(file_path, 'r') as fp:
        lines = csv.reader(fp, delimiter=',')

        row = 0
        for line in lines:
            if line is not None:
                if row == 0:
                    headers = line
                    row = row + 1
                else:
                    instance = core_models.CPTCode.objects.get(id=line[0])
                    instance.local_code = line[5]
                    instance.save()
            row = row + 1
    fs.delete(file.name)
    fp.close()


def save_new_cpt_code(request):
    if request.method == "POST":
        cpt_codes_mapping_form = core_forms.CPTCodesMappingForm(request.POST)

        if cpt_codes_mapping_form.is_valid():
            cpt_codes_mapping_form.full_clean()
            cpt_codes_mapping_form.save()
            return redirect(request.META['HTTP_REFERER'])


def update_cpt_code(request, item_pk):
    instance_cpt_code = core_models.CPTCode.objects.get(id=item_pk)
    form = core_forms.CPTCodesMappingForm(instance=instance_cpt_code)

    if request.method == "POST":
        if request.POST:
            form_cpt_code = core_forms.CPTCodesMappingForm(request.POST, instance=instance_cpt_code)
            if form_cpt_code.is_valid():
                form_cpt_code.save()
                return redirect(request.META['HTTP_REFERER'])
            else:
                pass
    else:
        header = "Update CPT code"
        url = "update_cpt_code"

        return render(request, 'Core/UpdateItem.html', {'form': form, 'header': header,
                                                        'item_pk': item_pk, "url": url
                                                        })

    return redirect(request.META['HTTP_REFERER'])


def convert_date_formats(date, date_format):

    try:
        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime(date_format)
        return formatted_date
    except ValueError:
        pass
