import requests
import json


def authenticate_with_leaf(leaf_username, leaf_password, remember_me=True):
  auth_url = "https://api.withleaf.io/api/authenticate"
  auth_data = {
      "username": leaf_username,
      "password": leaf_password,
      "rememberMe": str(remember_me).lower()
  }
  auth_response = requests.post(auth_url, json=auth_data)
  try: 
    return auth_response.json()['id_token']
  except Exception as e:
    print("problem authenticating, please try again ", e)


def get_fields(token,
               type=None,
               farmId=None,
               provider=None,
               leafUserId=None,
               page=0,
               size=100):
  fields_url = "https://api.withleaf.io/services/fields/api/fields"
  headers = {"Authorization": f"Bearer {token}"}
  all_fields = []

  while True:
    params = {
        "type": type,
        "farmId": farmId,
        "provider": provider,
        "leafUserId": leafUserId,
        "page": page,
        "size": size
    }
    fields_response = requests.get(fields_url, headers=headers, params=params)
    fields_data = fields_response.json()
    if not fields_data:
      break
    all_fields.extend(fields_data)
    page += 1
  return all_fields


def get_single_field(token, leafUserId, fieldId):
  single_field_url = f"https://api.withleaf.io/services/fields/api/users/{leafUserId}/fields/{fieldId}"
  headers = {"Authorization": f"Bearer {token}"}
  single_field_response = requests.get(single_field_url, headers=headers)
  single_field_data = single_field_response.json()
  return single_field_data


def get_operations(token,
                   leafUserId=None,
                   provider=None,
                   startTime=None,
                   updatedTime=None,
                   endTime=None,
                   operationType=None,
                   fieldId=None,
                   page=0,
                   size=None,
                   sort=None):
  operations_url = "https://api.withleaf.io/services/operations/api/operations"
  headers = {"Authorization": f"Bearer {token}"}
  all_operations = []

  while True:
    params = {
        "leafUserId": leafUserId,
        "provider": provider,
        "startTime": startTime,
        "updatedTime": updatedTime,
        "endTime": endTime,
        "operationType": operationType,
        "fieldId": fieldId,
        "page": page,
        "size": size,
        "sort": sort
    }
    operations_response = requests.get(operations_url,
                                       headers=headers,
                                       params=params)
    operations_data = operations_response.json()
    if not operations_data or (size is not None
                               and len(all_operations) >= size):
      break
    all_operations.extend(operations_data)
    page += 1
  return all_operations[:size] if size is not None else all_operations


def get_operation_summary(token, operation_id):
  operation_summary_url = f"https://api.withleaf.io/services/operations/api/operations/{operation_id}/summary"
  headers = {"Authorization": f"Bearer {token}"}
  operation_summary_response = requests.get(operation_summary_url,
                                            headers=headers)
  operation_summary_data = operation_summary_response.json()
  return operation_summary_data
