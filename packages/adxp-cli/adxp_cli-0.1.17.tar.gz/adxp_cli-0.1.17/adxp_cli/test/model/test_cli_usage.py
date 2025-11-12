#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Model CRUD CLI V2 - CLI 사용 예제
명령줄에서 모델을 관리하는 방법을 보여줍니다.
"""

import subprocess
import sys
import os
import time
from datetime import datetime


def get_auth_info():
    """
    CLI의 기본 인증 방식을 사용하여 인증 정보를 가져옵니다.
    """
    try:
        # CLI의 저장된 인증 정보 사용
        from adxp_cli.auth.service import get_credential
        headers, config = get_credential()
        
        print("[SUCCESS] 저장된 인증 정보를 사용합니다.")
        print(f"[INFO] 인증 정보:")
        print(f"   Username: {config.username}")
        print(f"   Project: {config.client_id}")
        print(f"   Base URL: {config.base_url}")
        
        token = config.token
        if not token:
            raise RuntimeError("저장된 토큰을 가져올 수 없습니다.")
        
        print(f"🔑 토큰 정보:")
        print(f"   - 토큰 길이: {len(token)}")
        print(f"   - 토큰 시작: {token[:20]}...")
        
        return token, config.base_url
        
    except Exception as e:
        print(f"[ERROR] 인증 정보 가져오기 실패: {e}")
        print("먼저 'adxp auth login' 명령어로 로그인하세요.")
        return None, None


def run_cli_command(command):
    """CLI 명령어 실행"""
    try:
        print(f"실행 명령어: {command}")
        
        # PYTHONPATH 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cli_dir = os.path.dirname(os.path.dirname(current_dir))  # cli/adxp_cli
        project_root = os.path.dirname(os.path.dirname(cli_dir))  # 프로젝트 루트
        
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{project_root};{env.get('PYTHONPATH', '')}"
        env['PYTHONIOENCODING'] = 'utf-8'  # 인코딩 설정
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', env=env)
        print(f"반환 코드: {result.returncode}")
        if result.stderr:
            print(f"에러 출력: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"예외 발생: {e}")
        return False, "", str(e)


def main():
    print("🚀 Model CRUD CLI V2 - CLI 사용 예제")
    print("=" * 60)
    print("[INFO] 사용 전 준비사항:")
    print("   1. 먼저 'adxp auth login' 명령어로 로그인하세요")
    print("   2. 프로바이더 ID를 실제 값으로 변경하세요")
    print("=" * 60)
    
    # 인증 정보 가져오기
    print("\n1. 인증 정보 확인")
    token, base_url = get_auth_info()
    
    if not token:
        print("인증 정보를 가져올 수 없습니다. 테스트를 종료합니다.")
        return
    
    # 환경변수 설정
    os.environ['MODEL_API_KEY'] = token
    print("[SUCCESS] API 키 설정 완료")
    
    # CLI 경로 설정 (현재 파일 기준으로 상대 경로 계산)
    current_file = os.path.abspath(__file__)
    test_dir = os.path.dirname(current_file)
    cli_dir = os.path.dirname(os.path.dirname(test_dir))
    cli_main = os.path.join(cli_dir, "cli.py")
    
    print(f"CLI 경로: {cli_main}")
    
    # 2. 모델 목록 조회 (테이블 형식)
    print("\n2. 모델 목록 조회 (테이블 형식)")
    input("Enter를 눌러서 모델 목록을 조회하세요...")
    
    success, stdout, stderr = run_cli_command(f"adxp-cli model list --size 5")
    if success:
        print("[SUCCESS] 모델 목록 조회 성공!")
        print(stdout)
    else:
        print(f"[ERROR] 모델 목록 조회 실패: {stderr}")
    
    # 3. 모델 목록 조회 (JSON 형식)
    print("\n3. 모델 목록 조회 (JSON 형식)")
    input("Enter를 눌러서 JSON 형식으로 모델 목록을 조회하세요...")
    
    success, stdout, stderr = run_cli_command(f"adxp-cli model list --size 3 --json")
    if success:
        print("[SUCCESS] 모델 목록 조회 성공!")
        print(stdout)
    else:
        print(f"[ERROR] 모델 목록 조회 실패: {stderr}")
    
    # 4. 특정 모델 조회 (첫 번째 모델이 있다면)
    print("\n4. 특정 모델 조회")
    input("Enter를 눌러서 첫 번째 모델의 상세 정보를 조회하세요...")
    
    # 먼저 모델 목록을 가져와서 첫 번째 모델 ID를 얻기
    success, stdout, stderr = run_cli_command(f"adxp-cli model list --size 1 --json")
    if success and stdout.strip():
        try:
            import json
            # stdout에서 실제 JSON 부분만 추출 (더 간단한 방법)
            # "모델이 성공적으로 생성되었습니다:" 다음에 오는 JSON만 추출
            lines = stdout.strip().split('\n')
            json_content = None
            
            # JSON이 시작되는 라인 찾기
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('{'):
                    # 이 라인부터 끝까지가 JSON
                    json_lines = lines[i:]
                    json_content = '\n'.join(json_lines)
                    break
            
            if json_content:
                models_data = json.loads(json_content)
                if models_data.get('data') and len(models_data['data']) > 0:
                    first_model_id = models_data['data'][0]['id']
                    
                    success, stdout, stderr = run_cli_command(f"adxp-cli model get {first_model_id}")
                    if success:
                        print("[SUCCESS] 모델 상세 조회 성공!")
                        print(stdout)
                    else:
                        print(f"[ERROR] 모델 상세 조회 실패: {stderr}")
                else:
                    print("   - 조회할 모델이 없습니다.")
            else:
                print("   - JSON 응답을 찾을 수 없습니다.")
                print(f"   - 응답 내용: {stdout[:200]}...")
        except Exception as e:
            print(f"[ERROR] 모델 ID 파싱 실패: {e}")
            print(f"   - 응답 내용: {stdout[:200]}...")
    else:
        print("   - 모델 목록을 가져올 수 없습니다.")
        if stderr:
            print(f"   - 오류: {stderr}")
    
    # 5. 모델 생성 테스트
    print("\n5. 모델 생성 테스트")
    input("Enter를 눌러서 테스트 모델을 생성하세요...")
    
    test_model_name = f"test-model-cli-v2-{int(time.time())}"
    
    # 멀티라인 명령어를 한 줄로 변경
    create_command = f'adxp-cli model create --name "{test_model_name}" --type language --provider-id "b73964a0-dd51-410c-b20e-30ea293eb019" --serving-type serverless --endpoint-url "https://test-endpoint.com" --endpoint-identifier "test-identifier" --endpoint-key "test-key" --display-name "Test Model CLI" --description "CLI로 생성한 테스트 모델입니다."'
    
    success, stdout, stderr = run_cli_command(create_command)
    if success:
        print("[SUCCESS] 모델 생성 성공!")
        print(stdout)
        
        # 생성된 모델 ID 추출 (테이블 형식에서)
        try:
            lines = stdout.strip().split('\n')
            created_model_id = None
            
            # 테이블에서 id 필드 찾기
            for line in lines:
                if '| id' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        created_model_id = parts[2].strip()
                        break
            
            if created_model_id:
                print(f"   - 생성된 모델 ID: {created_model_id}")
                print(f"   - 모델 이름: {test_model_name}")
            else:
                print("   - 생성된 모델 ID: N/A")
                print("   - 모델 이름: N/A")
        except Exception as e:
            print(f"   - 모델 ID 추출 실패: {e}")
            print("   - 생성된 모델 ID: N/A")
            print("   - 모델 이름: N/A")
                
        # 6. 모델 업데이트
        print("\n6. 모델 업데이트")
        input("Enter를 눌러서 모델을 업데이트하세요...")
        
        update_command = f'adxp-cli model update {created_model_id} --display-name "Updated Test Model CLI" --description "업데이트된 테스트 모델입니다."'
        success, stdout, stderr = run_cli_command(update_command)
        if success:
            print("[SUCCESS] 모델 업데이트 성공!")
            print(stdout)
        else:
            print(f"[ERROR] 모델 업데이트 실패: {stderr}")
        
        # 7. 태그 추가
        print("\n7. 태그 추가")
        input("Enter를 눌러서 모델에 태그를 추가하세요...")
        
        # CLI는 직접 태그를 인자로 받습니다
        add_tags_command = f'adxp-cli model tag-add {created_model_id} test cli-v2 example'
        
        success, stdout, stderr = run_cli_command(add_tags_command)
        
        if success:
            print("[SUCCESS] 태그 추가 성공!")
            print(stdout)
        else:
            print(f"[ERROR] 태그 추가 실패: {stderr}")
        
        # 8. 모델 삭제 (자동 확인)
        print("\n8. 모델 삭제")
        print("자동으로 모델을 삭제합니다...")
        
        # 자동 확인을 위해 echo를 사용
        delete_command = f'echo y | adxp-cli model delete {created_model_id}'
        success, stdout, stderr = run_cli_command(delete_command)
        if success:
            print("[SUCCESS] 모델 삭제 성공!")
            print(stdout)
        else:
            print(f"[ERROR] 모델 삭제 실패: {stderr}")
    else:
        print(f"[ERROR] 모델 생성 실패: {stderr}")
        print("   - 프로바이더 ID를 실제 값으로 변경하거나")
        print("   - API 권한을 확인해주세요.")
    
    print("\n🎉 모든 CLI 테스트가 완료되었습니다!")
    print("=" * 60)


if __name__ == "__main__":
    main()
