# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-13

### Added
- Initial release of Velora
- Real-time text chat over TCP sockets
- File sharing up to 1GB per file  
- Multiple connection modes (local, IP-based, global via ngrok)
- Zero external dependencies - pure Python standard library
- Command line interface with subcommands
- Quick share mode for one-command file sharing
- Automatic file download to Downloads folder
- Duplicate filename handling
- Length-prefixed message protocol for reliability
- Support for both text and binary file transfers
- Interactive and programmatic API modes

### Features
- `velora chat` - Start interactive chat client
- `velora share` - Quick file sharing
- `velora server` - Start chat server
- `velora-chat`, `velora-share`, `velora-server` - Alternative commands
- Library usage with `velora.VeloraClient`, `velora.VeloraServer`, `velora.quick_share`

### Technical Details
- Base64 encoding for file transfers
- JSON message protocol for file metadata
- Robust TCP socket handling with proper error recovery
- Multi-threaded server supporting multiple clients
- Graceful connection handling and cleanup