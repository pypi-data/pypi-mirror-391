# Authorization CLI

A.X Platform의 프로젝트, 사용자, 그룹, 역할 관리를 위한 CLI 도구입니다.

## 사전 준비

Authorization CLI를 사용하기 전에 인증이 필요합니다:

```bash
adxp-cli auth login
```

## 명령어 개요

```bash
adxp-cli authorization [COMMAND] [OPTIONS]
# 또는 약어 사용
adxp-cli authz [COMMAND] [OPTIONS]
```

**참고**: `authorization` 대신 `authz`라는 약어를 사용할 수 있습니다.

## 지원하는 명령어

### 1. Project 관리

#### 1.1 프로젝트 목록 조회

```bash
adxp-cli authorization project list [OPTIONS]
```

**기능**: 생성된 프로젝트 목록을 조회합니다.

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--json-output`: JSON 형태로 출력

**예시**:

```bash
# 기본 목록 조회
adxp-cli authorization project list
# 또는 약어 사용
adxp-cli authz project list

# 페이지네이션
adxp-cli authz project list --page 2 --size 20

# JSON 형태로 출력
adxp-cli authz project list --json-output
```

#### 1.2 프로젝트 생성

```bash
adxp-cli authorization project create [OPTIONS]
```

**기능**: 새로운 프로젝트를 생성합니다.

**옵션**:

- `--name`: 프로젝트 이름 **[필수]**
- `--node-type`: 노드 타입 (기본값: task)

**예시**:

```bash
# 기본 프로젝트 생성
adxp-cli authorization project create --name "my-project"

# 특정 노드 타입으로 생성
adxp-cli authorization project create --name "my-project" --node-type "inference"
```

**프롬프트 예시**:

```
Project name: my-new-project
Enter resource quota values below:
-----------------------------------------
CPU quota (Core): 10
Memory quota (GB): 32
GPU quota (Core): 2
```

#### 1.3 프로젝트 수정

```bash
adxp-cli authorization project update [NAME] [OPTIONS]
```

**기능**: 기존 프로젝트의 정보를 수정합니다.

**인수**:

- `NAME`: 수정할 프로젝트 이름 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--node-type`: 노드 타입 (기본값: task)

**예시**:

```bash
# 프로젝트 이름으로 직접 수정
adxp-cli authorization project update my-project

# 대화형으로 프로젝트 선택하여 수정
adxp-cli authorization project update
```

#### 1.4 프로젝트 삭제

```bash
adxp-cli authorization project delete [NAME] [OPTIONS]
```

**기능**: 프로젝트를 삭제합니다.

**인수**:

- `NAME`: 삭제할 프로젝트 이름 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 프로젝트 이름으로 직접 삭제
adxp-cli authorization project delete my-project

# 대화형으로 프로젝트 선택하여 삭제
adxp-cli authorization project delete
```

### 2. Role 관리 (Project 하위)

#### 2.1 역할 목록 조회

```bash
adxp-cli authorization project role list [OPTIONS]
```

**기능**: 현재 프로젝트의 역할 목록을 조회합니다.

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--json-output`: JSON 형태로 출력

**예시**:

```bash
# 기본 역할 목록 조회
adxp-cli authorization project role list

# JSON 형태로 출력
adxp-cli authorization project role list --json-output
```

#### 2.2 역할 생성

```bash
adxp-cli authorization project role create [OPTIONS]
```

**기능**: 새로운 역할을 생성합니다.

**옵션**:

- `--name`: 역할 이름 **[필수]**
- `--description`: 역할 설명 (기본값: 빈 문자열)

**예시**:

```bash
# 기본 역할 생성
adxp-cli authorization project role create --name "developer"

# 설명과 함께 역할 생성
adxp-cli authorization project role create --name "admin" --description "Administrator role"
```

#### 2.3 역할 수정

```bash
adxp-cli authorization project role update [ROLE_NAME] [OPTIONS]
```

**기능**: 기존 역할의 설명을 수정합니다.

**인수**:

- `ROLE_NAME`: 수정할 역할 이름 (옵션으로 제공 가능)

**옵션**:

- `--description`: 새로운 설명
- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 역할 이름으로 직접 수정
adxp-cli authorization project role update developer --description "Updated description"

# 대화형으로 역할 선택하여 수정
adxp-cli authorization project role update
```

#### 2.4 역할 삭제

```bash
adxp-cli authorization project role delete [ROLE_NAME] [OPTIONS]
```

**기능**: 역할을 삭제합니다.

**인수**:

- `ROLE_NAME`: 삭제할 역할 이름 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 역할 이름으로 직접 삭제
adxp-cli authorization project role delete old-role

# 대화형으로 역할 선택하여 삭제
adxp-cli authorization project role delete
```

### 3. User 관리

#### 3.1 사용자 목록 조회

