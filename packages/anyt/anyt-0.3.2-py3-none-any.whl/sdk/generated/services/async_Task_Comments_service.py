from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def list_task_comments_v1_workspaces__workspace_id__tasks__task_identifier__comments__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, limit : Optional[int] = None, offset : Optional[int] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> CommentListResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}/comments/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'limit' : limit,
'offset' : offset
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
        raise HTTPException(response.status_code, f'list_task_comments_v1_workspaces__workspace_id__tasks__task_identifier__comments__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return CommentListResponse(**body) if body is not None else CommentListResponse()
async def create_task_comment_v1_workspaces__workspace_id__tasks__task_identifier__comments__post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, data : CreateCommentRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> CommentResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}/comments/'
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
        raise HTTPException(response.status_code, f'create_task_comment_v1_workspaces__workspace_id__tasks__task_identifier__comments__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return CommentResponse(**body) if body is not None else CommentResponse()
async def get_task_comment_stats_v1_workspaces__workspace_id__tasks__task_identifier__comments_stats_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> CommentStatsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}/comments/stats'
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
        raise HTTPException(response.status_code, f'get_task_comment_stats_v1_workspaces__workspace_id__tasks__task_identifier__comments_stats_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return CommentStatsResponse(**body) if body is not None else CommentStatsResponse()