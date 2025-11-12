# 🛡️ NoStage

**Protect files from accidental Git commits - even when you `git add .`**

NoStage is a lightweight CLI tool that prevents specific files from being staged and committed, perfect for temporary debug files, experimental code, and personal workflow files that you don't want in your repository.

## 🎯 Why NoStage?

Ever had this happen?

```bash
# You're debugging with some test files
$ ls
debug.js  test-output.txt  my-feature.js  ...

# You finish your work and commit everything
$ git add .
$ git commit -m "Add new feature"

# 😱 Oops! debug.js and test-output.txt are now committed!
```

**NoStage solves this.** Mark files as "protected" once, and they'll never be accidentally committed.

## 🆚 NoStage vs .gitignore

| Feature | .gitignore | NoStage |
|---------|-----------|---------|
| **Scope** | Team-wide, affects everyone | Personal, per-developer |
| **Already tracked files** | ❌ Can't ignore | ✅ Works on any file |
| **Use case** | Files that should NEVER be committed | Files you might commit LATER |
| **Setup** | Manual editing | Simple CLI commands |
| **Dynamic** | Static file | Easy add/remove on the fly |

**Perfect for:**
- 🐛 Debug/test files you create while developing
- 🧪 Experimental code you're not ready to commit
- 📝 Personal notes or scratch files
- 🔧 Local configuration tweaks

## 🚀 Installation

```bash
# Install via pip
pip install nostage

# Initialize in your git repository
cd your-project
nostage init
```

## 📖 Usage

### Protect Files

```bash
# Protect specific files
nostage add debug.js test-output.txt scratch.py

# Now commit normally - protected files are auto-unstaged!
git add .
git commit -m "my changes"
# ✅ debug.js, test-output.txt, scratch.py won't be committed
```

### Protect Patterns

```bash
# Protect all files matching a pattern
nostage pattern "*.temp.js"
nostage pattern "debug_*.py"
nostage pattern "scratch/*"
```

### Manage Protection

```bash
# List all protected files and patterns
nostage list

# Remove protection from a file
nostage remove debug.js

# Remove a pattern
nostage remove-pattern "*.temp.js"

# Check status
nostage status
```

## 🎬 How It Works

1. **You mark files for protection:**
   ```bash
   nostage add debug.js
   ```

2. **NoStage installs a git pre-commit hook** that runs automatically

3. **When you commit:**
   ```bash
   git add .
   git commit -m "update"
   ```

4. **Protected files are auto-unstaged:**
   ```
   🛡️  NoStage: Protecting 1 file(s) from commit:
      • debug.js
   ```

5. **Only your real work gets committed!** ✨

## 💡 Examples

### Scenario 1: Debugging

```bash
# You create a debug file
echo "console.log('debug')" > debug.js

# Protect it so you don't accidentally commit it
nostage add debug.js

# Work on your feature
vim feature.js

# Commit everything - debug.js is automatically protected!
git add .
git commit -m "Add feature"
```

### Scenario 2: Experimental Code

```bash
# Protect experimental files
nostage add experiment.py
nostage pattern "test_*.py"

# Experiment freely
# When ready, remove protection and commit
nostage remove experiment.py
git add experiment.py
git commit -m "Add new algorithm"
```

### Scenario 3: Team Project

```bash
# Each developer can protect their own files
# Alice protects her debug scripts
nostage add alice-debug.sh

# Bob protects his test data
nostage add test-data.json

# No .gitignore conflicts, everyone's happy! 🎉
```

## 🛠️ Commands

| Command | Description |
|---------|-------------|
| `nostage init` | Install NoStage hook in current repo |
| `nostage add <files...>` | Protect specific files |
| `nostage remove <files...>` | Unprotect specific files |
| `nostage pattern <pattern>` | Protect files matching pattern |
| `nostage remove-pattern <pattern>` | Remove pattern protection |
| `nostage list` | Show all protected files/patterns |
| `nostage status` | Show NoStage status |
| `nostage uninstall` | Remove NoStage hook |

## ⚙️ Requirements

- Python 3.7+
- Git

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

MIT License - feel free to use in your projects!

## 🌟 Show Your Support

If NoStage helps you, give it a ⭐ on GitHub!

---

**Made with ❤️ by developers who've accidentally committed debug files one too many times.**
