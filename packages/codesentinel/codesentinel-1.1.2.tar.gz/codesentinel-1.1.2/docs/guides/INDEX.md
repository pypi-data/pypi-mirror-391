# Publication & Deployment Guides

## Overview

This directory contains comprehensive guides for publishing, deploying, and maintaining CodeSentinel across different environments and platforms.

## Quick Reference

### For Immediate Publishing

**→ Start here:** [`QUICK_PUBLISH_REFERENCE.md`](./QUICK_PUBLISH_REFERENCE.md)

- One-page checklist for quick publication
- Essential steps only
- ~5-10 minutes

### For Detailed Publication Process

**→ Full guide:** [`PYPI_PUBLICATION_GUIDE.md`](./PYPI_PUBLICATION_GUIDE.md)

- Complete step-by-step instructions
- Troubleshooting and verification steps
- Test repository and production procedures
- ~30-45 minutes

## Available Guides

### Publication & Release

| Guide | Purpose | Audience | Time |
|-------|---------|----------|------|
| [`QUICK_PUBLISH_REFERENCE.md`](./QUICK_PUBLISH_REFERENCE.md) | Quick checklist for publishing | Developers | 5-10m |
| [`PYPI_PUBLICATION_GUIDE.md`](./PYPI_PUBLICATION_GUIDE.md) | Complete publication process | Release managers | 30-45m |
| `publish_v1_0_3_beta.py` | Automated publication script | CI/CD systems | Auto |

### Installation & Setup

| Guide | Purpose | Audience |
|-------|---------|----------|
| [`QUICK_START.md`](./QUICK_START.md) | User installation guide | End users |
| `README.md` | Guide directory overview | Everyone |

## Release Workflow

```
1. Development → Version Bump → Testing (completed)
                          ↓
2. Build distributions (sdist + wheel)
                          ↓
3. Test on test.pypi.org (QUICK_PUBLISH_REFERENCE.md)
                          ↓
4. Verify with test installation
                          ↓
5. Publish to production PyPI (PYPI_PUBLICATION_GUIDE.md)
                          ↓
6. Tag release in Git → Update CHANGELOG
```

## Publication Checklist

### Pre-Publication (Run once per release)

- [ ] Version number updated in all locations
- [ ] CHANGELOG.md updated with release notes
- [ ] All tests passing (22/22)
- [ ] Distributions built and tested
- [ ] Documentation current and links verified
- [ ] No blocking security issues

### Test Repository Publication

- [ ] Upload to test.pypi.org
- [ ] Verify package downloads correctly
- [ ] Install and verify CLI works: `codesentinel --help`
- [ ] Install and verify GUI works: `codesentinel setup --gui`

### Production Publication

- [ ] Final confirmation from maintainer
- [ ] Upload to production PyPI
- [ ] Verify on PyPI package page
- [ ] Create GitHub release tag
- [ ] Announce in documentation

## Current Status: v1.0.3.beta

**Last Updated:** November 10, 2025

| Item | Status |
|------|--------|
| Version | 1.0.3.beta (normalized to 1.0.3b0) |
| Tests |  22/22 passing |
| CLI |  All commands functional |
| GUI |  Wizard operational |
| Distributions |  Built (sdist + wheel) |
| Documentation |  Current |
| Ready for Publication |  Yes |

## Next Steps

1. **For quick publication:** Read [`QUICK_PUBLISH_REFERENCE.md`](./QUICK_PUBLISH_REFERENCE.md)
2. **For detailed guide:** Read [`PYPI_PUBLICATION_GUIDE.md`](./PYPI_PUBLICATION_GUIDE.md)
3. **For test upload:** Follow steps 1-3 in quick reference
4. **For production:** Follow complete publication guide

## Troubleshooting

### Publication Issues

| Problem | Solution |
|---------|----------|
| Build errors | Check `setup.py` and `pyproject.toml` for syntax errors |
| Authentication fails | Verify PyPI token in `~/.pypirc` or `./.pypirc` |
| Upload rejected | Check version format (must be valid PEP 440) |

### Installation Issues After Publishing

| Problem | Solution |
|---------|----------|
| Installation fails | Check platform compatibility in setup.py |
| Import errors | Verify all dependencies in requirements.txt |
| Command not found | Check entry_points in setup.py |

## Support Resources

- PyPI Official: <https://pypi.org/>
- TestPyPI: <https://test.pypi.org/>
- PEP 440 (Versioning): <https://peps.python.org/pep-0440/>
- setuptools Documentation: <https://setuptools.pypa.io/>

## Related Documentation

- **Installation:** [`docs/guides/`](./README.md)
- **Architecture:** [`docs/architecture/`](../architecture/)
- **Development:** [`docs/planning/`](../planning/)
- **Compliance:** [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md)

---

*Last Updated: November 10, 2025*
*SEAM Protected™ Publication Workflow*
