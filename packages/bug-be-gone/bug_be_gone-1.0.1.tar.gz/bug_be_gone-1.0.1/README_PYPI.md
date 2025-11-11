# Bug-Be-Gone

**Automatically detect and fix Python errors. Never debug again.**

Bug-Be-Gone iterates through your broken code, detects errors, applies fixes, and repeats until everything works. Point it at any Python script and watch it fix itself.

## Installation

```bash
pip install bug-be-gone
```

## Quick Start

```bash
# Fix all errors in your script
bug-be-gone your_script.py

# Fix everything (runtime + types + deployment)
bug-be-gone --ultimate your_script.py

# Check for type errors
bug-be-gone --types your_script.py

# Validate deployment configuration
bug-be-gone --deploy
```

## What It Fixes

✅ **Runtime Errors** (50+ types)
- TypeError, ValueError, AttributeError
- KeyError, IndexError, ZeroDivisionError  
- FileNotFoundError, PermissionError
- JSONDecodeError, UnicodeDecodeError
- ImportError, ModuleNotFoundError
- And 40+ more...

✅ **Type Errors**
- Integrates with mypy
- Infers and adds type hints
- Fixes type mismatches

✅ **Deployment Issues**
- Missing environment variables
- Port configuration problems
- Permission errors
- Path issues

## Example Session

```bash
$ bug-be-gone --ultimate broken_app.py

[BACKUP] Created at broken_app.py.backup
[START] Universal Debugger ULTIMATE
[TRIAL] Evaluation license - expires Nov 17, 2025
[MODE] ULTIMATE
[TARGET] /home/user/broken_app.py
[DATABASE] 52 error types loaded

[TYPES] Running type checker...
[FOUND] 3 type error(s)
[FIX] Applied type fixes...

[RUNTIME] Fixing runtime errors...
[ITERATION 1] Running script...
[DETECTED] AttributeError at line 156
[FIX] Applied AttributeError fix at line 156
[ITERATION 2] Running script...
[DETECTED] KeyError at line 203
[FIX] Applied KeyError fix at line 203
[ITERATION 3] Running script...
[SUCCESS] No errors detected!

[COMPLETE] Fixed 5 error(s) in 2 iteration(s)
```

## How It Works

1. **Backup**: Automatically creates `.backup` file before any changes
2. **Detect**: Runs your code and captures error output
3. **Analyze**: Uses AST parsing to understand code context
4. **Fix**: Applies intelligent, context-aware fixes
5. **Repeat**: Iterates until all errors are resolved

## Key Features

🔒 **Safe**: Always creates backups before modifying code  
⚡ **Fast**: Deterministic pattern matching, not LLM-based  
🎯 **Smart**: AST-based analysis for context-aware fixes  
🔧 **Comprehensive**: 52 error types with multiple fix patterns each  
🏠 **Local**: Runs 100% on your machine, no code sent anywhere  

## Trial License

This is a **trial version** that expires on **November 17, 2025**.

All features are fully functional during the trial period.

## Purchasing

To purchase a full license:

**Email**: Keeghan@dishesandmore.com  
**Subject**: Bug-Be-Gone License

Available licenses:
- **Individual Developer**: $147/year or $499 lifetime
- **Team License (5 devs)**: $497/year  
- **Enterprise**: Custom pricing

## Commands

```bash
# Basic usage
bug-be-gone script.py              # Fix runtime errors
bug-be-gone --types script.py      # Fix type errors
bug-be-gone --deploy               # Check deployment
bug-be-gone --all script.py        # Fix everything
bug-be-gone --ultimate script.py   # MAXIMUM POWER

# Short alias
bbg --ultimate script.py
```

## Requirements

- Python 3.6+
- No external dependencies
- Works on Linux, macOS, Windows

## Technical Details

Bug-Be-Gone uses:
- **AST parsing** for intelligent code analysis
- **Pattern matching** for deterministic fixes
- **Type inference** for adding missing type hints
- **Mypy integration** for type checking
- **Multi-pass iteration** for complex error chains

Not LLM-based - this is fast, deterministic, and predictable.

## Safety

- ✅ Creates `.backup` files automatically
- ✅ Runs locally, no external API calls
- ✅ No telemetry or tracking
- ✅ You control when changes are applied

## Limitations

- Only fixes errors in target script (not library code)
- Maximum 100 iterations per run
- Type checking requires mypy (optional)
- Trial version expires Nov 17, 2025

## Support

**Trial Support**: Keeghan@dishesandmore.com  
**Response Time**: 48 hours  

## License

Proprietary - Trial License  
Copyright © 2025 Dishes & More Ventures

Unauthorized distribution, decompilation, or reverse engineering is prohibited.

---

**Questions?** Keeghan@dishesandmore.com

**Made with frustration** after debugging too many estate sale inventory tools.
