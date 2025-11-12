"""HWPX 파일 메타데이터 추출기"""

import os
import zipfile
from datetime import datetime
from typing import Optional
from xml.etree import ElementTree as ET

from .models import HwpMetadata


class HwpxParser:
    """HWPX (XML 기반 HWP) 파일 파서"""

    # XML 네임스페이스
    NAMESPACES = {
        "meta": "http://www.hancom.co.kr/hwpml/2011/metadata",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "hwpml": "http://www.hancom.co.kr/hwpml/2011/head",
    }

    @classmethod
    def parse(cls, file_path: str) -> HwpMetadata:
        """HWPX 파일에서 메타데이터 추출

        Args:
            file_path: HWPX 파일 경로

        Returns:
            HwpMetadata 객체

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            zipfile.BadZipFile: 유효하지 않은 ZIP 파일일 때
            ValueError: HWPX 형식이 아닐 때
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        file_size = os.path.getsize(file_path)

        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                # HWPX 파일인지 확인 (content.hpf 또는 content.xml)
                namelist = zf.namelist()
                has_content = any(
                    "Contents/content." in name and name.endswith((".hpf", ".xml"))
                    for name in namelist
                )
                if not has_content:
                    raise ValueError("유효한 HWPX 파일이 아닙니다")

                # 메타데이터 추출
                metadata_dict = {
                    "file_path": file_path,
                    "file_type": "HWPX",
                    "file_size": file_size,
                }

                # metadata.xml 파싱
                if "META-INF/metadata.xml" in zf.namelist():
                    cls._parse_metadata_xml(zf, metadata_dict)

                # header.xml 파싱 (문서 구조 정보)
                if "Contents/header.xml" in zf.namelist():
                    cls._parse_header_xml(zf, metadata_dict)

                return HwpMetadata(**metadata_dict)

        except zipfile.BadZipFile:
            raise ValueError(f"손상된 ZIP 파일입니다: {file_path}")

    @classmethod
    def _parse_metadata_xml(cls, zf: zipfile.ZipFile, metadata_dict: dict) -> None:
        """metadata.xml 파싱 (Dublin Core 메타데이터)"""
        try:
            with zf.open("META-INF/metadata.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()

                # Dublin Core 메타데이터 추출
                metadata_dict["title"] = cls._get_text(
                    root, ".//dc:title", "title"
                )
                metadata_dict["author"] = cls._get_text(
                    root, ".//dc:creator", "creator"
                )
                metadata_dict["subject"] = cls._get_text(
                    root, ".//dc:subject", "subject"
                )
                metadata_dict["keywords"] = cls._get_text(
                    root, ".//meta:keyword", "keyword"
                )
                metadata_dict["comments"] = cls._get_text(
                    root, ".//dc:description", "description"
                )

                # 날짜 정보
                created = cls._get_text(root, ".//dcterms:created", "created")
                if created:
                    metadata_dict["created_date"] = cls._parse_date(created)

                modified = cls._get_text(root, ".//dcterms:modified", "modified")
                if modified:
                    metadata_dict["modified_date"] = cls._parse_date(modified)

                # 문서 통계
                page_count = cls._get_text(root, ".//meta:pageCount", "pageCount")
                if page_count:
                    metadata_dict["page_count"] = int(page_count)

                word_count = cls._get_text(root, ".//meta:wordCount", "wordCount")
                if word_count:
                    metadata_dict["word_count"] = int(word_count)

                char_count = cls._get_text(root, ".//meta:charCount", "charCount")
                if char_count:
                    metadata_dict["char_count"] = int(char_count)

                paragraph_count = cls._get_text(
                    root, ".//meta:paragraphCount", "paragraphCount"
                )
                if paragraph_count:
                    metadata_dict["paragraph_count"] = int(paragraph_count)

                # 애플리케이션 정보
                metadata_dict["application"] = cls._get_text(
                    root, ".//meta:generator", "generator"
                )

                # 보안 정보
                security = cls._get_text(root, ".//meta:security", "security")
                if security:
                    metadata_dict["is_readonly"] = "read-only" in security.lower()

        except Exception:
            # metadata.xml 파싱 실패 시 무시
            pass

    @classmethod
    def _parse_header_xml(cls, zf: zipfile.ZipFile, metadata_dict: dict) -> None:
        """header.xml 파싱 (문서 구조 및 글꼴 정보)"""
        try:
            with zf.open("Contents/header.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()

                # 글꼴 정보 추출
                fonts = set()
                for font_elem in root.findall(".//hwpml:fontFace", cls.NAMESPACES):
                    font_name = font_elem.get("name")
                    if font_name:
                        fonts.add(font_name)

                if fonts:
                    metadata_dict["fonts"] = sorted(list(fonts))

                # HWP 버전 정보
                version = root.get("version")
                if version:
                    metadata_dict["hwp_version"] = version

        except Exception:
            # header.xml 파싱 실패 시 무시
            pass

    @classmethod
    def _get_text(cls, root: ET.Element, xpath: str, attr_name: str) -> Optional[str]:
        """XML에서 텍스트 추출 (네임스페이스 고려)"""
        # 먼저 네임스페이스로 시도
        elem = root.find(xpath, cls.NAMESPACES)
        if elem is not None and elem.text:
            return elem.text.strip()

        # 네임스페이스 없이 시도
        for elem in root.iter():
            if elem.tag.endswith(attr_name):
                if elem.text:
                    return elem.text.strip()

        return None

    @classmethod
    def _parse_date(cls, date_str: str) -> Optional[datetime]:
        """날짜 문자열을 datetime 객체로 변환"""
        # ISO 8601 형식 지원
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None
