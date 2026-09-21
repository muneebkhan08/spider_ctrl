## Description
<!-- Briefly describe what this pull request does, why it is needed, and link any relevant issues. -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Security hardening

## Security Checklist
Because SPIDER_CTRL interacts directly with system input, processes, and terminal execution, all changes must pass rigorous review:
- [ ] Does this pull request modify any command execution, terminal, or shell logic?
- [ ] Does this pull request touch pairing authentication, tokens, or TLS certificates?
- [ ] Does this pull request modify the one-line installer scripts (`install.sh` or `install.ps1`)?
- [ ] I have verified that no personal tokens, secrets, private keys, or credentials are committed.

## Testing & Verification
- [ ] Backend tests pass locally (`pytest server/tests`)
- [ ] Frontend type check passes (`cd frontend && npx tsc --noEmit`)
- [ ] Frontend builds cleanly (`cd frontend && npm run build`)
- [ ] Manual testing on local machine has been performed
