#!/usr/bin/env python3
"""
CLI Backend-AI Endpoints 테스트

이 테스트는 finetuning CLI에서 --use-backend-ai 옵션이 제대로 작동하는지 확인합니다.
"""

import os
import subprocess
import time

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
        
        if result.returncode == 0:
            print("[SUCCESS] 명령어 실행 성공")
            if result.stdout:
                print(f"출력: {result.stdout.strip()}")
            return True, result.stdout.strip(), result.stderr.strip()
        else:
            print(f"[ERROR] 명령어 실행 실패 (코드: {result.returncode})")
            if result.stderr:
                print(f"오류: {result.stderr.strip()}")
            return False, result.stdout.strip(), result.stderr.strip()
            
    except Exception as e:
        print(f"[ERROR] 명령어 실행 중 오류: {e}")
        return False, "", str(e)

def test_backend_ai_endpoints():
    """Backend-AI 엔드포인트 테스트"""
    print("=" * 60)
    print("Backend-AI 엔드포인트 테스트 시작")
    print("=" * 60)
    
    # 1. 일반 엔드포인트로 트레이닝 목록 조회
    print("\n1. 일반 엔드포인트로 트레이닝 목록 조회")
    print("테스트: adxp-cli finetuning training list --size 5")
    
    success, stdout, stderr = run_cli_command("adxp-cli finetuning training list --size 5")
    if success:
        print("[SUCCESS] 일반 엔드포인트로 트레이닝 목록 조회 성공!")
        print("응답에서 'api/v1/finetuning/' 엔드포인트가 사용되었습니다.")
    else:
        print("[ERROR] 일반 엔드포인트로 트레이닝 목록 조회 실패")
        print(f"오류: {stderr}")
    
    # 2. Backend-AI 엔드포인트로 트레이닝 목록 조회
    print("\n2. Backend-AI 엔드포인트로 트레이닝 목록 조회")
    print("테스트: adxp-cli finetuning training list --size 5 --use-backend-ai")
    
    success, stdout, stderr = run_cli_command("adxp-cli finetuning training list --size 5 --use-backend-ai")
    if success:
        print("[SUCCESS] Backend-AI 엔드포인트로 트레이닝 목록 조회 성공!")
        print("응답에서 'api/v1/backend-ai/finetuning/' 엔드포인트가 사용되었습니다.")
    else:
        print("[ERROR] Backend-AI 엔드포인트로 트레이닝 목록 조회 실패")
        print(f"오류: {stderr}")
    
    # 3. 일반 엔드포인트로 트레이닝 생성 (테스트용)
    print("\n3. 일반 엔드포인트로 트레이닝 생성")
    training_name = f"test-backend-ai-{int(time.time())}"
    create_command = f'adxp-cli finetuning training create --name "{training_name}" --project-id "24ba585a-02fc-43d8-b9f1-f7ca9e020fe5" --trainer-id "77a85f64-5717-4562-b3fc-2c963f66afa6" --dataset-ids "0c178ea6-fbc9-44f2-8b1e-6bb101901a8c" --base-model-id "cb0a4bdb-d2d6-48b3-98a3-b6333484329f" --resource "{{\\"cpu_quota\\": 4, \\"mem_quota\\": 8, \\"gpu_quota\\": 1, \\"gpu_type\\": \\"T4\\"}}" --params "learning_rate=0.0001" --description "Backend-AI 테스트용 트레이닝"'
    
    print(f"테스트: {create_command}")
    success, stdout, stderr = run_cli_command(create_command)
    if success:
        print("[SUCCESS] 일반 엔드포인트로 트레이닝 생성 성공!")
        print("응답에서 'api/v1/finetuning/' 엔드포인트가 사용되었습니다.")
    else:
        print("[ERROR] 일반 엔드포인트로 트레이닝 생성 실패")
        print(f"오류: {stderr}")
    
    # 4. Backend-AI 엔드포인트로 트레이닝 생성 (테스트용)
    print("\n4. Backend-AI 엔드포인트로 트레이닝 생성")
    training_name_backend = f"test-backend-ai-v2-{int(time.time())}"
    create_command_backend = f'adxp-cli finetuning training create --name "{training_name_backend}" --project-id "24ba585a-02fc-43d8-b9f1-f7ca9e020fe5" --trainer-id "77a85f64-5717-4562-b3fc-2c963f66afa6" --dataset-ids "0c178ea6-fbc9-44f2-8b1e-6bb101901a8c" --base-model-id "cb0a4bdb-d2d6-48b3-98a3-b6333484329f" --resource "{{\\"cpu_quota\\": 4, \\"mem_quota\\": 8, \\"gpu_quota\\": 1, \\"gpu_type\\": \\"T4\\"}}" --params "learning_rate=0.0001" --description "Backend-AI 테스트용 트레이닝" --use-backend-ai'
    
    print(f"테스트: {create_command_backend}")
    success, stdout, stderr = run_cli_command(create_command_backend)
    if success:
        print("[SUCCESS] Backend-AI 엔드포인트로 트레이닝 생성 성공!")
        print("응답에서 'api/v1/backend-ai/finetuning/' 엔드포인트가 사용되었습니다.")
    else:
        print("[ERROR] Backend-AI 엔드포인트로 트레이닝 생성 실패")
        print(f"오류: {stderr}")
    
    print("\n" + "=" * 60)
    print("Backend-AI 엔드포인트 테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    test_backend_ai_endpoints()
