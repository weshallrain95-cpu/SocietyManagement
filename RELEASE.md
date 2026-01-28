# SocietyOS — Release Governance Model

## Versioning Standard
Semantic Versioning: vMajor.Minor.Patch

### Examples
- v1.0.0 → first production release
- v1.1.0 → feature release
- v1.1.1 → hotfix
- v2.0.0 → breaking/architecture change

---

## Branch Model

main       → production  
develop    → integration  
release/*  → release candidates  
hotfix/*   → emergency fixes  
sprint/*   → sprint execution branches  

---

## Release Flow

1. develop → release/vX.Y.Z
2. release branch testing
3. staging deployment
4. governance approval
5. tag creation
6. merge to main
7. production deployment
8. changelog update

---

## Tagging Rules

- All releases must be tagged
- No untagged production deploys
- Tags are immutable
- Tags are signed (future enforcement)

---

## Promotion Gates

| Stage | Gate |
|------|------|
| develop → release | CI + governance |
| release → main | staging validation |
| main → prod | governance approval |

---

## Rollback Model

- All releases must be revertible
- Tags define rollback points
- main must always be stable
- hotfix branches for emergency rollback

---

## Authority Rule

No code reaches production without:
- Version tag
- Release branch
- Governance approval
- Changelog entry