```bash
adxp-cli authorization user list [OPTIONS]
```

**기능**: 시스템의 사용자 목록을 조회합니다.

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--json-output`: JSON 형태로 출력

**예시**:

```bash
# 기본 사용자 목록 조회
adxp-cli authorization user list

# JSON 형태로 출력
adxp-cli authorization user list --json-output
```

#### 3.2 사용자 생성

```bash
adxp-cli authorization user create [OPTIONS]
```

**기능**: 새로운 사용자를 생성합니다.

**옵션**:

- `--username`: 사용자명 **[필수]**
- `--email`: 이메일 주소 **[필수]**
- `--first-name`: 이름 **[필수]**
- `--last-name`: 성 **[필수]**

**예시**:

```bash
# 새 사용자 생성
adxp-cli authorization user create \
  --username "john.doe" \
  --email "john.doe@company.com" \
  --first-name "John" \
  --last-name "Doe"
```

#### 3.3 사용자 수정

```bash
adxp-cli authorization user update [USERNAME] [OPTIONS]
```

**기능**: 기존 사용자의 정보를 수정합니다.

**인수**:

- `USERNAME`: 수정할 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 사용자명으로 직접 수정
adxp-cli authorization user update john.doe

# 대화형으로 사용자 선택하여 수정
adxp-cli authorization user update
```

#### 3.4 사용자 삭제

```bash
adxp-cli authorization user delete [USERNAME] [OPTIONS]
```

**기능**: 사용자를 삭제합니다.

**인수**:

- `USERNAME`: 삭제할 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 사용자명으로 직접 삭제
adxp-cli authorization user delete john.doe

# 대화형으로 사용자 선택하여 삭제
adxp-cli authorization user delete
```

### 4. User-Role 관리

#### 4.1 사용자에게 할당된 역할 조회

```bash
adxp-cli authorization user roles list [USERNAME] [OPTIONS]
```

**기능**: 특정 사용자에게 할당된 역할 목록을 조회합니다.

**인수**:

- `USERNAME`: 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 특정 사용자의 역할 조회
adxp-cli authorization user roles list john.doe

# 대화형으로 사용자 선택하여 역할 조회
adxp-cli authorization user roles list
```

#### 4.2 사용자에게 역할 할당

```bash
adxp-cli authorization user roles assign [USERNAME] [OPTIONS]
```

**기능**: 사용자에게 하나 이상의 역할을 할당합니다.

**인수**:

- `USERNAME`: 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--roles`: 할당할 역할 이름들 (쉼표로 구분)
- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--role-page`: 역할 페이지 번호 (기본값: 1)
- `--role-size`: 역할 페이지 크기 (기본값: 10)

**예시**:

```bash
# 특정 사용자에게 역할 할당
adxp-cli authorization user roles assign john.doe --roles "developer,reviewer"

# 대화형으로 사용자와 역할 선택하여 할당
adxp-cli authorization user roles assign
```

#### 4.3 사용자에서 역할 제거

```bash
adxp-cli authorization user roles delete [USERNAME] [OPTIONS]
```

**기능**: 사용자에서 하나 이상의 역할을 제거합니다.

**인수**:

- `USERNAME`: 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--roles`: 제거할 역할 이름들 (쉼표로 구분)
- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--role-page`: 역할 페이지 번호 (기본값: 1)
- `--role-size`: 역할 페이지 크기 (기본값: 10)

**예시**:

```bash
# 특정 사용자에서 역할 제거
adxp-cli authorization user roles delete john.doe --roles "reviewer"

# 대화형으로 사용자와 역할 선택하여 제거
adxp-cli authorization user roles delete
```

### 5. Group 관리

#### 5.1 그룹 목록 조회

```bash
adxp-cli authorization group list [OPTIONS]
```

**기능**: 시스템의 그룹 목록을 조회합니다.

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--json-output`: JSON 형태로 출력

**예시**:

```bash
# 기본 그룹 목록 조회
adxp-cli authorization group list

# JSON 형태로 출력
adxp-cli authorization group list --json-output
```

#### 5.2 그룹 생성

```bash
adxp-cli authorization group create [NAME] [OPTIONS]
```

**기능**: 새로운 그룹을 생성합니다.

**인수**:

- `NAME`: 그룹 이름 (옵션으로 제공 가능)

**예시**:

```bash
# 그룹 이름으로 직접 생성
adxp-cli authorization group create developers

# 대화형으로 그룹 이름 입력하여 생성
adxp-cli authorization group create
```

#### 5.3 그룹 수정

```bash
adxp-cli authorization group update [NAME] [OPTIONS]
```

**기능**: 기존 그룹의 정보를 수정합니다.

**인수**:

- `NAME`: 수정할 그룹 이름 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 그룹 이름으로 직접 수정
adxp-cli authorization group update developers

# 대화형으로 그룹 선택하여 수정
adxp-cli authorization group update
```

