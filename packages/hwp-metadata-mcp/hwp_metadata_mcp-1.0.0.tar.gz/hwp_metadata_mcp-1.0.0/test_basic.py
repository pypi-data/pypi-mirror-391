"""기본 기능 테스트 스크립트"""

import sys
import os
import io

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hwp_metadata_mcp.models import HwpMetadata
from hwp_metadata_mcp.hwp_parser import detect_file_type
from hwp_metadata_mcp.hwpx_parser import HwpxParser
from datetime import datetime


def test_model():
    """Pydantic 모델 테스트"""
    print("=" * 50)
    print("1. Pydantic 모델 테스트")
    print("=" * 50)

    metadata = HwpMetadata(
        file_path="/test/document.hwp",
        file_type="HWP",
        file_size=51200,
        title="테스트 문서",
        author="홍길동",
        created_date=datetime.now(),
        page_count=5,
        is_encrypted=False
    )

    print(f"✓ 모델 생성 성공")
    print(f"  제목: {metadata.title}")
    print(f"  작성자: {metadata.author}")
    print(f"  페이지: {metadata.page_count}")
    print()

    # JSON 직렬화 테스트
    json_str = metadata.model_dump_json(indent=2, exclude_none=True)
    print("✓ JSON 직렬화 성공:")
    print(json_str[:200] + "...")
    print()


def test_file_type_detection():
    """파일 타입 감지 테스트"""
    print("=" * 50)
    print("2. 파일 타입 감지 테스트")
    print("=" * 50)

    # 현재 프로젝트에서 HWP 파일 찾기
    hwp_search_dirs = [
        os.path.join("..", "data", "answer_notes", "templates"),
        os.path.join("..", "..", "시험지"),
    ]

    found_hwp = False
    for search_dir in hwp_search_dirs:
        if os.path.exists(search_dir):
            for file in os.listdir(search_dir):
                if file.lower().endswith(('.hwp', '.hwpx')):
                    file_path = os.path.join(search_dir, file)
                    try:
                        file_type = detect_file_type(file_path)
                        print(f"✓ {file}: {file_type}")
                        found_hwp = True
                    except Exception as e:
                        print(f"✗ {file}: {e}")

    if not found_hwp:
        print("⚠ 테스트할 HWP/HWPX 파일을 찾을 수 없습니다")
    print()


def test_tools():
    """MCP Tools 인터페이스 테스트"""
    print("=" * 50)
    print("3. MCP Tools 인터페이스 테스트")
    print("=" * 50)

    from hwp_metadata_mcp.server import extract_metadata

    # 테스트 파일 경로
    test_paths = [
        os.path.join("..", "data", "answer_notes", "templates", "error_note_sample.hwpx"),
    ]

    for test_path in test_paths:
        if os.path.exists(test_path):
            print(f"테스트 파일: {os.path.basename(test_path)}")
            try:
                result = extract_metadata(test_path)
                print(f"✓ 메타데이터 추출 성공")
                print(f"  파일 타입: {result.file_type}")
                print(f"  파일 크기: {result.file_size:,} bytes")
                print(f"  제목: {result.title or '(없음)'}")
                print(f"  작성자: {result.author or '(없음)'}")
                print(f"  페이지 수: {result.page_count or '(없음)'}")
                print(f"  HWP 버전: {result.hwp_version or '(없음)'}")
                return
            except Exception as e:
                print(f"✗ 오류: {e}")

    print("⚠ 테스트 가능한 파일이 없습니다")
    print()


def main():
    print("\n" + "=" * 50)
    print("HWP Metadata MCP Server - 기본 기능 테스트")
    print("=" * 50 + "\n")

    try:
        test_model()
        test_file_type_detection()
        test_tools()

        print("=" * 50)
        print("✓ 모든 테스트 완료!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
