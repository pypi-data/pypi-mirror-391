from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def workspaceslist(api_config_override : Optional[APIConfig] = None, *, page : Optional[int] = None, per_page : Optional[int] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> WorkspaceListResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/'
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
'per_page' : per_page
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'workspaceslist failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return WorkspaceListResponse(**body) if body is not None else WorkspaceListResponse()
async def workspacescreate(api_config_override : Optional[APIConfig] = None, *, data : CreateWorkspaceRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Workspace:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/'
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

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'post',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 201:
        raise HTTPException(response.status_code, f'workspacescreate failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return Workspace(**body) if body is not None else Workspace()
async def workspacesget_current(api_config_override : Optional[APIConfig] = None, *, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Workspace:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/current'
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

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'workspacesget_current failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Workspace(**body) if body is not None else Workspace()
async def workspacesget(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Workspace:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}'
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

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'workspacesget failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Workspace(**body) if body is not None else Workspace()
async def workspacesdelete(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}'
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

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'delete',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f'workspacesdelete failed with status code: {response.status_code}')
    else:
                body = None if 204 == 204 else response.json()

    return None

async def workspacesupdate(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, data : WorkspaceUpdate, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Workspace:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}'
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

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'patch',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'workspacesupdate failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Workspace(**body) if body is not None else Workspace()