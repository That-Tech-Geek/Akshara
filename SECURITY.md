# Security Policy

## Supported Versions

The following versions of the project are actively supported with security updates:

| Version | Supported          |
|---------|--------------------|
| 1.x     | ✅ Fully Supported |
| 0.x     | ❌ No longer supported |

Please update to the latest version to ensure you receive security fixes.

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please follow the steps below:

1. **Do not publicly disclose the issue.**  
   Instead, report it privately to the maintainers using the contact method outlined below.

2. **Contact Method:**  
   Send an email to **sambit1912@gmail.com** with the following details:
   - A clear description of the vulnerability.
   - Steps to reproduce the issue, if applicable.
   - Your contact information for follow-up.

3. **Response Time:**  
   - We will acknowledge receipt of your report within **48 hours**.
   - We will provide updates on the status of the issue within **5 business days**.

4. **Coordinated Disclosure:**  
   We ask that you allow us a reasonable amount of time to address the issue before disclosing it publicly.

---

## Security Best Practices for Contributors

To ensure the project remains secure, contributors are encouraged to follow these guidelines:

- **Review dependencies regularly:** Use tools like `pip-audit`, `npm audit`, or similar to check for vulnerabilities in dependencies.
- **Avoid hardcoding sensitive information:** Use environment variables or `secrets.toml` to handle sensitive data securely.
- **Follow coding best practices:** Validate user inputs and use secure coding techniques to prevent injection vulnerabilities.
- **Use HTTPS for API calls:** Ensure all communications with external APIs are encrypted and secure.

---

## Public Vulnerability Disclosures

We maintain a public record of resolved security issues in our project. Please refer to the [Security Advisories](https://github.com/yourusername/yourproject/security/advisories) section for more information.

---

## Additional Resources

- [OWASP Top 10 Security Risks](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://realpython.com/python-security/)
- [GitHub Security Features](https://docs.github.com/en/code-security)
