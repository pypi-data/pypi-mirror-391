from __future__ import annotations
from typing import  cast, TYPE_CHECKING
from zempy.zosapi.core.types_var import N, Z
from zempy.zosapi.analysis.adapters.ia import IA
from zempy.zosapi.analysis.enums.analysisIDM import AnalysisIDM
from zempy.zosapi.analysis.adapters.analysis_registry import register_analysis
from zempy.zosapi.analysis.fftpsf.adapter.psf_settings import PSFSettings

if TYPE_CHECKING:
    from zempy.zosapi.analysis.fftpsf.protocols.IAS_FftPsf import IAS_FftPsf

@register_analysis(AnalysisIDM.FftPsf)
class FFTPSF(IA[PSFSettings, Z, N]):

    def __str__(self) -> str:
        return f"FFT PSF settings={self.settings}"

    @property
    def settings(self) -> IAS_FftPsf:
        return cast(IAS_FftPsf, super().settings)