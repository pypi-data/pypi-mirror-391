"""
Prompt CLI

Click 기반의 명령줄 인터페이스입니다.
핵심 CRUD 기능만 제공합니다.
"""

import click
import json
import os
from typing import Optional, List

try:
    from adxp_sdk.prompts.prompt_client import PromptClient
    from adxp_sdk.prompts.prompt_schemas import PromptCreateRequest, PromptUpdateRequest
except ImportError:
    # 직접 실행할 때를 위한 절대 import
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sdk'))
    from adxp_sdk.prompts.prompt_client import PromptClient
    from adxp_sdk.prompts.prompt_schemas import PromptCreateRequest, PromptUpdateRequest


@click.group()
@click.pass_context
def prompts(ctx):
    """Prompt CRUD CLI - 핵심 CRUD 기능만 제공"""
    try:
        # CLI의 저장된 인증 정보 사용
        from adxp_cli.auth.service import get_credential
        headers, config = get_credential()
        
        if not config.token:
            click.echo("Error: 저장된 인증 정보가 없습니다. 'adxp-cli auth login' 명령어로 로그인하세요.", err=True)
            ctx.exit(1)
        
        ctx.ensure_object(dict)
        # ApiKeyCredentials를 사용하여 인증 (CLI에서는 이미 발급받은 토큰 사용)
        from adxp_sdk.auth.credentials import ApiKeyCredentials
        credentials = ApiKeyCredentials(
            api_key=config.token,
            base_url=config.base_url
        )
        ctx.obj['client'] = PromptClient(credentials)
        
    except Exception as e:
        click.echo(f"Error: 인증 정보를 가져올 수 없습니다: {e}", err=True)
        click.echo("'adxp-cli auth login' 명령어로 로그인하세요.", err=True)
        ctx.exit(1)


# ====================================================================
# Guardrails 관련 명령어들 (구현 예정)
# ====================================================================

@prompts.group()
@click.pass_context
def guardrails(ctx):
    """Guardrails CRUD 명령어"""
    # 부모 컨텍스트에서 client 가져오기
    ctx.obj = ctx.parent.obj


@guardrails.command()
@click.option('--project-id', help='프로젝트 ID (기본값: 인증된 프로젝트)')
@click.option('--page', default=1, help='페이지 번호 (기본값: 1)')
@click.option('--size', default=10, help='페이지 크기 (기본값: 10)')
@click.option('--sort', help='정렬 기준')
@click.option('--filter', help='필터 조건')
@click.option('--search', help='검색어')
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.pass_context
def list(ctx, project_id: Optional[str], page: int, size: int, sort: Optional[str], 
         filter: Optional[str], search: Optional[str], json: bool):
    """Get Guardrails 목록"""
    client = ctx.obj['client']
    
    try:
        result = client.get_guardrails(
            project_id=project_id,
            page=page,
            size=size,
            sort=sort,
            filter=filter,
            search=search
        )
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[GUARDRAILS] Guardrails 목록:")
            click.echo("=" * 50)
            
            if 'data' in result:
                guardrails_list = result['data']
                click.echo(f"총 {len(guardrails_list)}개의 Guardrails")
                
                for i, guardrail in enumerate(guardrails_list, 1):
                    click.echo(f"\n{i}. {guardrail.get('name', 'N/A')}")
                    click.echo(f"   ID: {guardrail.get('id', 'N/A')}")
                    click.echo(f"   설명: {guardrail.get('description', 'N/A')}")
                    if 'tags' in guardrail:
                        tags = [tag.get('tag', '') for tag in guardrail['tags']]
                        click.echo(f"   태그: {', '.join(tags)}")
                    click.echo(f"   생성일: {guardrail.get('created_at', 'N/A')}")
            else:
                click.echo("No data found in response")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        else:
            click.echo(f"[ERROR] Failed to get guardrails: {e}", err=True)
        ctx.exit(1)


