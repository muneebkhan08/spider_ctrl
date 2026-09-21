# Contributing to SPIDER_CTRL

Thank you for your interest in contributing to SPIDER_CTRL! We welcome community contributions, bug reports, and enhancements.

To keep the repository stable, secure, and production-ready, all contributions must follow the workflow outlined below.

---

## 🔒 Security Notice: No Direct Pushes to `main`

**Direct pushes to the `main` branch are strictly prohibited and blocked by repository protection rules.**

All changes—including those by core maintainers—must be submitted as a **Pull Request (PR)** from a fork or a dedicated feature branch, pass all automated CI tests, and receive explicit approval from the repository code owner (`@muneebkhan08`).

---

## Contribution Workflow

### 1. Fork the Repository
Click the **Fork** button at the top right of the GitHub page to create your own copy of the repository.

### 2. Clone Your Fork Locally
```bash
git clone https://github.com/<your-username>/spider_ctrl.git
cd spider_ctrl
```

### 3. Create a Feature Branch
Use a descriptive branch name prefix:
* `feat/` for new features (e.g., `feat/audio-streaming`)
* `fix/` for bug fixes (e.g., `fix/linux-pactl-volume`)
* `docs/` for documentation changes (e.g., `docs/troubleshooting-guide`)
* `refactor/` for code refactoring

```bash
git checkout -b feat/my-new-feature
```

### 4. Set Up the Local Environment

#### Backend (Python)
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Frontend (Next.js)
```bash
cd ../frontend
npm install
```

### 5. Verify Tests & Build Locally

Before submitting your PR, ensure that all tests and build checks pass:

```bash
# Run backend test suite (from project root)
./server/venv/bin/python -m pytest server/tests

# Verify frontend types and production build
cd frontend
npx tsc --noEmit
npm run build
```

### 6. Commit Your Changes
* Write clear, conventional commit messages (e.g., `feat: add configurable screen resolution`, `fix: handle websocket disconnection cleanly`).
* **Never commit secrets, tokens, private keys (`.pem`, `.key`), or machine-specific configs.**

### 7. Push and Open a Pull Request
Push your branch to your GitHub fork and open a Pull Request against the `main` branch of `muneebkhan08/spider_ctrl`:
```bash
git push origin feat/my-new-feature
```

Fill out the Pull Request template completely, including the security and testing checklist.

---

## Code Review & Merge Process

1. **Automated CI**: GitHub Actions will automatically run the backend test suite and frontend type checks on your PR.
2. **Code Owner Approval**: The PR will be reviewed by `@muneebkhan08` (enforced via `.github/CODEOWNERS`).
3. **Squash & Merge**: Once approved and all CI checks pass, your changes will be merged into `main`.

---

## Reporting Bugs & Suggesting Features

* **Feature Requests & Non-Security Bugs**: Please open a standard [GitHub Issue](https://github.com/muneebkhan08/spider_ctrl/issues).
* **Security Vulnerabilities**: Do **not** open a public issue. Follow the instructions in [SECURITY.md](SECURITY.md).
