"""HWP Metadata MCP Server

MCP 서버 메인 로직 - FastMCP 사용
"""

import asyncio
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from fastmcp.exceptions import ToolError

from .hwp_parser import HwpParser, detect_file_type
from .hwpx_parser import HwpxParser
from .hml_parser import HmlParser
from .models import HwpMetadata


# MCP 서버 인스턴스 생성
mcp = FastMCP("hwp-metadata")


@mcp.tool()
def extract_hwp_metadata(
    file_path: Annotated[str, "HWP 파일 경로"]
) -> HwpMetadata:
    """HWP 5.0 파일의 메타데이터를 추출합니다.

    Args:
        file_path: HWP 파일의 절대 경로 또는 상대 경로

    Returns:
        HwpMetadata: 추출된 메타데이터

    Raises:
        ToolError: 파일을 찾을 수 없거나 유효하지 않은 HWP 파일일 때
    """
    try:
        metadata = HwpParser.parse(file_path)
        return metadata
    except FileNotFoundError as e:
        raise ToolError(f"파일을 찾을 수 없습니다: {file_path}")
    except ValueError as e:
        raise ToolError(f"유효하지 않은 HWP 파일입니다: {str(e)}")
    except Exception as e:
        raise ToolError(f"메타데이터 추출 중 오류 발생: {str(e)}")


@mcp.tool()
def extract_hwpx_metadata(
    file_path: Annotated[str, "HWPX 파일 경로"]
) -> HwpMetadata:
    """HWPX 파일의 메타데이터를 추출합니다.

    Args:
        file_path: HWPX 파일의 절대 경로 또는 상대 경로

    Returns:
        HwpMetadata: 추출된 메타데이터

    Raises:
        ToolError: 파일을 찾을 수 없거나 유효하지 않은 HWPX 파일일 때
    """
    try:
        metadata = HwpxParser.parse(file_path)
        return metadata
    except FileNotFoundError as e:
        raise ToolError(f"파일을 찾을 수 없습니다: {file_path}")
    except ValueError as e:
        raise ToolError(f"유효하지 않은 HWPX 파일입니다: {str(e)}")
    except Exception as e:
        raise ToolError(f"메타데이터 추출 중 오류 발생: {str(e)}")


@mcp.tool()
def extract_hml_metadata(
    file_path: Annotated[str, "HML 파일 경로"]
) -> HwpMetadata:
    """HML 파일의 메타데이터를 추출합니다.

    Args:
        file_path: HML 파일의 절대 경로 또는 상대 경로

    Returns:
        HwpMetadata: 추출된 메타데이터

    Raises:
        ToolError: 파일을 찾을 수 없거나 유효하지 않은 HML 파일일 때
    """
    try:
        metadata = HmlParser.parse(file_path)
        return metadata
    except FileNotFoundError as e:
        raise ToolError(f"파일을 찾을 수 없습니다: {file_path}")
    except ValueError as e:
        raise ToolError(f"유효하지 않은 HML 파일입니다: {str(e)}")
    except Exception as e:
        raise ToolError(f"메타데이터 추출 중 오류 발생: {str(e)}")


@mcp.tool()
def extract_metadata(
    file_path: Annotated[str, "HWP, HWPX 또는 HML 파일 경로"]
) -> HwpMetadata:
    """HWP, HWPX 또는 HML 파일의 메타데이터를 자동으로 감지하여 추출합니다.

    파일 형식을 자동으로 감지하고 적절한 파서를 사용하여 메타데이터를 추출합니다.

    Args:
        file_path: HWP, HWPX 또는 HML 파일의 절대 경로 또는 상대 경로

    Returns:
        HwpMetadata: 추출된 메타데이터

    Raises:
        ToolError: 파일을 찾을 수 없거나 지원하지 않는 파일 형식일 때
    """
    try:
        # 파일 타입 감지
        file_type = detect_file_type(file_path)

        # 적절한 파서 사용
        if file_type == "HWP":
            metadata = HwpParser.parse(file_path)
        elif file_type == "HWPX":
            metadata = HwpxParser.parse(file_path)
        elif file_type == "HML":
            metadata = HmlParser.parse(file_path)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file_type}")

        return metadata

    except FileNotFoundError:
        raise ToolError(f"파일을 찾을 수 없습니다: {file_path}")
    except ValueError as e:
        raise ToolError(str(e))
    except Exception as e:
        raise ToolError(f"메타데이터 추출 중 오류 발생: {str(e)}")


@mcp.resource("hwp://metadata/{filepath}")
def get_metadata_resource(filepath: str) -> str:
    """URI를 통해 HWP/HWPX 파일의 메타데이터를 조회합니다.

    Args:
        filepath: HWP 또는 HWPX 파일 경로

    Returns:
        메타데이터 JSON 문자열
    """
    try:
        metadata = extract_metadata(filepath)
        return metadata.model_dump_json(indent=2, exclude_none=True)
    except Exception as e:
        return f"오류: {str(e)}"


def main():
    """MCP 서버 실행 진입점"""
    # stdio transport로 실행
    asyncio.run(mcp.run())


if __name__ == "__main__":
    main()
