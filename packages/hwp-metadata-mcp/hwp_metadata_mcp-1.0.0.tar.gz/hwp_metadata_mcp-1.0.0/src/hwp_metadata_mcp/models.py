"""Pydantic models for HWP metadata"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HwpMetadata(BaseModel):
    """HWP/HWPX 파일 메타데이터 모델"""

    # 파일 기본 정보
    file_path: str = Field(..., description="파일 경로")
    file_type: str = Field(..., description="파일 타입 (HWP 또는 HWPX)")
    file_size: int = Field(..., description="파일 크기 (bytes)")

    # 문서 정보
    title: Optional[str] = Field(None, description="문서 제목")
    author: Optional[str] = Field(None, description="작성자")
    keywords: Optional[str] = Field(None, description="키워드")
    subject: Optional[str] = Field(None, description="주제")
    comments: Optional[str] = Field(None, description="설명/코멘트")

    # 시간 정보
    created_date: Optional[datetime] = Field(None, description="생성 날짜")
    modified_date: Optional[datetime] = Field(None, description="수정 날짜")
    last_printed_date: Optional[datetime] = Field(None, description="마지막 인쇄 날짜")

    # 문서 통계
    page_count: Optional[int] = Field(None, description="페이지 수")
    word_count: Optional[int] = Field(None, description="단어 수")
    char_count: Optional[int] = Field(None, description="문자 수")
    char_count_with_spaces: Optional[int] = Field(None, description="공백 포함 문자 수")
    paragraph_count: Optional[int] = Field(None, description="문단 수")
    line_count: Optional[int] = Field(None, description="줄 수")

    # 보안 정보
    is_encrypted: bool = Field(False, description="암호화 여부")
    is_readonly: Optional[bool] = Field(None, description="읽기 전용 여부")
    has_password: Optional[bool] = Field(None, description="비밀번호 보호 여부")

    # 기술 정보
    hwp_version: Optional[str] = Field(None, description="HWP 버전")
    fonts: Optional[list[str]] = Field(None, description="사용된 글꼴 목록")

    # 애플리케이션 정보
    application: Optional[str] = Field(None, description="생성 애플리케이션")
    app_version: Optional[str] = Field(None, description="애플리케이션 버전")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/document.hwp",
                "file_type": "HWP",
                "file_size": 51200,
                "title": "시험 문제지",
                "author": "홍길동",
                "keywords": "수학, 고등학교",
                "subject": "수학 시험",
                "created_date": "2024-01-15T09:00:00",
                "modified_date": "2024-01-16T10:30:00",
                "page_count": 5,
                "word_count": 1200,
                "char_count": 3500,
                "is_encrypted": False,
                "hwp_version": "5.0.0.7",
                "fonts": ["맑은 고딕", "바탕"],
                "application": "Hancom Office",
            }
        }
