from datetime import datetime, timezone

from relationalai.semantics.lqp import ir as lqp
from relationalai.semantics.lqp.constructors import mk_abstraction, mk_value, mk_var, mk_type, mk_primitive
from relationalai.semantics.lqp.utils import lqp_hash

def mk_intrinsic_datetime_now() -> lqp.Def:
    """Constructs a definition of the current datetime."""
    id = lqp_hash("__pyrel_lqp_intrinsic_datetime_now")
    out = mk_var("out")
    out_type = mk_type(lqp.TypeName.DATETIME)
    now = mk_value(lqp.DateTimeValue(value=datetime.now(timezone.utc), meta=None))
    datetime_now = mk_abstraction(
        [(out, out_type)],
        mk_primitive("rel_primitive_eq", [out, now]),
    )

    return lqp.Def(
        name = lqp.RelationId(id=id, meta=None),
        body = datetime_now,
        attrs = [],
        meta = None,
    )