@guardrails.command()
@click.option('--name', required=True, help='Guardrails 이름')
@click.option('--description', required=True, help='Guardrails 설명')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--prompt-id', required=True, help='프롬프트 ID')
@click.option('--serving-id', required=True, help='서빙 ID')
@click.option('--serving-name', required=True, help='서빙 이름')
@click.option('--tags', help='태그들 (쉼표로 구분, 예: tag1,tag2)')
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.pass_context
def create(ctx, name: str, description: str, project_id: str, prompt_id: str,
          serving_id: str, serving_name: str, tags: Optional[str], json: bool):
    """Create Guardrails"""
    client = ctx.obj['client']
    
    try:
        # LLMs 배열 구성
        llms = [{
            "serving_id": serving_id,
            "serving_name": serving_name
        }]
        
        # Tags 배열 구성
        tags_list = []
        if tags:
            tag_names = [tag.strip() for tag in tags.split(',')]
            tags_list = [{"tag": tag_name} for tag_name in tag_names]
        
        result = client.create_guardrails(
            name=name,
            description=description,
            project_id=project_id,
            prompt_id=prompt_id,
            llms=llms,
            tags=tags_list
        )
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[SUCCESS] Guardrails 생성 성공!")
            click.echo("=" * 50)
            
            if 'data' in result:
                data = result['data']
                click.echo(f"Guardrails ID: {data.get('id', 'N/A')}")
                click.echo(f"이름: {data.get('name', 'N/A')}")
                click.echo(f"설명: {data.get('description', 'N/A')}")
                click.echo(f"프로젝트 ID: {data.get('project_id', 'N/A')}")
                click.echo(f"프롬프트 ID: {data.get('prompt_id', 'N/A')}")
                
                if 'llms' in data:
                    click.echo(f"LLMs:")
                    for i, llm in enumerate(data['llms'], 1):
                        click.echo(f"  {i}. 서빙 ID: {llm.get('serving_id', 'N/A')}")
                        click.echo(f"     서빙 이름: {llm.get('serving_name', 'N/A')}")
                
                if 'tags' in data:
                    tag_names = [tag.get('tag', '') for tag in data['tags']]
                    click.echo(f"태그: {', '.join(tag_names)}")
                
                click.echo(f"생성일: {data.get('created_at', 'N/A')}")
            else:
                click.echo("No data found in response")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        elif "400" in error_msg or "Bad Request" in error_msg:
            click.echo(f"[ERROR] 잘못된 요청: {e}", err=True)
        else:
            click.echo(f"[ERROR] Failed to create guardrails: {e}", err=True)
        ctx.exit(1)


@guardrails.command()
@click.argument('guardrails_id', required=True)
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.pass_context
def get(ctx, guardrails_id: str, json: bool):
    """Get a single item of Guardrails"""
    client = ctx.obj['client']
    
    try:
        result = client.get_guardrails_by_id(guardrails_id)
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[GUARDRAILS] Guardrails 상세 정보:")
            click.echo("=" * 50)
            
            if 'data' in result:
                data = result['data']
                click.echo(f"Guardrails ID: {data.get('id', 'N/A')}")
                click.echo(f"이름: {data.get('name', 'N/A')}")
                click.echo(f"설명: {data.get('description', 'N/A')}")
                click.echo(f"프로젝트 ID: {data.get('project_id', 'N/A')}")
                click.echo(f"프롬프트 ID: {data.get('prompt_id', 'N/A')}")
                
                if 'llms' in data:
                    click.echo(f"\nLLMs:")
                    for i, llm in enumerate(data['llms'], 1):
                        click.echo(f"  {i}. 서빙 ID: {llm.get('serving_id', 'N/A')}")
                        click.echo(f"     서빙 이름: {llm.get('serving_name', 'N/A')}")
                
                if 'tags' in data:
                    tag_names = [tag.get('tag', '') for tag in data['tags']]
                    click.echo(f"\n태그: {', '.join(tag_names)}")
                
                click.echo(f"\n생성일: {data.get('created_at', 'N/A')}")
                click.echo(f"수정일: {data.get('updated_at', 'N/A')}")
                
                # 추가 필드들 출력
                other_fields = {k: v for k, v in data.items() if k not in [
                    'id', 'name', 'description', 'project_id', 'prompt_id', 
                    'llms', 'tags', 'created_at', 'updated_at'
                ]}
                if other_fields:
                    click.echo(f"\n추가 정보:")
                    for field, value in other_fields.items():
                        click.echo(f"  • {field}: {value}")
            else:
                click.echo("No data found in response")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        elif "404" in error_msg or "Not Found" in error_msg:
            click.echo(f"[ERROR] Guardrails not found: {guardrails_id}", err=True)
        else:
            click.echo(f"[ERROR] Failed to get guardrails: {e}", err=True)
        ctx.exit(1)


