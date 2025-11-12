"""HML 파일 구조 분석 스크립트"""
import os
import sys
import zipfile
from xml.etree import ElementTree as ET

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding='utf-8')

hml_path = r"C:\Users\이헌승\Dropbox\Management Program\python\PythonProject\omr_scan\module\resources\test_papers\test\고1 test\10월 18일 명제2.hml"

print(f"파일 크기: {os.path.getsize(hml_path):,} bytes")
print("\n=== ZIP 파일 여부 확인 ===")

# ZIP 파일인지 확인
try:
    with zipfile.ZipFile(hml_path, 'r') as zf:
        print("OK - ZIP 아카이브입니다")
        print(f"\n포함된 파일 목록 ({len(zf.namelist())}개):")
        for name in zf.namelist()[:20]:
            print(f"  - {name}")
except zipfile.BadZipFile:
    print("NOT ZIP - XML 파일로 읽기 시도...\n")

    # XML 파일로 읽기
    try:
        tree = ET.parse(hml_path)
        root = tree.getroot()

        print(f"OK - XML 파일입니다")
        print(f"루트 태그: {root.tag}")
        print(f"루트 속성: {root.attrib}")

        print("\n최상위 자식 태그들:")
        for child in list(root)[:10]:
            print(f"  - {child.tag}: {child.attrib}")

        # 메타데이터 찾기
        print("\n=== 메타데이터 검색 ===")
        for elem in root.iter():
            tag_lower = elem.tag.lower()
            if any(keyword in tag_lower for keyword in ['meta', 'info', 'property', 'author', 'title', 'date']):
                print(f"{elem.tag}: {elem.attrib}")
                if elem.text and elem.text.strip():
                    print(f"  텍스트: {elem.text.strip()[:100]}")

    except Exception as e:
        print(f"FAIL - XML 파싱 실패: {e}")

        # 텍스트로 읽기
        print("\n처음 2000자:")
        with open(hml_path, 'r', encoding='utf-8') as f:
            print(f.read(2000))
