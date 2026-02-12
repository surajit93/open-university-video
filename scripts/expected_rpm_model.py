# scripts/expected_rpm_model.py

class ExpectedRPMModel:

    BASE_RPM = {
        "AI": 6.5,
        "Economy": 8.0,
        "Collapse": 4.2,
        "Human Psychology": 7.2,
        "Tech Systems": 7.8
    }

    def estimate_rpm(self, cluster: str, ad_friendly_score: float) -> float:
        base = self.BASE_RPM.get(cluster, 5.0)

        # Penalize low ad friendliness
        adjusted = base * ad_friendly_score

        return round(adjusted, 2)
