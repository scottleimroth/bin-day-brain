# Bin Day Brain - Security Audit Checklist

## ABSOLUTE RULE: CREDENTIALS.md MUST NEVER BE PUBLIC

- CREDENTIALS.md must ALWAYS be listed in .gitignore -- no exceptions
- It must NEVER be committed to git, pushed to any remote, or exposed in any public or shared location
- If accidentally committed, treat as a full breach: rotate ALL keys/secrets immediately and scrub from git history
- Never reference CREDENTIALS.md contents directly in code -- always load via environment variables
- Never copy credential values into READMEs, comments, logs, error messages, or documentation
- Never expose credentials in CI/CD logs, build artifacts, or debug output

---

## Audit Checklist

### 1. Credentials & Secrets Exposure (CHECK FIRST -- EVERY TIME)

- [ ] CREDENTIALS.md exists and is listed in .gitignore
- [ ] .env file exists and is listed in .gitignore
- [ ] No API keys, tokens, passwords, or secrets hardcoded anywhere in source code
- [ ] No secrets in git history (run: `git log --all -p | grep -i "key\|secret\|password\|token"`)
- [ ] All credentials loaded via environment variables, never string literals
- [ ] No credentials in README, comments, logs, error messages, or docs
- [ ] No credentials in build artifacts or CI/CD output
- [ ] API keys use minimum required permissions/scopes
- [ ] All .gitignore entries confirmed: .env, CREDENTIALS.md, config files with secrets, database files, *.key, *.pem

### 2. Input & Data Handling

- [ ] ALL user inputs sanitised -- forms, URLs, query params, headers, file uploads
- [ ] Protected against SQL injection (parameterised queries only, never string concatenation)
- [ ] Protected against XSS (output encoding, CSP headers)
- [ ] Protected against CSRF (tokens on state-changing requests)
- [ ] Protected against command injection (no user input in shell commands)
- [ ] File uploads validated: type, size, content scanning
- [ ] Error handling doesn't leak system info (no stack traces, DB structure, file paths in responses)
- [ ] JSON/XML parsing handles malformed input gracefully

### 3. Authentication & Access

- [ ] All auth flows validated (login, signup, password reset, session management)
- [ ] Strong password policy enforced (minimum length, complexity)
- [ ] Rate limiting on auth endpoints (prevent brute force)
- [ ] Secure session tokens with proper expiry
- [ ] Password storage uses bcrypt/argon2 (never MD5/SHA1/plaintext)
- [ ] OAuth/SSO follows current best practices
- [ ] Admin/privileged routes properly protected
- [ ] Failed login attempts logged and monitored
- [ ] Account lockout after repeated failures

### 4. Network & API Security

- [ ] HTTPS enforced everywhere, no mixed content
- [ ] CORS policy properly configured (not wildcard * in production)
- [ ] Webhook payloads validated and sanitised
- [ ] API rate limiting implemented
- [ ] Request size limits set
- [ ] Security headers configured:
  - [ ] Content-Security-Policy (CSP)
  - [ ] Strict-Transport-Security (HSTS)
  - [ ] X-Frame-Options
  - [ ] X-Content-Type-Options
  - [ ] X-XSS-Protection
  - [ ] Referrer-Policy
  - [ ] Permissions-Policy

### 5. Dependencies & Supply Chain

- [ ] All packages audited for vulnerabilities:
  - npm: `npm audit`
  - pip: `pip audit` or `safety check`
  - Flutter/Dart: `dart pub audit` or `flutter pub audit`
- [ ] Dependency versions pinned (no floating ranges in production)
- [ ] No abandoned or unmaintained packages
- [ ] Package permissions reviewed (what does each package access?)
- [ ] Lock files committed (package-lock.json, pubspec.lock, etc.)

### 6. Database & Storage

- [ ] Parameterised queries exclusively -- never string concatenation
- [ ] Sensitive data encrypted at rest (PII with AES-256, passwords with bcrypt/argon2)
- [ ] Database connections use SSL/TLS
- [ ] Minimum-privilege database user accounts
- [ ] Backup procedures in place and tested
- [ ] No sensitive data in database logs
- [ ] Old/unused data has retention/deletion policy

### 7. Deployment & Infrastructure

- [ ] Debug mode DISABLED in production
- [ ] All test accounts, sample data, and dev endpoints removed
- [ ] Firewall rules configured
- [ ] Logging and monitoring active for suspicious activity
- [ ] Automated vulnerability scanning enabled (if available)
- [ ] Server/platform security patches up to date
- [ ] No default credentials on any service
- [ ] Backup and recovery procedures documented and tested

### 8. Code Quality & Future-Proofing

- [ ] No TODO: SECURITY comments left unresolved before deploy
- [ ] Deprecated functions/libraries replaced
- [ ] Security-sensitive code has clear comments explaining WHY
- [ ] Any temporarily relaxed security marked with `// TODO: SECURITY - tighten for production`
- [ ] Code review completed on security-sensitive changes

---

## Known Risks & Accepted Trade-offs

| Risk | Reason Accepted | Mitigation | Review Date |
|------|----------------|------------|-------------|
| Public APIs used without auth | Wollongong Waste & Open-Meteo are free public APIs | Monitor for API changes | 2026-06-01 |

---

## Incident Log

| Date | Incident | Action Taken | Resolved |
|------|----------|-------------|----------|
|      |          |             |          |

---

## Audit Priority Order

1. CREDENTIALS.md is .gitignored and unexposed
2. Secrets exposure (cross-reference CREDENTIALS.md against entire codebase)
3. Input validation and sanitisation
4. Authentication flows
5. Dependencies and supply chain
6. Network and deployment config

---

**Last audited:** 2026-02-10
**Audited by:** Claude Code
**Next audit due:** 2026-05-10
