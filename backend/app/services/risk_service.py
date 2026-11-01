from typing import Dict, Any, Optional
from app.detection.thresholds import score_to_severity


class RiskService:
    @staticmethod
    def calculate_risk(
        rule_score: int,
        ml_score: int,
        anomaly_score: float,
        is_attack: bool,
    ) -> Dict[str, Any]:
        """
        Calculate composite risk score.
        Alert-first principle: firewall blocking is never automatically applied.
        """
        base = max(rule_score, ml_score)
        anomaly_bonus = int(max(0.0, -anomaly_score) * 40) if anomaly_score < 0 else 0
        composite = min(100, base + anomaly_bonus)

        severity = score_to_severity(composite)

        # Recommendation: require authenticated administrator approval for any blocking
        if composite >= 85:
            recommendation = "Recommend administrator review for temporary block."
            eligible_for_block_request = True
        elif composite >= 65:
            recommendation = "Escalate for analyst triage and packet inspection."
            eligible_for_block_request = False
        else:
            recommendation = "Maintain routine log monitoring."
            eligible_for_block_request = False

        return {
            "risk_score": composite,
            "severity": severity,
            "recommendation": recommendation,
            "eligible_for_block_request": eligible_for_block_request,
        }
