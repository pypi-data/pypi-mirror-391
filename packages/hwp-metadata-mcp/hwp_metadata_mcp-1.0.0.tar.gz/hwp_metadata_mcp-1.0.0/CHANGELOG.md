# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-12

### Added
- Initial release of HWP Metadata MCP Server
- Support for HWP 5.0 (OLE-based binary format)
- Support for HWPX (XML-based open format)
- Support for HML (HWPML format)
- Automatic file format detection
- Cross-platform support (Windows, Linux, macOS)
- MCP server implementation with 4 tools:
  - `extract_metadata` - Auto-detect and extract
  - `extract_hwp_metadata` - HWP 5.0 specific
  - `extract_hwpx_metadata` - HWPX specific
  - `extract_hml_metadata` - HML specific
- MCP resource support via `hwp://metadata/{filepath}` URI
- Comprehensive metadata extraction (31 fields):
  - Document info (title, author, keywords, subject, description)
  - Time info (created, modified, last printed dates)
  - Statistics (page count, word count, character count, etc.)
  - Security info (encrypted, read-only, password protected)
  - Technical info (HWP version, fonts used)
  - Application info (creator application and version)
- Pure Python implementation (no HWP installation required)
- Pydantic models for type safety and validation
- Basic test suite

### Dependencies
- mcp >= 1.0.0
- pydantic >= 2.0.0
- olefile >= 0.46

[1.0.0]: https://github.com/heonseung4-del/hwp-metadata-mcp/releases/tag/v1.0.0
