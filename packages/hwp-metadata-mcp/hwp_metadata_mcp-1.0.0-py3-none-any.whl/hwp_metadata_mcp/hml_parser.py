"""HML 파일 메타데이터 추출기"""

import os
from datetime import datetime
from typing import Optional
from xml.etree import ElementTree as ET

from .models import HwpMetadata


class HmlParser:
    """HML (HWPML - XML 기반 HWP) 파일 파서"""

    @classmethod
    def parse(cls, file_path: str) -> HwpMetadata:
        """HML 파일에서 메타데이터 추출

        Args:
            file_path: HML 파일 경로

        Returns:
            HwpMetadata 객체

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            ValueError: HML 형식이 아닐 때
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        file_size = os.path.getsize(file_path)

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # HWPML 파일인지 확인
            if root.tag != "HWPML":
                raise ValueError("유효한 HML 파일이 아닙니다")

            # 메타데이터 추출
            metadata_dict = {
                "file_path": file_path,
                "file_type": "HML",
                "file_size": file_size,
            }

            # HWPML 버전 정보
            version = root.get("Version")
            sub_version = root.get("SubVersion")
            if version:
                metadata_dict["hwp_version"] = f"{version}"
                if sub_version:
                    metadata_dict["hwp_version"] += f" ({sub_version})"

            # HEAD 섹션에서 메타데이터 추출
            head = root.find("HEAD")
            if head is not None:
                cls._parse_head_section(head, metadata_dict)

            return HwpMetadata(**metadata_dict)

        except ET.ParseError as e:
            raise ValueError(f"XML 파싱 실패: {e}")

    @classmethod
    def _parse_head_section(cls, head: ET.Element, metadata_dict: dict) -> None:
        """HEAD 섹션 파싱 (문서 정보 추출)"""

        # DOCSUMMARY 섹션에서 문서 정보 추출
        doc_summary = head.find("DOCSUMMARY")
        if doc_summary is not None:
            # 제목
            title_elem = doc_summary.find("TITLE")
            if title_elem is not None and title_elem.text:
                metadata_dict["title"] = title_elem.text.strip()

            # 작성자
            author_elem = doc_summary.find("AUTHOR")
            if author_elem is not None and author_elem.text:
                metadata_dict["author"] = author_elem.text.strip()

            # 주제
            subject_elem = doc_summary.find("SUBJECT")
            if subject_elem is not None and subject_elem.text:
                metadata_dict["subject"] = subject_elem.text.strip()

            # 키워드
            keywords_elem = doc_summary.find("KEYWORDS")
            if keywords_elem is not None and keywords_elem.text:
                metadata_dict["keywords"] = keywords_elem.text.strip()

            # 설명
            comments_elem = doc_summary.find("COMMENTS")
            if comments_elem is not None and comments_elem.text:
                metadata_dict["comments"] = comments_elem.text.strip()

            # 날짜 (HWPML에서는 "2024년 07월 01일" 형식)
            date_elem = doc_summary.find("DATE")
            if date_elem is not None and date_elem.text:
                date_text = date_elem.text.strip()
                metadata_dict["created_date"] = cls._parse_korean_date(date_text)

            # 페이지 수
            pagecount_elem = doc_summary.find("PAGECOUNT")
            if pagecount_elem is not None and pagecount_elem.text:
                try:
                    metadata_dict["page_count"] = int(pagecount_elem.text)
                except ValueError:
                    pass

            # 단어 수
            wordcount_elem = doc_summary.find("WORDCOUNT")
            if wordcount_elem is not None and wordcount_elem.text:
                try:
                    metadata_dict["word_count"] = int(wordcount_elem.text)
                except ValueError:
                    pass

            # 문자 수
            charcount_elem = doc_summary.find("CHARCOUNT")
            if charcount_elem is not None and charcount_elem.text:
                try:
                    metadata_dict["char_count"] = int(charcount_elem.text)
                except ValueError:
                    pass

            # 문단 수
            paracount_elem = doc_summary.find("PARACOUNT")
            if paracount_elem is not None and paracount_elem.text:
                try:
                    metadata_dict["paragraph_count"] = int(paracount_elem.text)
                except ValueError:
                    pass

        # DOCINFO 섹션에서 추가 정보 추출
        doc_info = head.find("DOCINFO")
        if doc_info is not None:
            # 글꼴 정보 추출
            fonts = set()
            for face_name in doc_info.findall(".//FACENAMELIST/FONTFACE"):
                lang_attr = face_name.get("Lang")
                face_attr = face_name.get("Face")
                if face_attr:
                    fonts.add(face_attr)

            if fonts:
                metadata_dict["fonts"] = sorted(list(fonts))

            # 문서 보안 설정
            doc_opts = doc_info.find("DOCOPTION")
            if doc_opts is not None:
                # 암호화 여부는 파일 헤더에서 확인해야 하므로 HML에서는 확인 불가
                # 대신 보호 설정 확인
                protect = doc_opts.get("Protect")
                if protect:
                    metadata_dict["is_readonly"] = protect != "0"

    @classmethod
    def _parse_korean_date(cls, date_str: str) -> Optional[datetime]:
        """한글 날짜 문자열을 datetime 객체로 변환

        예: "2024년 07월 01일" -> datetime(2024, 7, 1)
        """
        try:
            # "2024년 07월 01일" 형식 파싱
            import re

            match = re.match(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day))

            # ISO 형식도 시도
            return datetime.fromisoformat(date_str)

        except (ValueError, AttributeError):
            return None
