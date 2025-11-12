"""
Dataset CRUD CLI

Click 기반의 명령줄 인터페이스입니다.
핵심 CRUD 기능만 제공합니다.
"""

import click
import json
import os
from typing import Dict, Any, Optional, List
from tabulate import tabulate

try:
    from adxp_sdk.dataset.hub import AXDatasetHub
    from adxp_sdk.dataset.schemas import (
        DatasetCreateRequest, DatasetUpdateRequest, DatasetType,
        DatasetFile, DatasetTag, DatasetProcessor, DatasetFilter
    )
except ImportError:
    # 직접 실행할 때를 위한 절대 import
    from adxp_sdk.dataset.hub import AXDatasetHub
    from adxp_sdk.dataset.schemas import (
        DatasetCreateRequest, DatasetUpdateRequest, DatasetType,
        DatasetFile, DatasetTag, DatasetProcessor, DatasetFilter
    )


def get_dataset_hub():
    """Get AXDatasetHub instance with credentials"""
    from ..auth.service import get_credential
    from adxp_sdk.auth.credentials import ApiKeyCredentials
    
    headers, config = get_credential()
    
    if not config.token:
        raise click.ClickException("Error: 저장된 인증 정보가 없습니다. 'adxp-cli auth login' 명령어로 로그인하세요.")
    
    credentials = ApiKeyCredentials(
        api_key=config.token,
        base_url=config.base_url
    )
    return AXDatasetHub(credentials)


def print_json(data: Dict[str, Any], indent: int = 2) -> None:
    """JSON 데이터를 보기 좋게 출력"""
    click.echo(json.dumps(data, ensure_ascii=False, indent=indent))


@click.group()
def cli():
    """Dataset CRUD CLI - 핵심 CRUD 기능만 제공"""
    pass


@cli.command()
@click.option('--name', required=True, help='Dataset 이름')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--description', help='Dataset 설명')
@click.option('--dataset-type', type=click.Choice(['unsupervised_finetuning', 'supervised_finetuning', 'model_benchmark', 'dpo_finetuning', 'custom']), required=True, help='Dataset 타입')
@click.option('--files', help='업로드할 파일 경로들 (쉼표로 구분)')
@click.option('--datasource-id', help='기존 데이터소스 ID (파일 없이 생성할 때)')
@click.option('--tags', help='Dataset 태그 (쉼표로 구분)')
@click.option('--processor-ids', help='프로세서 ID들 (쉼표로 구분)')
@click.option('--duplicate-columns', help='중복 제거 대상 컬럼들 (쉼표로 구분)')
@click.option('--regex-patterns', help='정규표현식 패턴들 (쉼표로 구분)')
def create(name: str, project_id: str, description: str, dataset_type: str, 
          files: str, datasource_id: str, tags: str, processor_ids: str, duplicate_columns: str, regex_patterns: str):
    """Dataset 생성 (파일 업로드 포함)"""
    try:
        client = get_dataset_hub()
        
        # 태그 처리
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # 프로세서 처리 (빈 배열 필드 제거)
        processor = None
        if processor_ids or duplicate_columns or regex_patterns:
            processor_data = {}
            if processor_ids:
                processor_data["ids"] = [pid.strip() for pid in processor_ids.split(',')]
            if duplicate_columns:
                processor_data["duplicate_subset_columns"] = [col.strip() for col in duplicate_columns.split(',')]
            if regex_patterns:
                processor_data["regular_expression"] = [pattern.strip() for pattern in regex_patterns.split(',')]
            
            # 빈 배열 필드 제거
            processor_data = {k: v for k, v in processor_data.items() if v}
            if processor_data:
                processor = DatasetProcessor(**processor_data)
        
        if files:
            # 파일이 있는 경우: 전체 플로우 실행
            file_paths = [path.strip() for path in files.split(',')]
            result = client.create_dataset_with_files(
                name=name,
                description=description or "",
                project_id=project_id,
                file_paths=file_paths,
                dataset_type=DatasetType(dataset_type),
                tags=tag_list,
                processor=processor
            )
        else:
            # 파일이 없는 경우: 기존 방식
            dataset_data = DatasetCreateRequest(
                name=name,
                description=description or "",
                project_id=project_id,
                type=DatasetType(dataset_type),
                tags=[{"name": tag} for tag in tag_list],
                datasource_id=datasource_id,
                processor=processor,
                is_deleted=False,
                created_by="",
                updated_by="",
                policy=[]
            )
            result = client.create_dataset(dataset_data)
        
        click.echo(f"Dataset 생성 성공: {result.get('id')}")
        print_json(result)
        
    except Exception as e:
        click.echo(f"Dataset 생성 실패: {e}", err=True)
        raise click.ClickException(f"Dataset 생성 실패: {e}")


