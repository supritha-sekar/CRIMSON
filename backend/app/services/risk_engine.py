from typing import Dict, Any, List

class RiskEngine:
    """
    CRIMSON Explainable Risk Scoring Engine.
    Evaluates entity parameters, case metrics, indicators, and linkage metrics to yield an explainable 0-100 risk score.
    """

    @staticmethod
    def calculate_risk(
        priority: str = "MEDIUM",
        status: str = "INVESTIGATING",
        entity_count: int = 1,
        evidence_count: int = 0,
        critical_flags: List[str] = None,
        base_score: int = 30
    ) -> Dict[str, Any]:
        factors = []
        score = base_score

        # Priority Factor
        priority_map = {"LOW": 10, "MEDIUM": 25, "HIGH": 45, "CRITICAL": 70}
        p_impact = priority_map.get(priority.upper(), 25)
        score += (p_impact - 25)
        factors.append({
            "category": "Priority Rating",
            "factor": f"Case Priority set to {priority}",
            "impact": p_impact - 25,
            "description": f"Priority setting contributes +{p_impact - 25} points to total threat calculation."
        })

        # Entity Linkage Factor
        linkage_impact = min(30, entity_count * 5)
        score += linkage_impact
        factors.append({
            "category": "Entity Network Density",
            "factor": f"{entity_count} connected subject/entity linkages",
            "impact": linkage_impact,
            "description": f"Expanded entity network increases risk vector by +{linkage_impact} points."
        })

        # Critical Flags
        if critical_flags:
            flag_impact = min(40, len(critical_flags) * 15)
            score += flag_impact
            factors.append({
                "category": "Threat Indicators",
                "factor": f"Detected {len(critical_flags)} red flags ({', '.join(critical_flags[:2])})",
                "impact": flag_impact,
                "description": f"Explicit intelligence threat indicators add +{flag_impact} risk weight."
            })

        # Evidence Sensitivity
        if evidence_count > 3:
            score += 10
            factors.append({
                "category": "Evidence Volume",
                "factor": f"{evidence_count} attached evidence items",
                "impact": 10,
                "description": "Substantial evidence repository suggests complex active investigation."
            })

        # Normalize score 0-100
        score = max(0, min(100, score))

        # Risk Level Mapping
        if score >= 75:
            level = "CRITICAL"
        elif score >= 50:
            level = "HIGH"
        elif score >= 25:
            level = "MEDIUM"
        else:
            level = "LOW"

        confidence = 0.91

        summary = (
            f"Subject or case risk assessed at {score}/100 ({level}). "
            f"Primary risk drivers: {factors[0]['factor']} and {factors[1]['factor'] if len(factors) > 1 else 'standard baseline'}."
        )

        return {
            "score": score,
            "level": level,
            "confidence": confidence,
            "factors": factors,
            "summary": summary,
            "disclaimer": "This score is generated for analytical demonstration and intelligence prioritization purposes."
        }

risk_engine = RiskEngine()
