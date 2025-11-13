from __future__ import annotations
from zempy.zosapi.core.im_adapter import (
    BaseAdapter, Z, N, run_native, validate_cast,
    PropertyScalar, property_enum, property_adapter, PropertySequence, PropertyEnum,
    dataclass, Optional, TYPE_CHECKING, logging,
)

from zempy.zosapi.tools.adapters.SystemTool import SystemTool
from zempy.zosapi.tools.general.enums.QuickFocusCriterion import QuickFocusCriterion

log = logging.getLogger(__name__)
@dataclass()
class QuickFocus(SystemTool[Z, N]):

    UseCentroid = PropertyScalar("UseCentroid", coerce_get=bool, coerce_set=bool)
    Criterion = PropertyEnum("Criterion", QuickFocusCriterion, read_only =False)



