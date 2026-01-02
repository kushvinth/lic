# Security Policy

## Supported Versions

We actively support the following versions of lic with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

As lic is in early development (v0.1.x), we recommend always using the latest version available on [PyPI](https://pypi.org/project/lic-cli/) or via [Homebrew](https://github.com/kushvinth/homebrew-tap).

## Reporting a Vulnerability

We take the security of lic seriously. If you discover a security vulnerability, please follow these steps:

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Email**: <kushvinth.m@gmail.com>
- **Subject**: `[SECURITY] Brief description of the issue`

### What to Include

To help us understand and resolve the issue quickly, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: What an attacker could potentially achieve
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Environment**: Your OS, Python version, and installation method (PyPI, Homebrew, source)
- **Proof of Concept**: If applicable, include code or commands that demonstrate the vulnerability

### What to Expect

- **Initial Response**: We aim to acknowledge your report within **48 hours**
- **Updates**: We will keep you informed about our progress at least once every **5 business days**
- **Timeline**: We aim to release a fix within **7-14 days** for critical vulnerabilities, depending on complexity
- **Credit**: If you wish, we will credit you in the security advisory and release notes (you can remain anonymous if preferred)

### If the Vulnerability is Accepted

- We will work on a fix and coordinate with you on disclosure timing
- A security advisory will be published on GitHub
- A new version with the fix will be released
- You will be notified when the fix is available

### If the Vulnerability is Declined

- We will provide a clear explanation of why we do not consider it a security issue
- If appropriate, we may suggest alternative ways to address your concern (e.g., as a feature request or bug report)

## Security Best Practices

When using lic, we recommend:

- Always use the latest version
- Be cautious when running lic with elevated privileges
- Review the generated LICENSE file before committing it to your repository
- Keep your Python environment and dependencies up to date

## Scope

This security policy applies to:

- The lic-cli package distributed via PyPI
- The official lic Homebrew formula
- The source code in the [main repository](https://github.com/kushvinth/lic)

## Contact

For any questions about this security policy, please contact <kushvinth.m@gmail.com>.

---

**Thank you for helping keep lic and its users safe!**
