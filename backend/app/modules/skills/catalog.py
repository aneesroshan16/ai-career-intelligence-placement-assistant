"""Role learning metadata kept on the backend, separate from presentation code.

The database remains the source for role/skill membership and importance.  This
catalog adds the instructional information that is intentionally static: topic
sequencing, prerequisites and observable outcomes.  Add a new role here (and
seed its skills) without changing a React component.
"""

SKILL_METADATA = {
    "Python": {"prerequisites": [], "topics": ["syntax and functions", "collections", "error handling"], "assessment": "Write small data-processing functions"},
    "SQL": {"prerequisites": [], "topics": ["SELECT and filtering", "joins", "aggregation", "subqueries", "window functions"], "assessment": "Query a multi-table dataset"},
    "Statistics": {"prerequisites": [], "topics": ["distributions", "hypothesis tests", "confidence intervals"], "assessment": "Interpret an experiment result"},
    "Pandas": {"prerequisites": ["Python"], "topics": ["dataframes", "cleaning", "groupby", "merging"], "assessment": "Clean and analyze a CSV"},
    "NumPy": {"prerequisites": ["Python"], "topics": ["arrays", "vectorization", "broadcasting"], "assessment": "Implement vectorized calculations"},
    "Machine Learning": {"prerequisites": ["Python", "Statistics", "Pandas"], "topics": ["feature engineering", "validation", "classification", "metrics"], "assessment": "Train and evaluate a baseline model"},
    "Deep Learning": {"prerequisites": ["Machine Learning"], "topics": ["neural networks", "optimization", "regularization"], "assessment": "Explain and train a small neural network"},
    "Scikit-learn": {"prerequisites": ["Python", "Pandas", "Machine Learning"], "topics": ["pipelines", "cross validation", "model selection"], "assessment": "Build a reproducible ML pipeline"},
    "React": {"prerequisites": ["JavaScript"], "topics": ["components", "state", "effects", "routing"], "assessment": "Build an accessible interactive page"},
    "Node.js": {"prerequisites": ["JavaScript"], "topics": ["HTTP", "async I/O", "API design"], "assessment": "Implement a REST endpoint"},
    "Docker": {"prerequisites": [], "topics": ["images", "containers", "environment configuration"], "assessment": "Containerize a service"},
    "Kubernetes": {"prerequisites": ["Docker"], "topics": ["pods", "deployments", "services"], "assessment": "Deploy a containerized application"},
    "AWS": {"prerequisites": [], "topics": ["IAM", "compute", "storage", "networking"], "assessment": "Design a least-privilege deployment"},
}


def metadata_for(skill: str) -> dict:
    """Return a useful safe default for catalog skills without custom metadata."""
    return SKILL_METADATA.get(skill, {
        "prerequisites": [],
        "topics": [f"core {skill} concepts", f"applied {skill} practice"],
        "assessment": f"Demonstrate {skill} in a small role-relevant exercise",
    })