@guardrails.command()
@click.argument('guardrails_id', required=True)
@click.option('--name', required=True, help='Guardrails 이름')
@click.option('--description', required=True, help='Guardrails 설명')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--prompt-id', required=True, help='프롬프트 ID')
@click.option('--serving-id', required=True, help='서빙 ID')
@click.option('--serving-name', required=True, help='서빙 이름')
@click.option('--tags', help='태그들 (쉼표로 구분, 예: tag1,tag2)')
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.pass_context
def update(ctx, guardrails_id: str, name: str, description: str, project_id: str, prompt_id: str,
          serving_id: str, serving_name: str, tags: Optional[str], json: bool):
    """Edit Guardrails"""
    client = ctx.obj['client']
    
    try:
        # LLMs 배열 구성
        llms = [{
            "serving_id": serving_id,
            "serving_name": serving_name
        }]
        
        # Tags 배열 구성
        tags_list = []
        if tags:
            tag_names = [tag.strip() for tag in tags.split(',')]
            tags_list = [{"tag": tag_name} for tag_name in tag_names]
        
        result = client.update_guardrails(
            guardrails_id=guardrails_id,
            name=name,
            description=description,
            project_id=project_id,
            prompt_id=prompt_id,
            llms=llms,
            tags=tags_list
        )
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[SUCCESS] Guardrails 수정 성공!")
            click.echo("=" * 50)
            
            if 'data' in result:
                data = result['data']
                click.echo(f"Guardrails ID: {data.get('id', 'N/A')}")
                click.echo(f"이름: {data.get('name', 'N/A')}")
                click.echo(f"설명: {data.get('description', 'N/A')}")
                click.echo(f"프로젝트 ID: {data.get('project_id', 'N/A')}")
                click.echo(f"프롬프트 ID: {data.get('prompt_id', 'N/A')}")
                
                if 'llms' in data:
                    click.echo(f"LLMs:")
                    for i, llm in enumerate(data['llms'], 1):
                        click.echo(f"  {i}. 서빙 ID: {llm.get('serving_id', 'N/A')}")
                        click.echo(f"     서빙 이름: {llm.get('serving_name', 'N/A')}")
                
                if 'tags' in data:
                    tag_names = [tag.get('tag', '') for tag in data['tags']]
                    click.echo(f"태그: {', '.join(tag_names)}")
                
                click.echo(f"수정일: {data.get('updated_at', 'N/A')}")
            else:
                click.echo("No data found in response")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        elif "400" in error_msg or "Bad Request" in error_msg:
            click.echo(f"[ERROR] 잘못된 요청: {e}", err=True)
        elif "404" in error_msg or "Not Found" in error_msg:
            click.echo(f"[ERROR] Guardrails not found: {guardrails_id}", err=True)
        else:
            click.echo(f"[ERROR] Failed to update guardrails: {e}", err=True)
        ctx.exit(1)


