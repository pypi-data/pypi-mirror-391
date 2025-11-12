# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-11-12

### Added
- **HostsManager 工具类** - 跨平台 hosts 文件管理工具
  - 支持添加/更新/删除 hosts 映射
  - 支持备份和恢复 hosts 文件
  - 支持列出和批量清除自定义条目
  - 自动权限检查和跨平台路径处理
  - 支持 Windows、Linux 和 macOS
- 完整的 HostsManager 使用文档 (`docs/HostsManager_Guide.md`)
- HostsManager 单元测试

### Fixed
- **Python 3.8/3.9 兼容性问题** - 添加 `from __future__ import annotations`
  - 修复 `client.py` 中 `str | None` 类型注解导致的 TypeError
  - 修复 `hosts.py` 中 `list[str]`、`dict[str, str]` 类型注解兼容性
  - 确保项目在 Python 3.8+ 所有版本中正常工作

## [0.1.2] - 2025-11-06

### Added
- 全局配置系统，支持通过环境变量配置（前缀 `HONGTA_`）
- `HSStockData` 数据模型，包含完整的沪深现货行情字段
- `Quote` 数据模型占位符
- HTTP 客户端模块 (`HistoricalClient`)
  - 支持获取股票历史数据
  - 内置重试机制（最多3次）
  - 支持 OAuth 2.0 认证
- 配置模块导出 `settings` 全局实例

### Changed
- `HistoricalClient` 使用全局配置实例替代硬编码参数
- `connect` 方法支持可选参数，默认使用配置中的用户名和密码
- 优化导入结构，统一从 `config` 和 `models` 包导出

### Fixed
- 修复 `models` 模块缺少 `__init__.py` 导致无法导入的问题
- 修正测试用例字段名称与实际模型不匹配的问题

## [0.1.0] - 2025-11-06

### Added
- 初始版本发布
- 基础项目结构
- HongTaData 模块框架
- 基本的 HTTP 客户端实现
- 项目依赖配置（httpx, pydantic, confluent-kafka 等）
- 开发工具配置（pytest, ruff, mypy）

[Unreleased]: https://github.com/mdhh1988/HongTaQuant/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/mdhh1988/HongTaQuant/compare/v0.1.0...v0.1.2
[0.1.0]: https://github.com/mdhh1988/HongTaQuant/releases/tag/v0.1.0
