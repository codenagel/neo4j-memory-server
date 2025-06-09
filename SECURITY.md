# Security Policy

## Supported Versions

| Version | Supported |
| ------- |-----------|
| 0.1.x   | yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **DO NOT** open a public GitHub issue
2. Email the maintainers privately (if you have contact info)
3. Or use GitHub's private vulnerability reporting feature

## Security Best Practices

### For Users

1. **Never use default passwords** - Always set strong, unique passwords
2. **Use environment variables** - Don't hardcode credentials in your config
3. **Network security** - Restrict access to Neo4j ports (7474, 7687)
4. **Regular updates** - Keep Neo4j and dependencies updated
5. **Data encryption** - Use TLS in production (`neo4j+s://`)

### For Contributors

1. **No secrets in code** - Use environment variables for all credentials
2. **Validate inputs** - Sanitize all user inputs to prevent injection
3. **Dependency scanning** - Keep dependencies updated and scan for vulnerabilities
4. **Code review** - All security-related changes require review

## Known Security Considerations

- This MCP server operates with full Neo4j database access
- No built-in authentication - relies on Neo4j authentication
- Knowledge graph data may contain sensitive information
- Consider access controls for production deployments

## Security Updates

Security updates will be released as patch versions and announced in:
- GitHub Releases
- README security notices
- This SECURITY.md file updates