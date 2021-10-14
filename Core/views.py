import json
import requests
from Core import models as core_models
from django.db import connection, connections
from decouple import config
from django.http import HttpResponse
from django.shortcuts import render
import pyodbc


him_services_received_url = config('HIM_SERVICES_RECEIVED_URL')
him_bed_occupancy_url = config('HIM_BED_OCCUPANCY_URL')
him_revenue_received_url = config('HIM_REVENUE_RECEIVED_URL')
him_death_by_disease_in_facility_url = config('HIM_DEATH_BY_DISEASE_IN_FACILITY_URL')
him_death_by_disease_outside_facility_url = config('HIM_DEATH_BY_DISEASE_OUTSIDE_FACILITY_URL')

him_username = config('HIM_USERNAME')
him_password = config('HIM_PASSWORD')

org_name = config('ORGANISATION_NAME')
facility_hfr_code = config('FACILITY_HFR_CODE')


# Create your views here.
def get_index_page(request):
    return render(request, 'Core/index.html', {"organisation_name": org_name, "facility_hfr_code":facility_hfr_code})


def import_icd_10_codes(request):
    icd10_url = "https://him-dev.moh.go.tz:5000/get-all-icd10-codes"
    icd10_payload = requests.get(icd10_url)
    data = json.loads(icd10_payload.content)

    for x in data:

        query = core_models.ICD10CodeCategory.objects.filter(local_id=x["id"]).first()

        if query is None:
            # # insert category
            instance_category = core_models.ICD10CodeCategory()
            instance_category.local_id = x["id"]
            instance_category.description = x["description"]
            instance_category.save()
        else:
            query.description = x["description"]
            query.save()

        sub_categories = x["sub_category"]

        for sub_category in sub_categories:
            sub_category_id = sub_category["id"]
            sub_category_name = sub_category['description']

            query = core_models.ICD10CodeSubCategory.objects.filter(local_id=sub_category_id).first()

            if query is None:
                # # insert sub category
                last_category = core_models.ICD10CodeCategory.objects.all().last()

                instance_sub_category = core_models.ICD10CodeSubCategory()
                instance_sub_category.local_id = sub_category_id
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

                query = core_models.ICD10Code.objects.filter(local_id=icd_10_id).first()

                if query is None:
                    # # insert icd code
                    instance_icd_code = core_models.ICD10Code()
                    last_sub_category = core_models.ICD10CodeSubCategory.objects.all().last()
                    instance_icd_code.sub_category_id =  last_sub_category.id
                    instance_icd_code.local_id = icd_10_id
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

                    query = core_models.ICD10SubCode.objects.filter(local_id=icd_10_sub_code_id).first()

                    if query is None:
                        # # insert icd sub code
                        instance_icd_sub_code = core_models.ICD10SubCode()

                        last_code = core_models.ICD10Code.objects.all().last()
                        instance_icd_sub_code.code_id = last_code.id
                        instance_icd_sub_code.local_id = icd_10_sub_code_id
                        instance_icd_sub_code.sub_code = icd_10_sub_code
                        instance_icd_sub_code.description = icd_10_sub_code_description
                        instance_icd_sub_code.save()
                    else:
                        query.sub_code = icd_10_sub_code
                        query.description = icd_10_sub_code_description
                        query.save()

    return HttpResponse("ICD10 codes uploaded to your system")


def import_cpt_codes(request):
    cpt_url = "https://him-dev.moh.go.tz:5000/get-all-cpt-codes"
    cpt_payload = requests.get(cpt_url)
    data = json.loads(cpt_payload.content)

    for x in data:
        # # insert category
        query = core_models.CPTCodeCategory.objects.filter(local_id=x["id"]).first()

        if query is None:
            instance_category = core_models.CPTCodeCategory()
            instance_category.local_id = x["id"]
            instance_category.description = x["description"]
            instance_category.save()
        else:
            query.description = x["description"]
            query.save()

        sub_categories = x["sub_category"]

        for sub_category in sub_categories:
            sub_category_id = sub_category["id"]
            sub_category_description = sub_category['description']

            query = core_models.CPTCodeSubCategory.objects.filter(local_id=sub_category_id).first()
            last_category = core_models.CPTCodeCategory.objects.all().last()

            if query is None:
                # insert sub category
                instance_sub_category = core_models.CPTCodeSubCategory()
                instance_sub_category.local_id = sub_category_id
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

                query = core_models.CPTCode.objects.filter(local_id=code_id).first()

                if query is None:
                    # # insert icd code
                    instance_cpt_code = core_models.CPTCode()
                    instance_cpt_code.sub_category_id = instance_sub_category.id
                    instance_cpt_code.local_id = code_id
                    instance_cpt_code.code = code_local_id
                    instance_cpt_code.description = code_description
                    instance_cpt_code.save()
                else:
                    query.code = code_id
                    query.description = code_description
                    query.save()

    return HttpResponse("CPT codes uploaded to your system")


