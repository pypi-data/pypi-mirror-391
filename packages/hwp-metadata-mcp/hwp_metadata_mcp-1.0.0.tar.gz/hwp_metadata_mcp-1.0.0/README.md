# HWP Metadata MCP Server

한글(HWP/HWPX) 파일의 메타데이터를 추출하는 MCP(Model Context Protocol) 서버입니다.

## 기능

- **HWP 5.0 지원**: OLE 기반 바이너리 HWP 파일
- **HWPX 지원**: XML 기반 오픈 포맷 HWPX 파일
- **자동 감지**: 파일 형식을 자동으로 감지하여 처리
- **크로스 플랫폼**: Windows, Linux, macOS 지원
- **HWP 설치 불필요**: 순수 Python 라이브러리로 구현

## 추출 가능한 메타데이터

- **문서 정보**: 제목, 작성자, 키워드, 주제, 설명
- **시간 정보**: 생성일, 수정일, 마지막 인쇄일
- **문서 통계**: 페이지 수, 단어 수, 문자 수, 문단 수
- **보안 정보**: 암호화 여부, 읽기 전용 여부
- **기술 정보**: HWP 버전, 사용된 글꼴 목록
- **애플리케이션 정보**: 생성 프로그램 및 버전

## 설치

```bash
# pip 사용
pip install hwp-metadata-mcp

# uv 사용 (권장)
uv add hwp-metadata-mcp

# 개발 버전 설치
git clone https://github.com/heonseung4-del/hwp-metadata-mcp
cd hwp-metadata-mcp
uv pip install -e .
```

## 사용법

### Claude Desktop에서 사용

`claude_desktop_config.json` 파일에 다음을 추가하세요:

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hwp-metadata": {
      "command": "uvx",
      "args": ["hwp-metadata-mcp"]
    }
  }
}
```

또는 로컬 설치된 경우:

```json
{
  "mcpServers": {
    "hwp-metadata": {
      "command": "python",
      "args": ["-m", "hwp_metadata_mcp.server"]
    }
  }
}
```

### Python에서 직접 사용

```python
from hwp_metadata_mcp.hwp_parser import HwpParser
from hwp_metadata_mcp.hwpx_parser import HwpxParser
from hwp_metadata_mcp.hwp_parser import detect_file_type

# 자동 감지
file_type = detect_file_type("document.hwp")
if file_type == "HWP":
    metadata = HwpParser.parse("document.hwp")
elif file_type == "HWPX":
    metadata = HwpxParser.parse("document.hwpx")

# 메타데이터 접근
print(f"제목: {metadata.title}")
print(f"작성자: {metadata.author}")
print(f"페이지 수: {metadata.page_count}")
print(f"생성일: {metadata.created_date}")
```

### MCP Tools

서버는 다음 3개의 tool을 제공합니다:

#### 1. `extract_metadata` (권장)
파일 형식을 자동으로 감지하여 메타데이터 추출

```python
# Claude Desktop에서:
# "이 HWP 파일의 메타데이터를 알려줘: /path/to/file.hwp"
```

#### 2. `extract_hwp_metadata`
HWP 5.0 파일 전용

#### 3. `extract_hwpx_metadata`
HWPX 파일 전용

### MCP Resources

URI를 통해 메타데이터 조회:

```
hwp://metadata//path/to/document.hwp
hwp://metadata//path/to/document.hwpx
```

## 개발

### 요구사항

- Python 3.10 이상
- mcp >= 1.0.0
- pydantic >= 2.0.0
- olefile >= 0.46

### 로컬 테스트

```bash
# MCP Inspector로 테스트
uv run mcp dev src/hwp_metadata_mcp/server.py

# 직접 실행
uv run python -m hwp_metadata_mcp.server
```

### 테스트 실행

```bash
# 테스트 패키지 설치
uv add --dev pytest pytest-asyncio

# 테스트 실행
pytest tests/
```

## 지원 환경

- **OS**: Windows, Linux, macOS
- **Python**: 3.10, 3.11, 3.12
- **HWP**: 5.0 이상
- **HWPX**: 모든 버전

## 제한사항

- **암호화된 HWP 파일**: 암호화 여부는 확인 가능하지만, 암호로 보호된 파일의 상세 메타데이터는 추출할 수 없습니다
- **문서 내용**: 메타데이터만 추출하며, 본문 텍스트는 추출하지 않습니다
- **편집 기능 없음**: 읽기 전용입니다. 파일 편집은 지원하지 않습니다

## 라이선스

BSD-3-Clause License

## 기여

이슈 및 Pull Request를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 관련 프로젝트

- [pyhwp](https://github.com/mete0r/pyhwp) - HWP 파일 파서 및 변환기
- [olefile](https://github.com/decalage2/olefile) - OLE 파일 파서
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol

## 문의

이슈를 통해 문의해주세요: [GitHub Issues](https://github.com/heonseung4-del/hwp-metadata-mcp/issues)