@cli.command()
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--page', default=1, help='페이지 번호')
@click.option('--size', default=10, help='페이지 크기')
@click.option('--sort', help='정렬 기준 (created_at, updated_at, name)')
@click.option('--dataset-type', help='Dataset 타입 필터')
@click.option('--status', help='상태 필터 (processing, completed, failed, canceled)')
@click.option('--tags', help='태그 필터 (쉼표로 구분)')
@click.option('--search', help='검색어')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
def list(project_id: str, page: int, size: int, sort: str, dataset_type: str, 
         status: str, tags: str, search: str, verbose: bool):
    """Dataset 목록 조회"""
    try:
        client = get_dataset_hub()
        
        # 필터 구성
        filter_obj = None
        if dataset_type or status or tags:
            filter_dict = {}
            if dataset_type:
                filter_dict['dataset_type'] = dataset_type
            if status:
                filter_dict['status'] = status
            if tags:
                filter_dict['tags'] = [tag.strip() for tag in tags.split(',')]
            filter_obj = DatasetFilter(**filter_dict)
        
        result = client.get_datasets(
            project_id=project_id,
            page=page,
            size=size,
            sort=sort,
            filter=filter_obj,
            search=search
        )
        
        if verbose:
            print_json(result)
        else:
            # 간단한 테이블 형태로 출력
            datasets = result.get('data', [])
            if datasets:
                headers = ['ID', 'Name', 'Type', 'Status', 'Created At']
                rows = []
                for dataset in datasets:
                    rows.append([
                        dataset.get('id', 'N/A'),
                        dataset.get('name', 'N/A'),
                        dataset.get('type', 'N/A'),
                        dataset.get('status', 'N/A'),
                        dataset.get('created_at', 'N/A')
                    ])
                click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            else:
                click.echo("No datasets found.")
                
    except Exception as e:
        click.echo(f"Dataset 목록 조회 실패: {e}", err=True)
        raise click.ClickException(f"Dataset 목록 조회 실패: {e}")


@cli.command()
@click.argument('dataset_id')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
def get(dataset_id: str, verbose: bool):
    """Dataset 상세 조회"""
    try:
        client = get_dataset_hub()
        result = client.get_dataset_by_id(dataset_id)
        
        if verbose:
            print_json(result)
        else:
            click.echo(f"Dataset ID: {result.get('id')}")
            click.echo(f"Name: {result.get('name')}")
            click.echo(f"Type: {result.get('type')}")
            click.echo(f"Status: {result.get('status')}")
            click.echo(f"Description: {result.get('description')}")
            click.echo(f"Created At: {result.get('created_at')}")
            
    except Exception as e:
        click.echo(f"Dataset 조회 실패: {e}", err=True)
        raise click.ClickException(f"Dataset 조회 실패: {e}")


@cli.command()
@click.argument('dataset_id')
@click.option('--name', help='Dataset 이름')
@click.option('--description', help='Dataset 설명')
@click.option('--tags', help='Dataset 태그 (쉼표로 구분)')
def update(dataset_id: str, name: str, description: str, tags: str):
    """Dataset 수정"""
    try:
        client = get_dataset_hub()
        
        # 업데이트 데이터 구성
        update_data = {}
        if name:
            update_data['name'] = name
        if description:
            update_data['description'] = description
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            update_data['tags'] = [{"name": tag} for tag in tag_list]
        
        if not update_data:
            click.echo("수정할 데이터가 없습니다.", err=True)
            return
        
        dataset_data = DatasetUpdateRequest(**update_data)
        result = client.update_dataset(dataset_id, dataset_data)
        
        click.echo(f"Dataset 수정 성공: {dataset_id}")
        print_json(result)
        
    except Exception as e:
        click.echo(f"Dataset 수정 실패: {e}", err=True)
        raise click.ClickException(f"Dataset 수정 실패: {e}")


@cli.command()
@click.argument('dataset_id')
@click.option('--force', is_flag=True, help='강제 삭제')
def delete(dataset_id: str, force: bool):
    """Dataset 삭제"""
    try:
        client = get_dataset_hub()
        result = client.delete_dataset(dataset_id)
        
        if result:
            click.echo(f"Dataset 삭제 성공: {dataset_id}")
        else:
            click.echo(f"Dataset 삭제 실패: {dataset_id}")
            
    except Exception as e:
        click.echo(f"Dataset 삭제 실패: {e}", err=True)
        raise click.ClickException(f"Dataset 삭제 실패: {e}")


@cli.command()
@click.argument('dataset_id')
@click.option('--page', default=1, help='페이지 번호')
@click.option('--size', default=10, help='페이지 크기')
@click.option('--sort', help='정렬 기준')
@click.option('--filter', help='필터')
@click.option('--search', help='검색어')
@click.option('--verbose', '-v', is_flag=True, help='상세 정보 출력')
def list_files(dataset_id: str, page: int, size: int, sort: str, filter: str, search: str, verbose: bool):
    """Dataset 파일 목록 조회"""
    try:
        client = get_dataset_hub()
        result = client.get_dataset_files(
            dataset_id=dataset_id,
            page=page,
            size=size,
            sort=sort,
            filter=filter,
            search=search
        )
        
        if verbose:
            print_json(result)
        else:
            files = result.get('data', [])
            if files:
                headers = ['ID', 'File Name', 'File Size', 'File Type', 'Created At']
                rows = []
                for file_info in files:
                    rows.append([
                        file_info.get('id', 'N/A'),
                        file_info.get('file_name', 'N/A'),
                        file_info.get('file_size', 'N/A'),
                        file_info.get('file_type', 'N/A'),
                        file_info.get('created_at', 'N/A')
                    ])
                click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            else:
                click.echo("No files found.")
                
    except Exception as e:
        click.echo(f"Dataset 파일 목록 조회 실패: {e}", err=True)
        raise click.ClickException(f"Dataset 파일 목록 조회 실패: {e}")


if __name__ == '__main__':
    cli()