"""
Generates a synthetic, plausibly-correlated placement-outcomes dataset for
bootstrapping the placement prediction model before real cohort outcome
data exists. Run:

    python scripts/generate_synthetic_placement_data.py

Writes data/placement_training.csv (1500 rows).
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 1500


def generate() -> pd.DataFrame:
    cgpa = np.clip(RNG.normal(7.5, 1.0, N), 4.0, 10.0)
    internships = RNG.poisson(1.1, N).clip(0, 5)
    projects_count = RNG.poisson(3, N).clip(0, 10)
    certifications_count = RNG.poisson(1.5, N).clip(0, 8)
    skills_count = RNG.poisson(9, N).clip(1, 25)
    coding_score = np.clip(RNG.normal(65, 18, N), 0, 100)
    aptitude_score = np.clip(RNG.normal(60, 15, N), 0, 100)
    ats_score = np.clip(RNG.normal(70, 15, N), 0, 100)
    interview_score = np.clip(RNG.normal(62, 17, N), 0, 100)

    # Weighted linear combination -> logistic probability -> Bernoulli label.
    z = (
        0.55 * (cgpa - 7.5)
        + 0.45 * internships
        + 0.22 * projects_count
        + 0.15 * certifications_count
        + 0.08 * (skills_count - 9)
        + 0.035 * (coding_score - 65)
        + 0.025 * (aptitude_score - 60)
        + 0.025 * (ats_score - 70)
        + 0.035 * (interview_score - 62)
    )
    prob = 1 / (1 + np.exp(-z / 1.4))
    placed = RNG.binomial(1, prob)

    return pd.DataFrame({
        "cgpa": cgpa.round(2),
        "internships": internships,
        "projects_count": projects_count,
        "certifications_count": certifications_count,
        "skills_count": skills_count,
        "coding_score": coding_score.round(1),
        "aptitude_score": aptitude_score.round(1),
        "ats_score": ats_score.round(1),
        "interview_score": interview_score.round(1),
        "placed": placed,
    })


if __name__ == "__main__":
    df = generate()
    df.to_csv("data/placement_training.csv", index=False)
    print(f"Wrote {len(df)} rows to data/placement_training.csv")
    print(f"Placement rate: {df['placed'].mean():.2%}")
