# Changelog

All notable changes to Bug-Be-Gone will be documented in this file.

## [1.0.1] - 2025-11-11

### Updated
- Contact email updated to Keeghan@dishesandmore.com

## [1.0.0] - 2025-11-11

### Trial Release
- Initial trial release on PyPI
- 52 error types supported with intelligent fixing
- AST-based code analysis
- Mypy integration for type checking
- Deployment validation
- Error prediction capabilities
- Automatic backup creation
- 7-day evaluation period

### Features
- Runtime error detection and fixing
- Type error detection and fixing
- Deployment issue validation
- Multi-pass iteration for complex error chains
- Smart ValueError fixing with context understanding
- Smart TypeError fixing with comprehensive type conversion
- Smart AttributeError fixing with suggestions
- UnboundLocalError automatic fixing
- Pattern-based error detection
- Context-aware solutions

### Supported Error Types (52+)
- TypeError, ValueError, AttributeError
- KeyError, IndexError, ZeroDivisionError
- FileNotFoundError, PermissionError, IsADirectoryError
- JSONDecodeError, UnicodeDecodeError, UnicodeEncodeError
- ImportError, ModuleNotFoundError
- NameError, UnboundLocalError
- StopIteration, RecursionError
- MemoryError, OverflowError
- AssertionError, RuntimeError
- NotImplementedError, EOFError
- TimeoutError, ConnectionError
- And 30+ more...

### Command Line Interface
- `bug-be-gone script.py` - Fix runtime errors
- `bug-be-gone --types script.py` - Fix type errors
- `bug-be-gone --deploy` - Validate deployment
- `bug-be-gone --all script.py` - Fix everything
- `bug-be-gone --ultimate script.py` - Maximum power mode
- `bbg` - Short alias for bug-be-gone

### Trial License
- Expires: November 17, 2025
- All features fully functional
- No code sent to external servers
- No telemetry or tracking

### Technical Details
- Pure Python implementation
- No external dependencies
- AST-based code parsing
- Deterministic pattern matching
- Cross-platform support (Linux, macOS, Windows)

### Known Limitations
- Only fixes errors in target script (not library code)
- Maximum 100 iterations per run
- Type checking requires mypy (optional dependency)

---

## Future Releases

### [1.1.0] - Planned
- Extended error database
- Performance optimizations
- Enhanced type inference
- Additional deployment checks
- Improved error prediction
- Configuration file support

### [2.0.0] - Planned
- API for CI/CD integration
- Plugin system for custom error patterns
- Multi-file project support
- Git integration
- Team collaboration features

---

For commercial licenses and updates beyond trial:
Email: keeg@dishesandmore.com
