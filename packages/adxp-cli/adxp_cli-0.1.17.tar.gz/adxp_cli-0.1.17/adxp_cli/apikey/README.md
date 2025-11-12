# API Key CLI

A.X Platform의 API Key를 관리하는 CLI 도구입니다.

## 사전 준비

API Key CLI를 사용하기 전에 인증이 필요합니다:

```bash
adxp-cli auth login
```

## 명령어 개요

```bash
adxp-cli apikey [COMMAND] [OPTIONS]
```

## 지원하는 명령어

### 1. API Key 목록 조회

```bash
adxp-cli apikey list [OPTIONS]
```

**기능**: 생성된 API Key 목록을 조회합니다.

**옵션**:

- `--page`: 페이지 번호 (기본값: 1)
- `--size`: 페이지 크기 (기본값: 10)
- `--sort`: 정렬 조건
- `--filter`: 필터 조건
- `--search`: 검색 키워드
- `--json-output`: JSON 형태로 출력

**예시**:

```bash
# 기본 목록 조회
adxp-cli apikey list

# 페이지네이션과 검색
adxp-cli apikey list --page 2 --size 20 --search "model"

# JSON 형태로 출력
adxp-cli apikey list --json-output
```

### 2. API Key 생성

```bash
adxp-cli apikey create [OPTIONS]
```

**기능**: 새로운 API Key를 생성합니다.

**옵션**:

- `--gateway-type`: Gateway 타입 (model/agent/mcp) **[필수]**
- `--is-master`: Master Key 여부 (true/false) **[필수]**
- `--serving-id`: Serving ID (is-master=false일 때 필수)
- `--allowed-host`: 허용된 호스트 (쉼표로 구분)
- `--tag`: 태그 (쉼표로 구분)
- `--started-at`: 시작 날짜 (YYYY-MM-DD 형식)
- `--expires-at`: 만료 날짜 (YYYY-MM-DD 형식)
- `--project-id`: 프로젝트 ID **[필수]**
- `--json-output`: JSON 형태로 출력

**예시**:

```bash
# Master API Key 생성
adxp-cli apikey create \
  --gateway-type model \
  --is-master true \
  --project-id your-project-id

# 특정 Serving용 API Key 생성
adxp-cli apikey create \
  --gateway-type agent \
  --is-master false \
  --serving-id serving-id-1,serving-id-2 \
  --project-id your-project-id

# 태그와 만료일이 있는 API Key 생성
adxp-cli apikey create \
  --gateway-type model \
  --is-master true \
  --tag production,api \
  --expires-at 2024-12-31 \
  --project-id your-project-id
```

### 3. API Key 수정

```bash
adxp-cli apikey update [API_KEY_ID] [OPTIONS]
```

**기능**: 기존 API Key의 정보를 수정합니다.

**인수**:

- `API_KEY_ID`: 수정할 API Key ID (옵션으로 제공 가능)

**옵션**:

- `--is-master`: Master Key 여부 (true/false)
- `--is-active`: 활성화 상태 (true/false)
- `--serving-id`: Serving ID (is-master=false일 때 필수)
- `--allowed-host`: 허용된 호스트 (여러 번 사용 가능)
- `--tag`: 태그 (여러 번 사용 가능)
- `--started-at`: 시작 날짜 (YYYY-MM-DD 또는 null)
- `--expires-at`: 만료 날짜 (YYYY-MM-DD 또는 null)

**예시**:

```bash
# API Key 비활성화
adxp-cli apikey update api-key-id-123 --is-active false

# 태그 추가
adxp-cli apikey update api-key-id-123 --tag production --tag api

# 만료일 수정
adxp-cli apikey update api-key-id-123 --expires-at 2025-12-31

# Serving ID 수정 (Non-master Key인 경우)
adxp-cli apikey update api-key-id-123 \
  --is-master false \
  --serving-id new-serving-id-1,new-serving-id-2
```

### 4. API Key 삭제

```bash
adxp-cli apikey delete [API_KEY_ID]
```

**기능**: API Key를 삭제합니다.

**인수**:

- `API_KEY_ID`: 삭제할 API Key ID (옵션으로 제공 가능)

**예시**:

```bash
# API Key 삭제 (ID 직접 지정)
adxp-cli apikey delete api-key-id-123

# API Key 삭제 (대화형으로 ID 입력)
adxp-cli apikey delete
```

**주의**: 삭제 시 확인 메시지가 표시됩니다. 삭제된 API Key는 복구할 수 없습니다.

## Gateway 타입 설명

### Model Gateway

- **용도**: 모델 서빙 API 접근
- **Master Key**: 모든 모델에 접근 가능
- **Non-Master Key**: 특정 Serving ID에만 접근 가능

### Agent Gateway

- **용도**: 에이전트 API 접근
- **Master Key**: 모든 에이전트에 접근 가능
- **Non-Master Key**: 특정 Serving ID에만 접근 가능

### MCP Gateway

- **용도**: MCP (Model Context Protocol) API 접근
- **Master Key**: 모든 MCP 리소스에 접근 가능
- **Non-Master Key**: 특정 Serving ID에만 접근 가능

## 출력 예시

### 목록 조회 출력

```
API Key List:
1. ID=4a33c93e-b0f5-40d7-a665-218958b98601 | Type=model | Master=True | Tag=[] | Key=sk-9ec4c11b71de943ec...
2. ID=a21bf470-ed82-4f4a-bdcc-3f0a3748d88d | Type=agent | Master=False | Tag=[production] | Key=sk-d21a4bbd5d9e4eaa3...
```

### JSON 출력 예시

```json
{
  "data": [
    {
      "api_key_id": "4a33c93e-b0f5-40d7-a665-218958b98601",
      "gateway_type": "model",
      "is_master": true,
      "api_key": "sk-9ec4c11b71de943ec...",
      "tag": [],
      "is_active": true
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
❌ Failed to create API key: 403 Forbidden
```

### 유효성 검사 오류

```
❌ Failed to create API key: 422 Client Error: Unprocessable Entity
```

## 주의사항

1. **API Key 보안**: 생성된 API Key는 안전하게 보관하세요.
2. **Master vs Non-Master**: Master Key는 모든 리소스에 접근 가능하므로 신중하게 사용하세요.
3. **만료일 설정**: 보안을 위해 적절한 만료일을 설정하는 것을 권장합니다.
4. **태그 활용**: API Key를 분류하고 관리하기 위해 태그를 활용하세요.
5. **정기적 정리**: 사용하지 않는 API Key는 정기적으로 삭제하세요.

## 도움말

특정 명령어에 대한 자세한 도움말을 보려면:

```bash
adxp-cli apikey --help
adxp-cli apikey create --help
adxp-cli apikey update --help
```
