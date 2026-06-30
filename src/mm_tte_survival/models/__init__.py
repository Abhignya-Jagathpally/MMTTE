"""Model layer. Legacy neural survival nets re-exported from .neural; the
first-class ResidualRiskModel and the abstract MultiHeadSurvivalModel live
alongside."""
from .neural import SurvivalMLP, make_ema_teacher, update_ema_teacher
from .residual_risk import ResidualRiskModel

__all__ = ["SurvivalMLP", "make_ema_teacher", "update_ema_teacher", "ResidualRiskModel"]
