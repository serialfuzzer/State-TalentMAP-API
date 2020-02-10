import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
import talentmap_api.fsbid.services.cdo as cdo_services
import talentmap_api.fsbid.services.available_positions as services_ap
import csv
from copy import deepcopy
from datetime import datetime
from django.conf import settings
from urllib.parse import urlencode, quote
from django.http import HttpResponse
from django.utils.encoding import smart_str

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def client(jwt_token, query):
    '''
    Get Clients by CDO
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"CDOClients?request_params.ad_id={ad_id}&{convert_client_query(query)}"
    print(uri)
    response = services.get_fsbid_results(uri, jwt_token, fsbid_clients_to_talentmap_clients)
    return response

def client_suggestions(jwt_token, perdet_seq_num):
    '''
    Get a suggestion for a client
    '''

    # if less than LOW, try broader query
    LOW = 5
    # but also don't go too high
    HIGH = 100
    # but going over HIGH is preferred over FLOOR
    FLOOR = 0

    client = single_client(jwt_token, perdet_seq_num)
    grade = client.get("grade")
    skills = client.get("skills")
    skills = deepcopy(skills)
    mappedSkills = ','.join([str(x.get("code")) for x in skills])

    values = {
        "position__grade__code__in": grade,
        "position__skill__code__in": mappedSkills,
    }

    # Dictionary for the next grade "up"
    nextGrades = {
        "08": "07",
        "07": "06",
        "06": "05",
        "05": "04",
        "04": "03",
        "02": "01",
    }

    count = services_ap.get_available_positions_count(values, jwt_token)
    count = int(count.get("count"))

    # If we get too few results, try a broader query
    if count < LOW and nextGrades.get(grade) is not None:
        nextGrade = nextGrades.get(grade)
        values2 = deepcopy(values)
        values2["position__grade__code__in"] = f"{grade},{nextGrade}"
        count2 = services_ap.get_available_positions_count(values2, jwt_token)
        count2 = int(count2.get("count"))
        # Only use our broader query if the first one <= FLOOR OR the second < HIGH, and the counts don't match
        if (count <= FLOOR or count2 < HIGH) and count != count2:
            values = values2

    # Finally, return the query
    return values

def single_client(jwt_token, perdet_seq_num):
    '''
    Get a single client for a CDO
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    uri = f"CDOClients?request_params.ad_id={ad_id}&request_params.perdet_seq_num={perdet_seq_num}"
    response = services.get_fsbid_results(uri, jwt_token, fsbid_clients_to_talentmap_clients)
    cdo = cdo_services.single_cdo(jwt_token, perdet_seq_num)
    client = list(response)[0]
    client['cdo'] = cdo
    return client

def get_client_csv(query, jwt_token, rl_cd, host=None):
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    data = services.send_get_csv_request(
        "CDOClients",
        query,
        convert_client_query,
        jwt_token,
        fsbid_clients_to_talentmap_clients_for_csv,
        "/api/v1/fsbid/client/",
        host,
        ad_id
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=clients_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Skill"),
        smart_str(u"Grade"),
        smart_str(u"Employee ID"),
        # smart_str(u"Role Code"), Might not be useful to users
        smart_str(u"Position Location Code"),
    ])

    for record in data:
        writer.writerow([
            smart_str(record["name"]),
            smart_str(record["skills"]),
            smart_str("=\"%s\"" % record["grade"]),
            smart_str("=\"%s\"" % record["employee_id"]),
            # smart_str(record["role_code"]), Might not be useful to users
            smart_str("=\"%s\"" % record["pos_location_code"]),
        ])
    return response


def fsbid_clients_to_talentmap_clients(data):
    employee = data.get('employee', None)
    current_assignment = employee.get('currentAssignment', None)
    position = current_assignment.get('currentPosition', None)    
    return {
        "id": employee.get("pert_external_id", None),
        "name": f"{employee.get('per_first_name', None)} {employee.get('per_last_name', None)}",
        "perdet_seq_number": data.get("perdet_seq_num", None),
        "grade": employee.get("per_grade_code", None),
        "skills": map_skill_codes(employee),
        "employee_id": employee.get("pert_external_id", None),
        "role_code": data.get("rl_cd", None),
        "pos_location_code": position.get("pos_location_code", None),
        "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd"))
    }

def fsbid_clients_to_talentmap_clients_for_csv(data):
    employee = data.get('employee', None)
    current_assignment = employee.get('currentAssignment', None)
    position = current_assignment.get('currentPosition', None)
    return {
        "id": employee.get("pert_external_id", None),
        "name": f"{employee.get('per_first_name', None)} {employee.get('per_last_name', None)}",
        "grade": employee.get("per_grade_code", None),
        "skills": ' , '.join(map_skill_codes_for_csv(employee)),
        "employee_id": employee.get("pert_external_id", None),
        "role_code": data.get("rl_cd", None),
        "pos_location_code": position.get("pos_location_code", None),
        "hasHandshake": fsbid_handshake_to_tmap(data.get("hs_cd"))
    }

def convert_client_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the client search filter naming
    '''
    values = {
        "request_params.hru_id": query.get("hru_id", None),
        "request_params.rl_cd": query.get("rl_cd", None),
        "request_params.ad_id": query.get("ad_id", None),
        "request_params.hasHandshake": query.get("hs_cd", None),
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.freeText": query.get("q", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

def map_skill_codes_for_csv(data):
    skills = []
    for i in range(1,4):
        index = f'_{i}'
        if i == 1:
            index = ''
        desc = data.get(f'per_skill{index}_code_desc', None)
        skills.append(desc)
    return filter(lambda x: x is not None, skills)

def map_skill_codes(data):
    skills = []
    for i in range(1,4):
        index = f'_{i}'
        if i == 1:
            index = ''
        code = data.get(f'per_skill{index}_code', None)
        desc = data.get(f'per_skill{index}_code_desc', None)
        skills.append({ 'code': code, 'description': desc })
    return filter(lambda x: x.get('code', None) is not None, skills)

def fsbid_handshake_to_tmap(hs):
    # Maps FSBid Y/N value for handshakes to expected TMap Front end response for handshake
    fsbid_dictionary = {
        "Y": "true",
        "N": "false",
    }
    return fsbid_dictionary.get(hs, None)

def tmap_handshake_to_fsbid(hs):
    # Maps TMap true/false value to acceptable fsbid api params for handshake
    tmap_dictionary = {
        "true": "Y",
        "false": "N"
    }
    return tmap_dictionary.get(hs, None)