#### 5.4 그룹 삭제

```bash
adxp-cli authorization group delete [NAME] [OPTIONS]
```

**기능**: 그룹을 삭제합니다.

**인수**:

- `NAME`: 삭제할 그룹 이름 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 그룹 이름으로 직접 삭제
adxp-cli authorization group delete old-group

# 대화형으로 그룹 선택하여 삭제
adxp-cli authorization group delete
```

### 6. User-Group 관리

#### 6.1 사용자에게 할당된 그룹 조회

```bash
adxp-cli authorization group assigned [USERNAME] [OPTIONS]
```

**기능**: 특정 사용자에게 할당된 그룹 목록을 조회합니다.

**인수**:

- `USERNAME`: 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 특정 사용자의 그룹 조회
adxp-cli authorization group assigned john.doe

# 대화형으로 사용자 선택하여 그룹 조회
adxp-cli authorization group assigned
```

#### 6.2 사용자에게 할당 가능한 그룹 조회

```bash
adxp-cli authorization group available [USERNAME] [OPTIONS]
```

**기능**: 특정 사용자에게 할당 가능한 그룹 목록을 조회합니다.

**인수**:

- `USERNAME`: 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 특정 사용자에게 할당 가능한 그룹 조회
adxp-cli authorization group available john.doe

# 대화형으로 사용자 선택하여 할당 가능한 그룹 조회
adxp-cli authorization group available
```

#### 6.3 사용자에게 그룹 할당

```bash
adxp-cli authorization group assign [USERNAME] [OPTIONS]
```

**기능**: 사용자에게 그룹을 할당합니다.

**인수**:

- `USERNAME`: 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--group-id`: 할당할 그룹 ID
- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 특정 사용자에게 그룹 할당
adxp-cli authorization group assign john.doe --group-id "group-uuid-123"

# 대화형으로 사용자와 그룹 선택하여 할당
adxp-cli authorization group assign
```

#### 6.4 사용자에서 그룹 제거

```bash
adxp-cli authorization group unassign [USERNAME] [OPTIONS]
```

**기능**: 사용자에서 그룹을 제거합니다.

**인수**:

- `USERNAME`: 사용자명 (옵션으로 제공 가능)

**옵션**:

- `--group-id`: 제거할 그룹 ID
- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)

**예시**:

```bash
# 특정 사용자에서 그룹 제거
adxp-cli authorization group unassign john.doe --group-id "group-uuid-123"

# 대화형으로 사용자와 그룹 선택하여 제거
adxp-cli authorization group unassign
```

## 출력 예시

### 프로젝트 목록 출력

```
📂 Project List:
1. default
2. test-project
3. development
```

### 사용자 목록 출력

```
👥 User List:
1. admin (admin@company.com)
2. john.doe (john.doe@company.com)
3. jane.smith (jane.smith@company.com)
```

### 역할 목록 출력

```
👥 Roles for Project default:
1. admin (ID=role-uuid-1)
2. developer (ID=role-uuid-2)
3. viewer (ID=role-uuid-3)
```

### JSON 출력 예시

```json
{
  "data": [
    {
      "project": {
        "id": "project-uuid-123",
        "name": "default",
        "cpu_quota": 10,
        "memory_quota": 32,
        "gpu_quota": 2
      }
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10
}
```

## 에러 처리

### 인증 오류

```
🔐 401 Unauthorized : Please login again.
 Run: adxp-cli auth login
```

### 권한 오류

```
❌ Failed to create project: 403 Forbidden
```

### 유효성 검사 오류

```
❌ 프로젝트 'nonexistent' 를 찾을 수 없습니다.
```

## 주의사항

1. **프로젝트 컨텍스트**: Role 관리 명령어는 현재 로그인된 프로젝트 내에서만 작동합니다.
2. **삭제 확인**: 삭제 명령어는 확인 프롬프트가 표시됩니다.
3. **리소스 할당**: 프로젝트 생성 시 CPU, 메모리, GPU 할당량을 설정해야 합니다.
4. **사용자 권한**: 일부 명령어는 관리자 권한이 필요할 수 있습니다.
5. **대화형 모드**: 인수를 제공하지 않으면 대화형으로 선택할 수 있습니다.

## 도움말

특정 명령어에 대한 자세한 도움말을 보려면:

```bash
# 전체 명령어 또는 약어 사용
adxp-cli authorization --help
adxp-cli authz --help

# 하위 명령어들
adxp-cli authorization project --help
adxp-cli authz project --help

adxp-cli authorization project create --help
adxp-cli authz project create --help

adxp-cli authorization user --help
adxp-cli authz user --help

adxp-cli authorization group --help
adxp-cli authz group --help
```

**팁**: 긴 명령어를 입력하기 번거로우면 `authz` 약어를 사용하세요!