def send_services_received_payload(request):
    if config("EMR_NAME") == "Jeeva":
        conn = pyodbc.connect('DSN=JEEVADB;UID=JEEVADB;PASSWORD=SVRJEEVAJV')
        cursor = conn.cursor()

        cursor.execute('''''' + config('SERVICES_RECEIVED_PAYLOAD') + '''''')

        row = cursor.fetchall()

    else:
        cursor = connection.cursor()

        with connections['data'].cursor() as cursor:
            cursor.execute('''''' + config('SERVICES_RECEIVED_PAYLOAD') + '''''')

            row = cursor.fetchall()

    services_received = row

    message_type = "SVCREC"

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

    if response.status_code == 200:
        return HttpResponse("Service received data uploaded")
    elif response.status_code == 401:
        return HttpResponse("Unauthorized access")
    else:
        return HttpResponse("failed")


def send_bed_occupancy_payload(request):
    if config("EMR_NAME") == "Jeeva":
        conn = pyodbc.connect('DSN=JEEVADB;UID=JEEVADB;PASSWORD=SVRJEEVAJV')
        cursor = conn.cursor()

        cursor.execute('''''' + config('BED_OCCUPANCY_PAYLOAD') + '''''')

        row = cursor.fetchall()

    else:
        cursor = connection.cursor()

        with connections['data'].cursor() as cursor:
            cursor.execute('''''' + config('BED_OCCUPANCY_PAYLOAD') + '''''')

            row = cursor.fetchall()

    bed_occupancies = row

    message_type = "BEDOCC"

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

    print(response.status_code)

    if response.status_code == 200:
        return HttpResponse("Bed Occupancy data uploaded")
    elif response.status_code == 401:
        return HttpResponse("Unauthorized access")
    else:
        return HttpResponse("failed")


def send_revenue_received_payload(request):
    if config("EMR_NAME") == "Jeeva":
        conn = pyodbc.connect('DSN=JEEVADB;UID=JEEVADB;PASSWORD=SVRJEEVAJV')
        cursor = conn.cursor()

        cursor.execute('''''' + config('REVENUE_RECEIVED_PAYLOAD') + '''''')

        row = cursor.fetchall()

    else:
        cursor = connection.cursor()

        with connections['data'].cursor() as cursor:
            cursor.execute('''''' + config('REVENUE_RECEIVED_PAYLOAD') + '''''')

            row = cursor.fetchall()

    revenue_received = row

    message_type = "REV"

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
        billed_amount = formatted_tuple[8]
        waived_amount = formatted_tuple[9]
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

    if response.status_code == 200:
        return HttpResponse("Revenue received data uploaded")
    elif response.status_code == 401:
        return HttpResponse("Unauthorized access")
    else:
        return HttpResponse("failed")


def send_death_by_disease_in_facility_payload(request):
    if config("EMR_NAME") == "Jeeva":
        conn = pyodbc.connect('DSN=JEEVADB;UID=JEEVADB;PASSWORD=SVRJEEVAJV')
        cursor = conn.cursor()

        cursor.execute('''''' + config('DEATH_IN_FACILITY_PAYLOAD') + '''''')

        row = cursor.fetchall()

    else:
        cursor = connection.cursor()

        with connections['data'].cursor() as cursor:
            cursor.execute('''''' + config('DEATH_IN_FACILITY_PAYLOAD') + '''''')

            row = cursor.fetchall()

    death_by_disease_in_facility = row

    message_type = "DDC"

    death_in_facility_items = []

    for death in death_by_disease_in_facility:
        formatted_tuple = tuple(death)

        ward_id = str(formatted_tuple[0])
        ward_name = str(formatted_tuple[1])
        patient_id = str(formatted_tuple[2])
        icd_10_code = str(formatted_tuple[3])
        gender = formatted_tuple[4]
        dob = str(formatted_tuple[5])
        date_death_occured = formatted_tuple[6]


        death_in_facility_object = {"wardId": ward_id, "wardName": ward_name,
                                   "patId": patient_id,
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

    if response.status_code == 200:
        return HttpResponse("Death in facility data uploaded")
    elif response.status_code == 401:
        return HttpResponse("Unauthorized access")
    else:
        return HttpResponse("failed")


def send_death_by_disease_outside_facility_payload(request):
    if config("EMR_NAME") == "Jeeva":
        conn = pyodbc.connect('DSN=JEEVADB;UID=JEEVADB;PASSWORD=SVRJEEVAJV')
        cursor = conn.cursor()

        cursor.execute('''''' + config('DEATH_OUTSIDE_FACILITY_PAYLOAD') + '''''')

        row = cursor.fetchall()

    else:
        cursor = connection.cursor()

        with connections['data'].cursor() as cursor:
            cursor.execute('''''' + config('DEATH_OUTSIDE_FACILITY_PAYLOAD') + '''''')

            row = cursor.fetchall()

    death_by_disease_outside_facility = row

    message_type = "DDCOUT"

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

    if response.status_code == 200:
        return HttpResponse("Death outside facility data uploaded")
    elif response.status_code == 401:
        return HttpResponse("Unauthorized access")
    else:
        return HttpResponse("failed")


