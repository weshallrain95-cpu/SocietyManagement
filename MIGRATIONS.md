# Database Migrations
# Migration Governance Policy

## Principles
- No destructive migrations without rollback
- All migrations must be reversible
- All migrations must be versioned
- All migrations must be auditable
- No silent schema changes

## Rules
- Every migration has:
  - ID
  - Purpose
  - Rollback plan
  - Environment scope
  - Approval record

## Process
1. Design migration
2. Risk analysis
3. Governance approval
4. Staging execution
5. Validation
6. Production execution
7. Post-migration audit

## Enforcement
No migration can reach prod without:
- CI validation
- Governance approval
- Rollback plan

