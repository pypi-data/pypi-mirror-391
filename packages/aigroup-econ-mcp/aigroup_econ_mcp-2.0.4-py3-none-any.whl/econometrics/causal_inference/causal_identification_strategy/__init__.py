"""
因果识别策略模块
"""

from .instrumental_variables import (
    instrumental_variables_2sls,
    IVResult
)

from .difference_in_differences import (
    difference_in_differences,
    DIDResult
)

from .regression_discontinuity import (
    regression_discontinuity,
    RDDResult
)

from .fixed_effects import (
    fixed_effects_model,
    FixedEffectsResult
)

from .random_effects import (
    random_effects_model,
    RandomEffectsResult
)

from .control_function import (
    control_function_approach,
    ControlFunctionResult
)

from .first_difference import (
    first_difference_model,
    FirstDifferenceResult
)

from .triple_difference import (
    triple_difference,
    TripeDifferenceResult
)

from .event_study import (
    event_study,
    EventStudyResult
)

from .synthetic_control import (
    synthetic_control_method,
    SyntheticControlResult
)

from .propensity_score_matching import (
    propensity_score_matching,
    PSMMatchResult
)

from .mediation_analysis import (
    mediation_analysis,
    MediationResult
)

from .moderation_analysis import (
    moderation_analysis,
    ModerationResult
)

from .hausman_test import (
    hausman_test,
    HausmanResult
)

__all__ = [
    "instrumental_variables_2sls",
    "difference_in_differences",
    "regression_discontinuity",
    "fixed_effects_model",
    "random_effects_model",
    "control_function_approach",
    "first_difference_model",
    "triple_difference",
    "event_study",
    "synthetic_control_method",
    "propensity_score_matching",
    "mediation_analysis",
    "moderation_analysis",
    "hausman_test",
    "IVResult",
    "DIDResult",
    "RDDResult",
    "FixedEffectsResult",
    "RandomEffectsResult",
    "ControlFunctionResult",
    "FirstDifferenceResult",
    "TripeDifferenceResult",
    "EventStudyResult",
    "SyntheticControlResult",
    "PSMMatchResult",
    "MediationResult",
    "ModerationResult",
    "HausmanResult"
]