@guardrails.command()
@click.argument('guardrails_id', required=True)
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.option('--force', is_flag=True, help='확인 없이 강제 삭제')
@click.pass_context
def delete(ctx, guardrails_id: str, json: bool, force: bool):
    """Delete Guardrails"""
    client = ctx.obj['client']
    
    try:
        # 확인 메시지 (force 옵션이 없을 때만)
        if not force:
            click.confirm(f'정말로 Guardrails "{guardrails_id}"를 삭제하시겠습니까?', abort=True)
        
        result = client.delete_guardrails(guardrails_id)
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[SUCCESS] Guardrails 삭제 성공!")
            click.echo("=" * 50)
            
            if 'data' in result:
                data = result['data']
                click.echo(f"삭제된 Guardrails ID: {data.get('id', guardrails_id)}")
                click.echo(f"삭제 시간: {data.get('deleted_at', 'N/A')}")
                
                # 추가 정보가 있다면 출력
                other_fields = {k: v for k, v in data.items() if k not in ['id', 'deleted_at']}
                if other_fields:
                    click.echo(f"\n추가 정보:")
                    for field, value in other_fields.items():
                        click.echo(f"  • {field}: {value}")
            else:
                # 응답에 data가 없어도 성공으로 간주
                click.echo(f"Guardrails '{guardrails_id}'가 성공적으로 삭제되었습니다.")
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        elif "404" in error_msg or "Not Found" in error_msg:
            click.echo(f"[ERROR] Guardrails not found: {guardrails_id}", err=True)
        elif "403" in error_msg or "Forbidden" in error_msg:
            click.echo(f"[ERROR] 삭제 권한이 없습니다: {guardrails_id}", err=True)
        else:
            click.echo(f"[ERROR] Failed to delete guardrails: {e}", err=True)
        ctx.exit(1)


@guardrails.command()
@click.option('--serving-name', required=True, help='서빙 이름')
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.pass_context
def serving(ctx, serving_name: str, json: bool):
    """Get a Guardrails Prompt by Serving Name"""
    client = ctx.obj['client']
    
    try:
        result = client.get_guardrails_by_serving(serving_name)
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[GUARDRAILS] Guardrails 정보 (서빙 이름으로 조회):")
            click.echo("=" * 50)
            
            if 'data' in result:
                data = result['data']
                click.echo(f"서빙 이름: {serving_name}")
                click.echo(f"Guardrails ID: {data.get('id', 'N/A')}")
                click.echo(f"이름: {data.get('name', 'N/A')}")
                click.echo(f"설명: {data.get('description', 'N/A')}")
                click.echo(f"프로젝트 ID: {data.get('project_id', 'N/A')}")
                click.echo(f"프롬프트 ID: {data.get('prompt_id', 'N/A')}")
                
                if 'llms' in data:
                    click.echo(f"\nLLMs:")
                    for i, llm in enumerate(data['llms'], 1):
                        click.echo(f"  {i}. 서빙 ID: {llm.get('serving_id', 'N/A')}")
                        click.echo(f"     서빙 이름: {llm.get('serving_name', 'N/A')}")
                
                if 'tags' in data:
                    tag_names = [tag.get('tag', '') for tag in data['tags']]
                    click.echo(f"\n태그: {', '.join(tag_names)}")
                
                click.echo(f"\n생성일: {data.get('created_at', 'N/A')}")
                click.echo(f"수정일: {data.get('updated_at', 'N/A')}")
                
                # 추가 필드들 출력
                other_fields = {k: v for k, v in data.items() if k not in [
                    'id', 'name', 'description', 'project_id', 'prompt_id', 
                    'llms', 'tags', 'created_at', 'updated_at'
                ]}
                if other_fields:
                    click.echo(f"\n추가 정보:")
                    for field, value in other_fields.items():
                        click.echo(f"  • {field}: {value}")
            else:
                click.echo(f"서빙 이름 '{serving_name}'에 해당하는 Guardrails를 찾을 수 없습니다.")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        elif "404" in error_msg or "Not Found" in error_msg:
            click.echo(f"[ERROR] 서빙 이름 '{serving_name}'에 해당하는 Guardrails를 찾을 수 없습니다.", err=True)
        else:
            click.echo(f"[ERROR] Failed to get guardrails by serving: {e}", err=True)
        ctx.exit(1)


