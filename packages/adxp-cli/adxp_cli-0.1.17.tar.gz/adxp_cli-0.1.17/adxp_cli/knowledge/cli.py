import click
import json
from adxp_cli.auth.service import get_credential
from adxp_sdk.knowledges.hub import AXKnowledgeHub



@click.group()
@click.option('--base-url', default='https://aip-stg.sktai.io', help='API 기본 URL')
@click.option('--api-key', envvar='KNOWLEDGES_API_KEY', help='API 키')
def knowledge(base_url : str, api_key : str):
    """Knowledges CRUD CLI - 핵심 CRUD 기능만 제공"""
    pass



@knowledge.command()
@click.option("--is_active", default=None, help="사용가능 여부 (true/false)")
@click.option("--page", default=1, help="페이지 번호")
@click.option("--size", default=10, help="페이지 크기")
@click.option("--sort", default=None, help="정렬 기준")
@click.option("--filter", default=None, help="필터 조건")
@click.option("--search", default=None, help="검색어")
def list(is_active: bool, page: int, size: int, sort: str, filter: str, search: str):
    """ Knowledge List 조회 """

    try:
        headers, config = get_credential()
        hub = AXKnowledgeHub(headers=headers, base_url=config.base_url)

        result = hub.list_knowledge(
            is_active=is_active,
            page=page, 
            size=size,
            sort=sort,    
            filter=filter,
            search=search
        )

        click.secho("✅ Knowledge List 조회 성공", fg="green")
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.secho(f"❌ Knowledge List 조회 실패 Error: {e}", fg="red")



@knowledge.command()
@click.option("--name", required=True, help="이름")
@click.option("--description", default=None, help="설명")
@click.option("--datasource-id", default=None, help="데이터소스 ID")
@click.option("--embedding-model-name", required=True, help="임베딩 모델 명")
@click.option("--loader", default="Default", help="로더 타입")
@click.option("--splitter", type=click.Choice(['RecursiveCharacter', 'Character', 'Semantic', 'CustomSplitter', 'NotSplit']), default="RecursiveCharacter", help="Splitter 타입")
@click.option("--vector-db-id", required=True, help="백터DB ID")
@click.option("--chunk-size", type=int, default=None, help="청크 크기")
@click.option("--chunk-overlap", type=int, default=None, help="청크 오버랩")
@click.option("--separator", default=None, help="분리자")
def create(name: str, description: str, datasource_id: str, embedding_model_name: str, loader: str, splitter: str,
    vector_db_id: str, chunk_size: int, chunk_overlap: int, separator: str):
    """ Knowledge 리포지토리 생성 """
    
    try:
        headers, config = get_credential()
        hub = AXKnowledgeHub(headers=headers, base_url=config.base_url)
        
        result = hub.create_knowledge(
            name=name,
            description=description,
            datasource_id=datasource_id,
            embedding_model_name=embedding_model_name,
            loader=loader,
            splitter=splitter,
            vector_db_id=vector_db_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator,
            project_id=config.client_id
        )
        
        click.secho("✅ Knowledge 생성 성공", fg="green")
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.secho(f"❌ Knowledge 생성 실패 Error: {e}", fg="red")



@knowledge.command()
@click.option("--repo-id", required=True, help="knowledge 리포지토리 ID")
@click.option("--name", default=None, help="이름")
@click.option("--description", default=None, help="설명")
@click.option("--loader", default=None, help="로더 타입")
@click.option("--splitter", default=None, help="Splitter 타입")
@click.option("--chunk-size", type=int, help="청크 크기")
@click.option("--chunk-overlap", type=int, help="청크 오버랩")
@click.option("--separator", default=None, help="분리자")
def update(repo_id: str, name: str, description: str, loader: str, splitter: str, chunk_size: int, chunk_overlap: int, separator: str):
    """ Knowledge 리포지토리 수정 """
    
    try:
        headers, config = get_credential()
        hub = AXKnowledgeHub(headers=headers, base_url=config.base_url)

        result = hub.update_knowledge(
            repo_id=repo_id,
            name=name,
            description=description,
            loader=loader,
            splitter=splitter,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator
        )
        
        click.secho("✅ Knowledge 업데이트 성공", fg="green")
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.secho(f"❌ Knowledge 업데이트 실패 Error: {e}", fg="red")



@knowledge.command()
@click.option("--repo-id", required=True, help="knowledge 리포지토리 ID")
def delete(repo_id: str):
    """ Knowledge 리포지토리 삭제 """

    try:
        headers, config = get_credential()
        hub = AXKnowledgeHub(headers=headers, base_url=config.base_url)

        result = hub.delete_knowledge(
            repo_id=repo_id
        )

        click.secho("✅ Knowledge 삭제 성공", fg="green")
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        click.secho(f"❌ Knowledge 삭제 실패 Error: {e}", fg="red")



@knowledge.command()
@click.option("--repo-id", required=True, help="knowledge 리포지토리 ID")
@click.option("--datasource-id", default=None, help="데이터소스 ID")
@click.option("--file-path", required=True, help="업로드 파일 경로")
def upload(file_path: str, datasource_id: str, repo_id: str):
    """ Knowledge 리포지토리 파일 업로드 """

    try:
        headers, config = get_credential()
        hub = AXKnowledgeHub(headers=headers, base_url=config.base_url)
        
        result = hub.upload_knowledge_file(
            repo_id=repo_id,
            datasource_id=datasource_id,
            file_path=file_path
        )
        
        click.secho("✅ 파일 업로드 성공", fg="green")
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        click.echo(f"❌ 파일 업로드 실패: {e}", err=True)


if __name__ == '__main__':
    knowledge()