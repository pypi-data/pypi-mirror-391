from __future__ import annotations
from zempy.zosapi.core.im_adapter import (
    BaseAdapter, Z, N, run_native, validate_cast,
    dataclass, logging,
)

from zempy.zosapi.tools.general.adapters.quickfocus.QuickFocus import QuickFocus
from zempy.zosapi.tools.general.protocols.quickfocus.IQuickFocus import IQuickFocus
from zempy.zosapi.tools.raytrace.adapters.BatchRayTrace import BatchRayTrace
from zempy.zosapi.tools.raytrace.protocols.IBatchRayTrace import IBatchRayTrace

log = logging.getLogger(__name__)
@dataclass()
class OpticalSystemTools(BaseAdapter[Z, N]):
    """ Concrete adapter over native ZOSAPI.Tools.IOpticalSystemTools."""

    def OpenQuickFocus(self) -> IQuickFocus:
        """Open the Quick Focus tool and return its adapter."""
        native_qf = run_native(
            "Tools.OpenQuickFocus",
            lambda: self.native.OpenQuickFocus(),
            ensure=self.ensure_native,
        )
        log.debug("SystemTools.OpenQuickFocus() created")
        return validate_cast(QuickFocus(self.zosapi, native_qf), IQuickFocus)

    def OpenBatchRayTrace(self) -> IBatchRayTrace:
        """Open the BatchRayTrace tool and return its adapter."""
        native_qf = run_native(
            "Tools.OpenBatchRayTrace",
            lambda: self.native.OpenBatchRayTrace(),
            ensure=self.ensure_native,
        )
        log.debug("SystemTools.OpenQuickFocus() created")
        return validate_cast(BatchRayTrace(self.zosapi, native_qf), IBatchRayTrace)




    def RemoveAllVariables(self) -> bool:
        """Remove all lens/system variables. Returns True on success."""
        ok = run_native(
            "Tools.RemoveAllVariables",
            lambda: getattr(self.native, "RemoveAllVariables")(),
            ensure=self.ensure_native,
        )
        log.debug("SystemTools.RemoveAllVariables() is completed")
        return bool(ok)