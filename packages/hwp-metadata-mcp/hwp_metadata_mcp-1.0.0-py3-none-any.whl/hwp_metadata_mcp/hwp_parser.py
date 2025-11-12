"""HWP 5.0 파일 메타데이터 추출기"""

import os
import struct
from datetime import datetime
from typing import Optional

import olefile

from .models import HwpMetadata


class HwpParser:
    """HWP 5.0 (OLE 기반) 파일 파서"""

    @classmethod
    def parse(cls, file_path: str) -> HwpMetadata:
        """HWP 5.0 파일에서 메타데이터 추출

        Args:
            file_path: HWP 파일 경로

        Returns:
            HwpMetadata 객체

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            ValueError: 유효하지 않은 HWP 파일일 때
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        file_size = os.path.getsize(file_path)

        try:
            ole = olefile.OleFileIO(file_path)
        except Exception:
            raise ValueError(f"유효한 HWP 파일이 아닙니다: {file_path}")

        metadata_dict = {
            "file_path": file_path,
            "file_type": "HWP",
            "file_size": file_size,
        }

        try:
            # HwpSummaryInformation 파싱
            if ole.exists("\x05HwpSummaryInformation"):
                cls._parse_summary_information(ole, metadata_dict)

            # FileHeader 파싱
            if ole.exists("FileHeader"):
                cls._parse_file_header(ole, metadata_dict)

            # DocInfo 파싱 (복잡하므로 기본 정보만)
            if ole.exists("DocInfo"):
                cls._parse_doc_info(ole, metadata_dict)

            return HwpMetadata(**metadata_dict)

        finally:
            ole.close()

    @classmethod
    def _parse_summary_information(
        cls, ole: olefile.OleFileIO, metadata_dict: dict
    ) -> None:
        """HwpSummaryInformation 스트림 파싱

        표준 Windows OLE Property Set 형식
        """
        try:
            # OLE Property Set으로 파싱
            meta = ole.get_metadata()

            # 기본 문서 정보
            if hasattr(meta, "title") and meta.title:
                metadata_dict["title"] = meta.title

            if hasattr(meta, "author") and meta.author:
                metadata_dict["author"] = meta.author

            if hasattr(meta, "subject") and meta.subject:
                metadata_dict["subject"] = meta.subject

            if hasattr(meta, "keywords") and meta.keywords:
                metadata_dict["keywords"] = meta.keywords

            if hasattr(meta, "comments") and meta.comments:
                metadata_dict["comments"] = meta.comments

            # 날짜 정보
            if hasattr(meta, "create_time") and meta.create_time:
                metadata_dict["created_date"] = meta.create_time

            if hasattr(meta, "last_saved_time") and meta.last_saved_time:
                metadata_dict["modified_date"] = meta.last_saved_time

            if hasattr(meta, "last_printed") and meta.last_printed:
                metadata_dict["last_printed_date"] = meta.last_printed

            # 문서 통계
            if hasattr(meta, "num_pages") and meta.num_pages:
                metadata_dict["page_count"] = meta.num_pages

            if hasattr(meta, "num_words") and meta.num_words:
                metadata_dict["word_count"] = meta.num_words

            if hasattr(meta, "num_chars") and meta.num_chars:
                metadata_dict["char_count"] = meta.num_chars

            if hasattr(meta, "num_chars_with_spaces") and meta.num_chars_with_spaces:
                metadata_dict["char_count_with_spaces"] = meta.num_chars_with_spaces

            # 애플리케이션 정보
            if hasattr(meta, "creating_application") and meta.creating_application:
                metadata_dict["application"] = meta.creating_application

            # 보안 정보
            if hasattr(meta, "security") and meta.security:
                metadata_dict["has_password"] = meta.security > 0

        except Exception:
            # OLE metadata 파싱 실패 시 수동 파싱 시도
            cls._parse_summary_manual(ole, metadata_dict)

    @classmethod
    def _parse_summary_manual(
        cls, ole: olefile.OleFileIO, metadata_dict: dict
    ) -> None:
        """HwpSummaryInformation 수동 파싱 (OLE metadata 실패 시)"""
        try:
            stream = ole.openstream("\x05HwpSummaryInformation")
            data = stream.read()

            # 간단한 파싱 - 주요 속성만 추출
            # OLE Property Set 포맷은 복잡하므로 기본 정보만
            # (실제 구현에서는 python-olefile의 PropertySet 사용)

        except Exception:
            pass

    @classmethod
    def _parse_file_header(cls, ole: olefile.OleFileIO, metadata_dict: dict) -> None:
        """FileHeader 스트림 파싱

        HWP 파일 포맷 버전 및 암호화 정보
        """
        try:
            stream = ole.openstream("FileHeader")
            data = stream.read(256)  # FileHeader는 256바이트

            if len(data) < 256:
                return

            # 파일 시그니처 확인 (처음 32바이트: "HWP Document File")
            signature = data[:32]
            if not signature.startswith(b"HWP Document File"):
                return

            # 버전 정보 (오프셋 36-40)
            version = struct.unpack("<I", data[36:40])[0]
            major = (version >> 24) & 0xFF
            minor = (version >> 16) & 0xFF
            micro = (version >> 8) & 0xFF
            build = version & 0xFF

            metadata_dict["hwp_version"] = f"{major}.{minor}.{micro}.{build}"

            # 속성 플래그 (오프셋 40-44)
            flags = struct.unpack("<I", data[40:44])[0]

            # 암호화 여부 확인
            is_compressed = (flags & 0x01) != 0
            is_encrypted = (flags & 0x02) != 0
            is_distribution = (flags & 0x04) != 0

            metadata_dict["is_encrypted"] = is_encrypted

            # 파일이 배포용 문서인 경우 읽기 전용
            if is_distribution:
                metadata_dict["is_readonly"] = True

        except Exception:
            pass

    @classmethod
    def _parse_doc_info(cls, ole: olefile.OleFileIO, metadata_dict: dict) -> None:
        """DocInfo 스트림 파싱

        문서 구조 및 스타일 정보 (복잡하므로 기본 정보만)
        """
        try:
            stream = ole.openstream("DocInfo")
            # DocInfo는 zlib으로 압축되어 있고 레코드 구조로 되어 있음
            # 완전한 파싱은 복잡하므로 여기서는 생략
            # 실제 구현 시 pyhwp 라이브러리의 구조를 참고할 수 있음

            # 압축된 데이터 읽기
            import zlib

            compressed_data = stream.read()

            # zlib 압축 해제 시도
            try:
                decompressed = zlib.decompress(compressed_data, -15)
                # 레코드 파싱은 복잡하므로 생략
                # 향후 확장: 글꼴 목록, 스타일 정보 등 추출
            except Exception:
                pass

        except Exception:
            pass


def detect_file_type(file_path: str) -> str:
    """HWP 파일 타입 감지 (HWP vs HWPX vs HML)

    Args:
        file_path: 파일 경로

    Returns:
        "HWP", "HWPX", 또는 "HML"

    Raises:
        ValueError: 지원하지 않는 파일 형식
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    # 확장자로 먼저 확인
    _, ext = os.path.splitext(file_path.lower())

    if ext == ".hml":
        return "HML"
    elif ext == ".hwpx":
        return "HWPX"
    elif ext == ".hwp":
        return "HWP"

    # 파일 시그니처로 확인
    try:
        with open(file_path, "rb") as f:
            signature = f.read(100)  # 더 많이 읽어서 XML 확인

            # XML 파일 시그니처 (HML) - UTF-8 BOM 또는 <?xml
            if signature[:3] == b"\xef\xbb\xbf" or signature[:5] == b"<?xml":
                # HWPML 루트 태그 확인
                try:
                    with open(file_path, "r", encoding="utf-8") as txt_f:
                        content = txt_f.read(1000)
                        if "<HWPML" in content:
                            return "HML"
                except Exception:
                    pass

            # ZIP 파일 시그니처 (HWPX)
            if signature[:4] == b"PK\x03\x04":
                return "HWPX"

            # OLE 파일 시그니처 (HWP 5.0)
            if signature[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                return "HWP"

    except Exception:
        pass

    raise ValueError(f"지원하지 않는 파일 형식입니다: {file_path}")