@guardrails.command()
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.pass_context
def tags(ctx, json: bool):
    """Get Guardrails Tags"""
    client = ctx.obj['client']
    
    try:
        result = client.get_guardrails_tags()
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[TAG] Guardrails 태그 목록:")
            click.echo("=" * 50)
            
            if 'data' in result:
                tags_list = result['data']
                if isinstance(tags_list, list) and tags_list:
                    click.echo(f"총 {len(tags_list)}개의 태그:")
                    for i, tag in enumerate(tags_list, 1):
                        click.echo(f"  {i}. {tag}")
                else:
                    click.echo("태그가 없습니다.")
            else:
                click.echo("태그 데이터를 찾을 수 없습니다.")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        else:
            click.echo(f"[ERROR] Failed to get guardrails tags: {e}", err=True)
        ctx.exit(1)


@guardrails.command()
@click.option('--filters', required=True, help='검색 필터')
@click.option('--json', is_flag=True, help='JSON 형식으로 출력')
@click.pass_context
def search_tags(ctx, filters: str, json: bool):
    """Search Guardrails Tags"""
    client = ctx.obj['client']
    
    try:
        result = client.search_guardrails_tags(filters)
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo(f"[SEARCH] Guardrails 태그 검색 결과 (필터: '{filters}'):")
            click.echo("=" * 50)
            
            if 'data' in result:
                guardrails_list = result['data']
                if isinstance(guardrails_list, list) and guardrails_list:
                    click.echo(f"총 {len(guardrails_list)}개의 Guardrails:")
                    for i, guardrail in enumerate(guardrails_list, 1):
                        click.echo(f"\n{i}. {guardrail.get('name', 'N/A')}")
                        click.echo(f"   ID: {guardrail.get('id', 'N/A')}")
                        click.echo(f"   설명: {guardrail.get('description', 'N/A')}")
                        if 'tags' in guardrail:
                            tag_names = [tag.get('tag', '') for tag in guardrail['tags']]
                            click.echo(f"   태그: {', '.join(tag_names)}")
                        click.echo(f"   생성일: {guardrail.get('created_at', 'N/A')}")
                else:
                    click.echo(f"필터 '{filters}'에 해당하는 Guardrails를 찾을 수 없습니다.")
            else:
                click.echo("검색 결과 데이터를 찾을 수 없습니다.")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        else:
            click.echo(f"[ERROR] Failed to search guardrails tags: {e}", err=True)
        ctx.exit(1)


# ====================================================================
# 기존 프롬프트 명령어들
# ====================================================================

