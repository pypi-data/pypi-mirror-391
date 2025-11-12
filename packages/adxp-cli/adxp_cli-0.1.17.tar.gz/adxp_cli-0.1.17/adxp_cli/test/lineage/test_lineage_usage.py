"""
Lineage CLI 사용 예제
"""

import subprocess
import sys
import os


def run_cli_command(command):
    """CLI 명령어 실행"""
    try:
        # Windows에서는 cp949가 기본 인코딩이지만, UTF-8을 시도하고 실패하면 cp949 사용
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return None, str(e), 1


def wait_for_enter(step_name):
    """사용자가 엔터를 누를 때까지 대기"""
    print(f"단계 {step_name} 완료!")
    print("다음 단계로 진행하려면 엔터를 누르세요...")
    input()
    print()


def main():
    """Lineage CLI 사용 예제"""
    
    print("Lineage CLI 사용 예제")
    print("=" * 60)
    
    # 1. Downstream lineage 조회
    print("1. Downstream lineage 조회")
    print("=" * 60)
    
    object_key = input("조회할 객체의 key를 입력하세요 (예: 모델 UUID): ").strip()
    
    command = f"adxp-cli lineage get {object_key} --direction downstream --action USE --max-depth 5"
    print(f"실행 명령어: {command}")
    print("=" * 60)
    
    stdout, stderr, return_code = run_cli_command(command)
    
    print("STDOUT:")
    print(stdout if stdout else "None")
    print("STDERR:")
    print(stderr if stderr else "None")
    print(f"Return Code: {return_code}")
    
    if return_code != 0:
        print("명령어 실행 실패 - 인증이 필요할 수 있습니다.")
        print("다음 명령어로 로그인하세요: adxp-cli auth login")
    
    print("=" * 60)
    wait_for_enter("Downstream lineage 조회")
    
    # 2. Upstream lineage 조회
    print("2. Upstream lineage 조회")
    print("=" * 60)
    
    command = f"adxp-cli lineage get {object_key} --direction upstream --action USE --max-depth 3"
    print(f"실행 명령어: {command}")
    print("=" * 60)
    
    stdout, stderr, return_code = run_cli_command(command)
    
    print("STDOUT:")
    print(stdout if stdout else "None")
    print("STDERR:")
    print(stderr if stderr else "None")
    print(f"Return Code: {return_code}")
    
    if return_code != 0:
        print("명령어 실행 실패 - 인증이 필요할 수 있습니다.")
        print("다음 명령어로 로그인하세요: adxp-cli auth login")
    
    print("=" * 60)
    wait_for_enter("Upstream lineage 조회")
    
    # 3. CREATE action으로 조회
    print("3. CREATE action으로 lineage 조회")
    print("=" * 60)
    
    command = f"adxp-cli lineage get {object_key} --direction downstream --action CREATE --max-depth 3"
    print(f"실행 명령어: {command}")
    print("=" * 60)
    
    stdout, stderr, return_code = run_cli_command(command)
    
    print("STDOUT:")
    print(stdout if stdout else "None")
    print("STDERR:")
    print(stderr if stderr else "None")
    print(f"Return Code: {return_code}")
    
    if return_code != 0:
        print("명령어 실행 실패 - 인증이 필요할 수 있습니다.")
        print("다음 명령어로 로그인하세요: adxp-cli auth login")
    
    print("=" * 60)
    wait_for_enter("CREATE action lineage 조회")
    
    # 4. JSON 출력
    print("4. JSON 출력으로 lineage 조회")
    print("=" * 60)
    
    command = f"adxp-cli lineage get {object_key} --direction downstream --json"
    print(f"실행 명령어: {command}")
    print("=" * 60)
    
    stdout, stderr, return_code = run_cli_command(command)
    
    print("STDOUT:")
    print(stdout if stdout else "None")
    print("STDERR:")
    print(stderr if stderr else "None")
    print(f"Return Code: {return_code}")
    
    if return_code != 0:
        print("명령어 실행 실패 - 인증이 필요할 수 있습니다.")
        print("다음 명령어로 로그인하세요: adxp-cli auth login")
    
    print("=" * 60)
    
    print("\n모든 테스트가 완료되었습니다!")
    print("=" * 60)


if __name__ == "__main__":
    main()

