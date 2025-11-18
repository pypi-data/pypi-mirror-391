# Pull Request Requirements

### Pre-PR checklist

- [ ] Run `ruff format` and `ruff check --fix`
- [ ] Run `trufflehog git file://. --since-commit origin/main --branch HEAD --results=verified,unknown` (expect no verified results)
- [ ] Keep lines ≤ 88 chars (`E501` enforced)
- [ ] Prefix intentionally unused loop vars with `_` (satisfies B007)
- [ ] Use `trufflehog:ignore` only for reviewed, specific exceptions
