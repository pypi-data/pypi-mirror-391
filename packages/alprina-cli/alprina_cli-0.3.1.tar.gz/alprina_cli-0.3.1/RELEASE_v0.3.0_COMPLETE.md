# Alprina CLI v0.3.0 - Release Complete! 🎉

**Release Date**: 2025-11-11  
**Status**: ✅ Published to npm, Python package ready

---

## 🎯 What's in v0.3.0

### **Enhanced Conversational AI** 🤖
- Chat naturally like you would with ChatGPT/Claude
- Friendly, helpful personality - like talking to a senior security engineer
- "Scan my code", "Explain SQL injection", "Fix finding #3"

### **Better Thinking Indicators** 💭
- See which agents are working in real-time
- Transparent agent selection process
- Multi-step progress indicators with emojis
- Non-transient display (stays visible)

### **Agent Transparency** 🔍
- Know which security agents are analyzing your code
- Understand why specific agents were selected
- Clear task type display (scan, explain, remediation)

### **Friendly Personality** 🛡️
- Gets excited about finding (and fixing) vulnerabilities
- Explains complex security concepts simply
- Shares real-world examples
- Encourages good security practices
- Never judges - everyone's learning!

---

## 📦 Published Packages

### ✅ **NPM Package** - LIVE!
```bash
# Install
npm install -g @alprina/cli

# Verify
npm info @alprina/cli
```

**Package**: https://www.npmjs.com/package/@alprina/cli  
**Version**: 0.3.0  
**Published**: ✅ Successfully published!

---

### 🐍 **Python Package** - Ready to Publish

**Built successfully**:
- `alprina_cli-0.3.0.tar.gz` ✅
- `alprina_cli-0.3.0-py3-none-any.whl` ✅

**To publish to PyPI**:
```bash
cd cli
source .venv/bin/activate

# Upload to PyPI
python -m twine upload dist/*

# Or to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

**Note**: You'll need PyPI credentials. Get them at:
- https://pypi.org/manage/account/token/

---

## 🎨 Bonus: Dashboard Dark/Light Mode

Also shipped in this update:

### **Theme Switching** 🌓
- Light mode
- Dark mode
- System (auto-detect)

**Implementation**:
- ✅ next-themes integration
- ✅ shadcn components fully compatible
- ✅ Theme toggle in sidebar
- ✅ Smooth transitions
- ✅ Persists across sessions

**Try it**: Click theme toggle in dashboard sidebar!

---

## 🚀 User Experience

### **Before v0.2.2** ❌
```bash
> alprina chat

You: scan my code

Alprina: Processing...
[Silent working, no feedback]

Alprina: Found vulnerabilities.
```

### **After v0.3.0** ✅
```bash
> alprina chat

🛡️  Hey! I'm Alprina, your security expert!

💬 Chat with me naturally, like:
  • "Scan my Python app for vulnerabilities"
  • "What's SQL injection and how do I fix it?"

You: scan my code

💭 Analyzing your request...
✓ Request analyzed
🤖 Selected agents: CodeAgent
🎯 Task type: scan_request
⚡ Executing security analysis...
✓ Analysis complete!

Alprina: Hey! I scanned your code and found 3 security 
issues. Let me break them down for you:

1. 🔴 SQL Injection in user_login.py (HIGH)
   Uh oh, this is serious - an attacker could steal your 
   entire database! Want me to show you the fix?

2. 🟡 XSS in comment_handler.py (MEDIUM)
   Users could inject malicious scripts here. I can 
   provide the secure code!

3. 🔴 Hardcoded API key in config.py (HIGH)
   This is publicly visible - very risky! Let me help 
   you move this to environment variables.

Which one should we tackle first?
```

---

## 📊 Technical Details

### **Files Changed**:
- `cli/src/alprina_cli/chat.py` - Enhanced thinking, agent transparency
- `cli/pyproject.toml` - Version bump to 0.3.0
- `cli/bun/package.json` - Version bump to 0.3.0

### **New Features**:
1. Multi-step progress indicators
2. Agent selection transparency
3. Enhanced system prompt with personality
4. Better welcome message
5. Conversational communication style

### **Dashboard Bonus**:
- `website/components/theme-provider.tsx` - NEW
- `website/components/theme-toggle.tsx` - NEW
- `website/app/globals.css` - Light/dark mode variables
- `website/app/layout.tsx` - ThemeProvider integration

---

## 🎯 Installation

### **NPM** (Wrapper + Python CLI)
```bash
npm install -g @alprina/cli
alprina --version  # Should show 0.3.0
```

### **Python** (Once published to PyPI)
```bash
pip install alprina-cli
alprina --version  # Should show 0.3.0
```

### **Try It Now**
```bash
alprina chat

# Then ask naturally:
> Scan my Python app for vulnerabilities
> What's SQL injection?
> Find secrets in my code
```

---

## 📢 Announcement Template

### **GitHub Release**
```markdown
## Alprina CLI v0.3.0 - Conversational AI Update! 🎉

Chat naturally with Alprina like you would with ChatGPT!

### ✨ What's New
- 🤖 Enhanced conversational AI
- 💭 Better thinking indicators
- 🔍 Agent transparency
- 🛡️ Friendly, helpful personality

### 📦 Installation
npm install -g @alprina/cli

### 🚀 Try It
alprina chat

Then ask: "Scan my code", "Explain SQL injection", etc.
```

### **Twitter/X**
```
🎉 Alprina CLI v0.3.0 is live on npm!

✨ Chat naturally: "Scan my code"
💭 See agents working in real-time
🛡️ Friendly security expert personality

Try it: npm install -g @alprina/cli

#cybersecurity #ai #devsecops #nodejs
```

---

## ✅ Post-Release Checklist

### **Completed** ✅
- [x] Version bumped to 0.3.0 in all package files
- [x] Git commits with detailed changelog
- [x] Pushed to GitHub main branch
- [x] Published to npm registry
- [x] Python package built successfully
- [x] Dashboard theme toggle implemented
- [x] Documentation updated

### **Remaining** 📝
- [ ] Publish Python package to PyPI (need credentials)
- [ ] Create GitHub release with changelog
- [ ] Post announcement on Twitter/X
- [ ] Update docs.alprina.com with v0.3.0 features
- [ ] Write blog post about conversational AI features
- [ ] Record demo video showing new chat experience

---

## 🔗 Links

**NPM Package**: https://www.npmjs.com/package/@alprina/cli  
**GitHub Repo**: https://github.com/0xShortx/Alprina  
**Documentation**: https://docs.alprina.com  
**Dashboard**: https://dashboard.alprina.ai

---

## 🎓 Publishing Python Package to PyPI

When ready to publish:

```bash
cd cli
source .venv/bin/activate

# Check the build
twine check dist/*

# Upload to TestPyPI (optional, for testing)
python -m twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ alprina-cli

# If all good, upload to real PyPI
python -m twine upload dist/*

# Verify
pip install alprina-cli
alprina --version
```

**PyPI Token**: Create at https://pypi.org/manage/account/token/

---

## 🎉 Success Metrics

### **Before Release**:
- CLI version: 0.2.2
- Basic chat, no personality
- Silent progress indicators
- No agent transparency

### **After Release**:
- CLI version: 0.3.0 ✅
- Conversational AI with personality ✅
- Real-time thinking indicators ✅
- Full agent transparency ✅
- Published to npm ✅
- Dashboard theme toggle ✅

---

**Status**: 🎉 **v0.3.0 Successfully Released!**

**npm**: ✅ Published  
**PyPI**: 📦 Built, ready to publish  
**Dashboard**: 🌓 Theme toggle live

**You did it!** 🚀
