# Security and privacy

- Passwords use Argon2 through `pwdlib`; JWTs expire and are signed with `JWT_SECRET`.
- API ownership filters scope resources to the current account. Foreign or missing IDs return 404.
- Upload accepts PDF and DOCX, limits bytes, checks common signatures, sanitizes the stored display filename, and does not execute content.
- Parser input is untrusted. No document content is sent to a model or external provider.
- Resume source bytes are not retained; extracted text and parsed fields are stored until the user deletes the resume/account.
- Configure CORS using `FRONTEND_ORIGINS`; never commit `.env`.

Production work still needed: rate limiting and abuse controls, dependency scanning, security headers, HttpOnly cookies/CSRF design, robust MIME/container validation and malware scanning, encrypted backups, retention policy, audit trail, migrations and tested deletion from backups, and secrets rotation. Do not advertise compliance certifications or a security guarantee.
