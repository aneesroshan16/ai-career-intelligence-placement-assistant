from app.ml_core.placement_model.features import PlacementFeatures
from app.ml_core.placement_model.predict import predict_placement


def test_predict_returns_valid_probability():
    features = PlacementFeatures(
        cgpa=8.5, internships=2, projects_count=5, certifications_count=3,
        skills_count=14, coding_score=78, aptitude_score=70, ats_score=82, interview_score=75,
    )
    result = predict_placement(features)
    assert 0.0 <= result["probability"] <= 1.0
    assert isinstance(result["predicted_label"], bool)
    assert "model_version" in result


def test_strong_profile_scores_higher_than_weak_profile():
    strong = PlacementFeatures(
        cgpa=9.2, internships=3, projects_count=8, certifications_count=4,
        skills_count=20, coding_score=90, aptitude_score=88, ats_score=90, interview_score=85,
    )
    weak = PlacementFeatures(
        cgpa=5.5, internships=0, projects_count=1, certifications_count=0,
        skills_count=3, coding_score=30, aptitude_score=35, ats_score=40, interview_score=30,
    )
    assert predict_placement(strong)["probability"] > predict_placement(weak)["probability"]
