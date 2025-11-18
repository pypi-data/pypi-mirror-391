# Alprina CLI - Publishing Guide

**Version**: 0.3.0  
**Date**: 2025-11-11

---

## 🎯 Quick Publish Commands

### **Publish to NPM** (Bun wrapper)

```bash
# 1. Navigate to bun directory
cd cli/bun

# 2. Login to npm (use your token)
npm login

# 3. Publish to npm
npm publish --access public

# 4. Verify
npm info @alprina/cli
```

### **Publish to PyPI** (Python package)

```bash
# 1. Navigate to cli directory
cd cli

# 2. Build the package
python -m build

# 3. Upload to PyPI
python -m twine upload dist/*

# 4. Verify
pip show alprina-cli
```

---

## 🔐 Authentication

### **NPM Token** (Stored securely)

```bash
# Set token as environment variable
export NPM_TOKEN="your_npm_token_here"

# Or add to .npmrc
echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > ~/.npmrc
```

### **PyPI Token**

```bash
# Use API token (not password)
# Create at: https://pypi.org/manage/account/token/

python -m twine upload dist/* --username __token__ --password pypi-your-token-here
```

---

## 📦 Version Bump Checklist

Before publishing, update versions in:

- [ ] `cli/pyproject.toml` → `version = "0.3.0"`
- [ ] `cli/bun/package.json` → `"version": "0.3.0"`
- [ ] `cli/src/alprina_cli/__init__.py` → `__version__ = "0.3.0"` (if exists)

---

## ✅ Pre-Publish Checklist

### **1. Run Tests**
```bash
cd cli
pytest tests/
```

### **2. Lint Code**
```bash
black src/
isort src/
flake8 src/
```

### **3. Build Locally**
```bash
python -m build
```

### **4. Test Installation**
```bash
# Test Python package
pip install dist/alprina_cli-0.3.0-py3-none-any.whl

# Test CLI
alprina --version
alprina chat

# Uninstall
pip uninstall alprina-cli
```

### **5. Check README**
Make sure `cli/README.md` is up to date with:
- Installation instructions
- New features (0.3.0)
- Usage examples

---

## 🚀 Publishing Steps (Detailed)

### **Step 1: NPM Package** (@alprina/cli)

```bash
# Clean build
cd cli/bun
rm -rf node_modules package-lock.json

# Login (if not already)
npm login

# Dry run (test without publishing)
npm publish --dry-run

# Publish for real
npm publish --access public

# Verify
npm view @alprina/cli
npm info @alprina/cli versions
```

**Expected Output**:
```
+ @alprina/cli@0.3.0
```

### **Step 2: Python Package** (alprina-cli)

```bash
# Clean previous builds
cd cli
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Check the build
twine check dist/*

# Upload to TestPyPI first (optional)
python -m twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ alprina-cli

# If all good, upload to real PyPI
python -m twine upload dist/*

# Verify
pip search alprina-cli
pip show alprina-cli
```

**Expected Output**:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading alprina_cli-0.3.0-py3-none-any.whl
Uploading alprina-cli-0.3.0.tar.gz
```

---

## 🔍 Post-Publish Verification

### **1. Install from npm**
```bash
npm install -g @alprina/cli
alprina --version  # Should show 0.3.0
```

### **2. Install from pip**
```bash
pip install alprina-cli
alprina --version  # Should show 0.3.0
```

### **3. Test New Features**
```bash
alprina chat

# Should see:
# 🛡️  Hey! I'm Alprina, your security expert!
# 💬 Chat with me naturally, like:
#   • "Scan my Python app for vulnerabilities"
```

### **4. Check Package Pages**
- NPM: https://www.npmjs.com/package/@alprina/cli
- PyPI: https://pypi.org/project/alprina-cli/

---

## 🎉 Release Announcement

After publishing, announce on:

### **GitHub Release**
```markdown
## Alprina CLI v0.3.0 - Conversational AI Update! 🎉

### ✨ What's New

**🤖 Enhanced Conversational AI**
- Chat naturally with Alprina like you would with ChatGPT
- "Scan my code", "Explain SQL injection", "Fix finding #3"
- Friendly, helpful personality - like talking to a senior security engineer

**💭 Better Thinking Indicators**
- See which agents are working in real-time
- Transparent agent selection process
- Multi-step progress indicators with emojis

**🛡️ Agent Transparency**
- Know which security agents are analyzing your code
- Understand why specific agents were selected
- Clear task type display (scan, explain, remediation)

### 📦 Installation

```bash
npm install -g @alprina/cli
# or
pip install alprina-cli
```

### 🚀 Try It Now

```bash
alprina chat
```

Then ask naturally:
- "Scan my Python app for vulnerabilities"
- "What's SQL injection and how do I fix it?"
- "Find secrets in my code"

Full changelog: [CHANGELOG.md](./CHANGELOG.md)
```

### **Twitter/X**
```
🎉 Alprina CLI v0.3.0 is live!

✨ New: Conversational AI - chat naturally like ChatGPT
💭 New: Transparent thinking - see which agents are working
🤖 New: Friendly personality - like talking to a security expert

Try it: npm install -g @alprina/cli

#cybersecurity #ai #devsecops
```

### **Product Hunt** (Optional)
Submit as "Alprina CLI v0.3.0 - Conversational Security Expert"

---

## 🐛 Rollback (If Needed)

### **Unpublish from npm** (within 72 hours)
```bash
npm unpublish @alprina/cli@0.3.0
```

### **Yank from PyPI** (marks as unavailable)
```bash
# Cannot delete, but can yank
twine upload --repository pypi --skip-existing dist/*

# Or via web UI:
# https://pypi.org/manage/project/alprina-cli/releases/
# Click "Yank" button
```

---

## 📋 Changelog Entry

Add to `CHANGELOG.md`:

```markdown
## [0.3.0] - 2025-11-11

### Added
- Enhanced conversational AI with natural language understanding
- Better thinking indicators showing agent selection process
- Agent transparency - see which agents are working
- Friendly, helpful personality in chat responses
- Multi-step progress indicators with emojis

### Changed
- Welcome message now emphasizes natural language chat
- System prompt enhanced with personality and communication style
- Progress indicators now stay visible (non-transient)
- Version bumped to 0.3.0

### Improved
- Chat experience now feels like talking to a senior security engineer
- More transparent about which agents are selected and why
- Better user feedback during security analysis
```

---

## 🎯 Version Strategy

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **0.3.0**: Major UX improvement (conversational AI)
- **0.2.2**: Previous version (basic chat)
- **Next**: 
  - 0.3.1 - Bug fixes
  - 0.4.0 - New features
  - 1.0.0 - Production ready

---

## 📞 Support

**Issues**: https://github.com/0xShortx/Alprina/issues  
**Docs**: https://docs.alprina.ai  
**Email**: support@alprina.com

---

**Status**: ✅ Ready to Publish!  
**Version**: 0.3.0  
**Date**: 2025-11-11