@prompts.command()
@click.option('--name', required=True, help='프롬프트 이름')
@click.option('--project-id', help='프로젝트 ID (기본값: 인증된 프로젝트)')
@click.option('--description', help='프롬프트 설명')
@click.option('--system-prompt', help='시스템 프롬프트')
@click.option('--user-prompt', help='사용자 프롬프트')
@click.option('--assistant-prompt', help='어시스턴트 프롬프트')
@click.option('--tags', help='프롬프트 태그 (쉼표로 구분)')
@click.option('--variables', help='프롬프트 변수 (쉼표로 구분)')
@click.option('--template', help='템플릿 이름 (예: AGENT__GENERATOR)')
@click.option('--release', type=bool, help='릴리즈 여부')
@click.pass_context
def create(ctx, name: str, project_id: str, description: str, system_prompt: str, 
          user_prompt: str, assistant_prompt: str, tags: str, variables: str, 
          template: str, release: Optional[bool]):
    """프롬프트 생성"""
    client = ctx.obj['client']
    
    # project_id가 없으면 인증된 프로젝트 사용
    if not project_id:
        from adxp_cli.auth.service import get_credential
        _, config = get_credential()
        project_id = config.client_id  # client_id를 프로젝트로 사용
    
    # 프롬프트 데이터 구성
    prompt_data = {
        "name": name,
        "project_id": project_id,
        "release": release if release is not None else False
    }
    
    if description:
        prompt_data["desc"] = description
    
    # 템플릿 사용
    if template:
        prompt_data["template"] = template
    else:
        # 직접 메시지 구성
        messages = []
        if system_prompt:
            messages.append({"message": system_prompt, "mtype": 1})
        if user_prompt:
            messages.append({"message": user_prompt, "mtype": 2})
        if assistant_prompt:
            messages.append({"message": assistant_prompt, "mtype": 3})
        
        if not messages:
            click.echo("Error: 프롬프트 생성 시 최소 하나의 메시지가 필요합니다.", err=True)
            click.echo("  --system-prompt, --user-prompt, --assistant-prompt 중 하나를 입력하거나", err=True)
            click.echo("  --template 옵션을 사용하세요.", err=True)
            ctx.exit(1)
        
        prompt_data["messages"] = messages
        
        # 태그 구성
        if tags:
            tag_list = []
            for tag in tags.split(","):
                tag_list.append({"tag": tag.strip()})
            prompt_data["tags"] = tag_list
        
        # 변수 구성
        if variables:
            variable_list = []
            for var in variables.split(","):
                variable_list.append({
                    "variable": var.strip(),
                    "token_limit": 0,
                    "token_limit_flag": False,
                    "validation": "",
                    "validation_flag": False
                })
            prompt_data["variables"] = variable_list
    
    try:
        result = client.create_prompt(prompt_data)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 생성 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.option('--project-id', help='프로젝트 ID (기본값: 인증된 프로젝트)')
