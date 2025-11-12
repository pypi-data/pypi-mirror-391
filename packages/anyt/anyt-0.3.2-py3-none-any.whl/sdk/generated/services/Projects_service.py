from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def list_projects_v1_workspaces__workspace_id__projects__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], page : Optional[int] = None, per_page : Optional[int] = None, status : Optional[Union[str,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> ProjectListResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'page' : page,
'per_page' : per_page,
'status' : status
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'list_projects_v1_workspaces__workspace_id__projects__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return ProjectListResponse(**body) if body is not None else ProjectListResponse()
def create_project_v1_workspaces__workspace_id__projects__post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], data : CreateProjectRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Project:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'post',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 201:
        raise HTTPException(response.status_code, f'create_project_v1_workspaces__workspace_id__projects__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return Project(**body) if body is not None else Project()
def get_current_project_v1_workspaces__workspace_id__projects_current_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Project:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/current'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'get_current_project_v1_workspaces__workspace_id__projects_current_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Project(**body) if body is not None else Project()
def get_project_v1_workspaces__workspace_id__projects__project_id__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Project:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'get_project_v1_workspaces__workspace_id__projects__project_id__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Project(**body) if body is not None else Project()
def delete_project_v1_workspaces__workspace_id__projects__project_id__delete(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'delete',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'delete_project_v1_workspaces__workspace_id__projects__project_id__delete failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return body

def update_project_v1_workspaces__workspace_id__projects__project_id__patch(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, data : ProjectUpdate, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Project:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'patch',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'update_project_v1_workspaces__workspace_id__projects__project_id__patch failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Project(**body) if body is not None else Project()