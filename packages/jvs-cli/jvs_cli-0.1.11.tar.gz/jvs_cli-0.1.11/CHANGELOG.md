# Changelog

## [0.1.7] - 2025-10-28

### Fixed
- Fixed conversation continuity for follow-up questions: conversation_id is now correctly sent in jarvis_options field according to API specification
- This ensures that when Jarvis asks follow-up questions (e.g., via ask_followup_question tool), the user's response is properly understood in context

### Changed
- Updated ChatCompletionRequest model to use jarvis_options field instead of top-level conversation_id
- Improved request logging to include jarvis_options for better debugging

## [0.1.4] - 2025-10-24

### Added
- Added `exit` and `quit` commands (without slash) to exit CLI
- Improved conversation_id extraction from both jarvis_metadata and jarvis_step.data

### Fixed
- Fixed conversation continuity: conversations now persist within the same REPL session
- Removed confusing "Starting conversation:" message
- Better visual feedback when continuing an existing conversation

### Changed
- Updated help text to include new exit commands
- Improved debug logging for conversation tracking

## [0.1.3] - 2025-10-24

### Changed
- Simplified config init to only 3 fields: URL, Login Code, Theme
- All display options now default to enabled
- Added `login_code` field (backward compatible with `user_id`)

## [0.1.1] - 2025-10-24

### Fixed
- Fixed AttributeError in `jvs-cli config show` command

## [0.1.0] - 2025-10-23

Initial release

### Features
- Interactive REPL mode
- Streaming responses
- AI thinking visualization
- Conversation history
- Configurable display options
- OpenAI-compatible API support