@click.option('--page', default=1, help='페이지 번호')
@click.option('--size', default=10, help='페이지 크기')
@click.option('--sort', help='정렬 기준 (created_at, updated_at, name)')
@click.option('--filter', help='필터 조건')
@click.option('--search', help='검색어')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
@click.pass_context
def list(ctx, project_id: str, page: int, size: int, sort: str, filter: str, search: str, verbose: bool):
    """프롬프트 목록 조회"""
    client = ctx.obj['client']
    
    # project_id가 없으면 인증된 프로젝트 사용
    if not project_id:
        from adxp_cli.auth.service import get_credential
        _, config = get_credential()
        project_id = config.client_id  # client_id를 프로젝트로 사용
    
    try:
        result = client.get_prompts(
            project_id=project_id,
            page=page,
            size=size,
            sort=sort,
            filter=filter,
            search=search
        )
        
        if verbose:
            # 상세 정보 출력
            click.echo("=== 프롬프트 목록 조회 결과 ===")
            click.echo(f"응답 코드: {result.get('code', 'N/A')}")
            click.echo(f"응답 메시지: {result.get('detail', 'N/A')}")
            
            prompts = result.get('data', [])
            if prompts:
                click.echo(f"\n총 {len(prompts)}개의 프롬프트:")
                for i, prompt in enumerate(prompts, 1):
                    click.echo(f"\n{i}. {prompt.get('name', 'N/A')}")
                    click.echo(f"   UUID: {prompt.get('uuid', 'N/A')}")
                    click.echo(f"   설명: {prompt.get('desc', 'N/A')}")
                    click.echo(f"   생성일: {prompt.get('created_at', 'N/A')}")
                    if prompt.get('tags'):
                        tags = [tag.get('tag', '') for tag in prompt.get('tags', [])]
                        click.echo(f"   태그: {', '.join(tags)}")
            else:
                click.echo("\n프롬프트가 없습니다.")
        else:
            # 간단한 정보만 출력
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
            
    except Exception as e:
        click.echo(f"프롬프트 목록 조회 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.argument('prompt_uuid', required=True)
@click.pass_context
def get(ctx, prompt_uuid: str):
    """특정 프롬프트 조회"""
    client = ctx.obj['client']
    
    try:
        result = client.get_prompt(prompt_uuid)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 조회 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.argument('prompt_uuid', required=True)
@click.option('--name', help='프롬프트 이름')
@click.option('--description', help='프롬프트 설명')
@click.option('--system-prompt', help='시스템 프롬프트')
@click.option('--user-prompt', help='사용자 프롬프트')
@click.option('--assistant-prompt', help='어시스턴트 프롬프트')
@click.option('--tags', help='프롬프트 태그 (쉼표로 구분)')
@click.option('--variables', help='프롬프트 변수 (쉼표로 구분)')
@click.option('--release', type=bool, help='릴리즈 여부')
@click.pass_context
def update(ctx, prompt_uuid: str, name: str, description: str, system_prompt: str,
          user_prompt: str, assistant_prompt: str, tags: str, variables: str, release: bool):
    """프롬프트 수정"""
    client = ctx.obj['client']
    
    # 수정할 데이터 구성 (API 형식에 맞춤)
    update_data = {}
    
    if name:
        update_data["new_name"] = name  # name 대신 new_name 사용
    
    if description:
        update_data["desc"] = description  # description 대신 desc 사용
    
    # 메시지 구성
    messages = []
    if system_prompt:
        messages.append({"message": system_prompt, "mtype": 1})
    if user_prompt:
        messages.append({"message": user_prompt, "mtype": 2})
    if assistant_prompt:
        messages.append({"message": assistant_prompt, "mtype": 3})
    
    if messages:
        update_data["messages"] = messages
    
    # 태그 구성
    if tags:
        tag_list = []
        for tag in tags.split(","):
            tag_list.append({"tag": tag.strip()})
        update_data["tags"] = tag_list
    
    # 변수 구성
    if variables:
        variable_list = []
        for var in variables.split(","):
            variable_list.append({
                "variable": var.strip(),
                "token_limit": 0,
                "token_limit_flag": False,
                "validation": "",
                "validation_flag": False
            })
        update_data["variables"] = variable_list
    
    if release is not None:
        update_data["release"] = release
    
    try:
        result = client.update_prompt(prompt_uuid, update_data)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 수정 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.argument('prompt_uuid', required=True)
@click.pass_context
def delete(ctx, prompt_uuid: str):
    """프롬프트 삭제"""
    client = ctx.obj['client']
    
    try:
        result = client.delete_prompt(prompt_uuid)
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.echo(f"프롬프트 삭제 실패: {e}", err=True)
        ctx.exit(1)


@prompts.command()
@click.argument('prompt_uuid', required=True)
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.pass_context
def get_prompt(ctx, prompt_uuid: str, json: bool):
    """Get a prompt messages and variables"""
    client = ctx.obj['client']
    
    try:
        result = client.get_prompt(prompt_uuid)
        
        if json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Pretty print the result
            click.echo("[INFO] Prompt Information:")
            click.echo("=" * 50)
            
            if 'data' in result:
                data = result['data']
                click.echo(f"Prompt UUID: {prompt_uuid}")
                
                if 'messages' in data:
                    click.echo(f"\n[MESSAGE] Messages ({len(data['messages'])}):")
                    for i, message in enumerate(data['messages'], 1):
                        click.echo(f"  {i}. {message}")
                
                if 'variables' in data:
                    click.echo(f"\n[VAR] Variables ({len(data['variables'])}):")
                    for var_name, var_value in data['variables'].items():
                        click.echo(f"  • {var_name}: {var_value}")
                
                # Show other fields if present
                other_fields = {k: v for k, v in data.items() if k not in ['messages', 'variables']}
                if other_fields:
                    click.echo(f"\n[DOC] Additional Information:")
                    for field, value in other_fields.items():
                        click.echo(f"  • {field}: {value}")
            else:
                click.echo("No data found in response")
                if json:
                    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            click.echo("[ERROR] 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh", err=True)
        elif "404" in error_msg or "Not Found" in error_msg:
            click.echo(f"[ERROR] Prompt not found: {prompt_uuid}", err=True)
        else:
            click.echo(f"[ERROR] Failed to get prompt: {e}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    prompts()