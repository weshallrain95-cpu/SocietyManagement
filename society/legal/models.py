# society/legal/models.py

# ============================
# Authority Layer
# ============================

from society.legal.constitution.models.authority import (
    LegalAuthority,
    AuthorityType,
)

from society.legal.constitution.models.authority_graph import (
    LegalAuthorityRelation,
    AuthorityRelationType,
)

# ============================
# Canon Layer
# ============================

from society.legal.constitution.models.canon import (
    LegalCanonNode,
    CanonType,
)

# ============================
# Document Layer
# ============================

from society.legal.constitution.models.document import (
    LegalDocument,
    DocumentType,
)

# ============================
# Bylaw Layer
# ============================

from society.legal.constitution.models.bylaw import (
    Bylaw,
)
