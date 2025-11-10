# 피카츄 데이터 Notion 연동 가이드

## 개요
이 가이드는 n8n을 사용하여 PokeAPI에서 피카츄의 능력치 데이터를 가져와 Notion 데이터베이스에 자동으로 추가하는 워크플로우 설정 방법을 안내합니다.

## 사전 준비사항

### 1. Notion 데이터베이스 생성

Notion에서 새로운 데이터베이스를 생성하고 다음 속성(Properties)을 추가하세요:

| 속성 이름 | 타입 | 설명 |
|---------|------|------|
| Name | Title | 포켓몬 이름 (기본 제목 속성) |
| HP | Number | 체력 능력치 |
| Attack | Number | 공격력 능력치 |
| Defense | Number | 방어력 능력치 |
| Special Attack | Number | 특수 공격력 능력치 |
| Special Defense | Number | 특수 방어력 능력치 |
| Speed | Number | 스피드 능력치 |
| Types | Multi-select | 포켓몬 타입(들) |
| Weight | Number | 무게 |
| Height | Number | 키 |
| Image | URL | 포켓몬 이미지 URL |

### 2. Notion API 통합 설정

1. [Notion Integrations 페이지](https://www.notion.so/my-integrations) 접속
2. "New integration" 클릭
3. Integration 이름 입력 (예: "n8n Pokemon")
4. "Submit" 클릭
5. **Internal Integration Token** 복사 (나중에 사용)

### 3. 데이터베이스에 Integration 연결

1. Notion에서 생성한 데이터베이스 페이지 열기
2. 오른쪽 상단 "..." 메뉴 클릭
3. "Connections" → "Connect to" 선택
4. 생성한 Integration 선택

### 4. Database ID 확인

데이터베이스 URL에서 Database ID를 확인하세요:
```
https://www.notion.so/[workspace-name]/[DATABASE_ID]?v=...
```
예시: `https://www.notion.so/myworkspace/abc123def456...`
→ Database ID는 `abc123def456...` 부분입니다.

## n8n 워크플로우 설정

### 1. 워크플로우 임포트

1. n8n 인스턴스에 로그인
2. 좌측 메뉴에서 "Workflows" 클릭
3. 우측 상단 "Import from File" 클릭
4. `pokemon_to_notion_workflow.json` 파일 선택
5. "Import" 클릭

### 2. Notion Credentials 설정

1. "Add Notion Page" 노드 클릭
2. "Credentials" 드롭다운에서 "Create New" 선택
3. Notion API 타입 선택
4. **API Key** 필드에 앞서 복사한 Integration Token 입력
5. "Create" 클릭

### 3. Database ID 설정

1. "Add Notion Page" 노드에서 **Database ID** 필드 찾기
2. 앞서 확인한 Database ID 입력
3. "Save" 클릭

### 4. 속성 매핑 확인

"Add Notion Page" 노드의 "Properties" 섹션에서 각 필드가 올바르게 매핑되었는지 확인:

- **Name** → `{{ $json.pokemon_name }}`
- **HP** → `{{ $json.hp }}`
- **Attack** → `{{ $json.attack }}`
- **Defense** → `{{ $json.defense }}`
- **Special Attack** → `{{ $json.special_attack }}`
- **Special Defense** → `{{ $json.special_defense }}`
- **Speed** → `{{ $json.speed }}`
- **Types** → `{{ $json.types.split(', ') }}`
- **Weight** → `{{ $json.weight }}`
- **Height** → `{{ $json.height }}`
- **Image** → `{{ $json.image }}`

## 워크플로우 실행

### 테스트 실행

1. n8n 워크플로우 편집 화면에서 "Execute Workflow" 버튼 클릭
2. 각 노드의 실행 결과 확인:
   - **Get Pokemon - Pikachu**: PokeAPI 응답 데이터 확인
   - **Format Pokemon Data**: 변환된 데이터 확인
   - **Add Notion Page**: Notion 페이지 생성 결과 확인
3. Notion 데이터베이스에서 피카츄 페이지가 추가되었는지 확인

### 예상 결과

Notion에 다음과 같은 데이터가 포함된 피카츄 페이지가 생성됩니다:

- **Name**: pikachu
- **HP**: 35
- **Attack**: 55
- **Defense**: 40
- **Special Attack**: 50
- **Special Defense**: 50
- **Speed**: 90
- **Types**: electric
- **Weight**: 60
- **Height**: 4
- **Image**: https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png

## 워크플로우 구조

```
[Manual Trigger]
    ↓
[Get Pokemon - Pikachu]
    ↓ (PokeAPI에서 데이터 가져오기)
[Format Pokemon Data]
    ↓ (Notion 형식으로 데이터 변환)
[Add Notion Page]
    ↓ (Notion 데이터베이스에 페이지 추가)
```

## 커스터마이징

### 다른 포켓몬 추가하기

"Get Pokemon - Pikachu" 노드의 URL을 변경:
```
https://pokeapi.co/api/v2/pokemon/[포켓몬이름 또는 번호]
```

예시:
- 이상해씨: `https://pokeapi.co/api/v2/pokemon/bulbasaur` 또는 `/pokemon/1`
- 파이리: `https://pokeapi.co/api/v2/pokemon/charmander` 또는 `/pokemon/4`
- 꼬부기: `https://pokeapi.co/api/v2/pokemon/squirtle` 또는 `/pokemon/7`

### 여러 포켓몬 한 번에 추가하기

1. Manual Trigger 대신 "Schedule Trigger" 사용
2. "Get Pokemon" 노드 앞에 "Code" 노드 추가하여 포켓몬 리스트 생성
3. "Split In Batches" 노드로 반복 처리

예시 코드:
```javascript
// Code 노드
const pokemonList = ['pikachu', 'bulbasaur', 'charmander', 'squirtle'];
return pokemonList.map(name => ({ json: { pokemon: name } }));
```

## 문제 해결

### Notion API 오류

**에러**: `Could not connect to Notion`
- Notion Integration Token이 올바른지 확인
- Integration이 데이터베이스에 연결되었는지 확인

**에러**: `Database not found`
- Database ID가 정확한지 확인
- Integration에 데이터베이스 접근 권한이 있는지 확인

### 속성 매핑 오류

**에러**: `Property not found`
- Notion 데이터베이스의 속성 이름이 정확히 일치하는지 확인
- 대소문자 구분 주의

**에러**: `Invalid property type`
- 속성 타입이 올바른지 확인 (Number, Multi-select 등)
- Types 속성이 Multi-select로 설정되었는지 확인

### PokeAPI 오류

**에러**: `404 Not Found`
- 포켓몬 이름 철자가 정확한지 확인
- 소문자로 입력했는지 확인

## 추가 리소스

- [PokeAPI 공식 문서](https://pokeapi.co/docs/v2)
- [Notion API 공식 문서](https://developers.notion.com/)
- [n8n 공식 문서](https://docs.n8n.io/)
- [n8n Notion 노드 가이드](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.notion/)

## 라이센스 및 저작권

- PokeAPI: [BSD License](https://pokeapi.co/docs/v2#fairuse)
- Notion: [Notion API Terms](https://www.notion.so/Terms-and-Privacy-28ffdd083dc3473e9c2da6ec011b58ac)

---

**작성일**: 2025-11-07
**버전**: 1.0
