from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def list_goals_v1_workspaces__workspace_id__goals__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], status_filter : Optional[Union[str,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> List[GoalResponse]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/goals/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'status_filter' : status_filter
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
        raise HTTPException(response.status_code, f'list_goals_v1_workspaces__workspace_id__goals__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return [GoalResponse(**item) for item in body]
def create_goal_v1_workspaces__workspace_id__goals__post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], data : CreateGoalRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> GoalResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/goals/'
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
        raise HTTPException(response.status_code, f'create_goal_v1_workspaces__workspace_id__goals__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return GoalResponse(**body) if body is not None else GoalResponse()
def get_goal_v1_workspaces__workspace_id__goals__goal_id__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], goal_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> GoalResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/goals/{goal_id}'
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
        raise HTTPException(response.status_code, f'get_goal_v1_workspaces__workspace_id__goals__goal_id__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return GoalResponse(**body) if body is not None else GoalResponse()
def delete_goal_v1_workspaces__workspace_id__goals__goal_id__delete(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], goal_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/goals/{goal_id}'
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

    if response.status_code != 204:
        raise HTTPException(response.status_code, f'delete_goal_v1_workspaces__workspace_id__goals__goal_id__delete failed with status code: {response.status_code}')
    else:
                body = None if 204 == 204 else response.json()

    return None

def decompose_goal_v1_workspaces__workspace_id__goals__goal_id__decompose_post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], goal_id : int, data : DecompositionRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> DecompositionResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/goals/{goal_id}/decompose'
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

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'decompose_goal_v1_workspaces__workspace_id__goals__goal_id__decompose_post failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return DecompositionResponse(**body) if body is not None else DecompositionResponse()