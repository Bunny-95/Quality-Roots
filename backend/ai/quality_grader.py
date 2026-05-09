"""
Organic Roots AI Quality Grader
Uses RandomForest to grade product batches as Grade A/B/C
Trained on well-separated synthetic boundaries so high-quality inputs predict A.
"""
import sys
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from typing import Dict, Any, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RANDOM_STATE, MODEL_DIR


def _build_separated_training_arrays(seed: int = RANDOM_STATE) -> Tuple[np.ndarray, np.ndarray]:
    """Synthetic data with clear, non-overlapping grade regions (200 samples each)."""
    rng = np.random.default_rng(seed)
    n = 200

    # Grade A — high quality
    grade_a = np.column_stack([
        rng.uniform(5, 12, n),
        rng.uniform(7.5, 10, n),
        rng.uniform(7.5, 10, n),
        rng.uniform(0, 5, n),
        rng.uniform(120, 200, n),
    ])

    # Grade B — average quality
    grade_b = np.column_stack([
        rng.uniform(12, 20, n),
        rng.uniform(5, 7.5, n),
        rng.uniform(5, 7.5, n),
        rng.uniform(5, 15, n),
        rng.uniform(80, 120, n),
    ])

    # Grade C — poor quality
    grade_c = np.column_stack([
        rng.uniform(20, 40, n),
        rng.uniform(0, 5, n),
        rng.uniform(0, 5, n),
        rng.uniform(15, 50, n),
        rng.uniform(30, 80, n),
    ])

    X = np.vstack([grade_a, grade_b, grade_c])
    y = np.array(["A"] * n + ["B"] * n + ["C"] * n)
    return X, y


class QualityGrader:
    """AI-based quality grader for agricultural products"""

    def __init__(self):
        self.model = None
        self.feature_columns = [
            "moisture_level",
            "color_score",
            "aroma_score",
            "defect_percentage",
            "weight_per_unit",
        ]
        self.product_types = ["spice", "coffee", "tea", "millet", "organic"]
        self.model_path = MODEL_DIR / "quality_grader.joblib"
        self.is_trained = False
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

    def generate_synthetic_data(self) -> pd.DataFrame:
        """Build training DataFrame from separated synthetic arrays."""
        X, y = _build_separated_training_arrays(RANDOM_STATE)
        df = pd.DataFrame(X, columns=self.feature_columns)
        df["grade"] = y
        a_ct = (df["grade"] == "A").sum()
        b_ct = (df["grade"] == "B").sum()
        c_ct = (df["grade"] == "C").sum()
        print(
            f"[QUALITY_GRADER] Synthetic data: {a_ct} A, {b_ct} B, {c_ct} C "
            f"(total {len(df)})"
        )
        return df

    def train_model(self) -> Dict[str, Any]:
        """Train the quality grading model and persist to disk."""
        print("[QUALITY_GRADER] Training RandomForest on separated synthetic data...")
        df = self.generate_synthetic_data()
        X = df[self.feature_columns]
        y = df["grade"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
        )

        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=RANDOM_STATE,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=1,
            class_weight="balanced_subsample",
        )
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"[QUALITY_GRADER] Hold-out accuracy: {accuracy:.3f}")
        print(classification_report(y_test, y_pred))

        joblib.dump(self.model, self.model_path)
        self.is_trained = True

        return {
            "accuracy": accuracy,
            "feature_importance": dict(
                zip(self.feature_columns, self.model.feature_importances_)
            ),
            "training_samples": len(df),
            "test_samples": len(X_test),
        }

    def load_model(self) -> bool:
        """Load trained model from disk, or train if missing."""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                print("[QUALITY_GRADER] Model loaded from disk")
                return True
            print("[QUALITY_GRADER] No saved model; training new one...")
            self.train_model()
            return True
        except Exception as e:
            print(f"[QUALITY_GRADER] Load failed ({e}); retraining...")
            self.train_model()
            return True

    def _proba_dict(self, X: pd.DataFrame) -> Tuple[str, float, Dict[str, float]]:
        """
        Predict grade, confidence = probability mass on predicted class,
        and full A/B/C probabilities aligned to model.classes_.
        """
        proba = self.model.predict_proba(X)[0]
        classes = [str(c) for c in self.model.classes_]
        pred = self.model.predict(X)[0]
        pred = str(pred)

        idx_map = {c: i for i, c in enumerate(classes)}
        if pred not in idx_map:
            pred = classes[int(np.argmax(proba))]
        confidence = float(proba[idx_map[pred]])

        grade_probabilities = {"A": 0.0, "B": 0.0, "C": 0.0}
        for c, p in zip(classes, proba):
            if c in grade_probabilities:
                grade_probabilities[c] = float(p)
        return pred, confidence, grade_probabilities

    def grade_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a product batch; confidence is P(predicted grade)."""
        if not self.is_trained:
            self.load_model()

        features = []
        for col in self.feature_columns:
            value = batch_data.get(col)
            if value is None:
                raise ValueError(f"Missing required feature: {col}")
            features.append(float(value))

        X_row = pd.DataFrame([features], columns=self.feature_columns)
        grade, confidence, grade_probs = self._proba_dict(X_row)

        quality_score = self._calculate_quality_score(batch_data)
        recommendations = self._generate_recommendations(batch_data, grade)

        return {
            "grade": grade,
            "confidence": round(confidence, 3),
            "quality_score": round(quality_score, 1),
            "recommendations": recommendations,
            "grade_probabilities": {
                "A": round(grade_probs["A"], 3),
                "B": round(grade_probs["B"], 3),
                "C": round(grade_probs["C"], 3),
            },
        }

    def _calculate_quality_score(self, batch_data: Dict[str, Any]) -> float:
        """Overall quality score (0-100) for display (independent of ML grade)."""
        moisture = batch_data["moisture_level"]
        color = batch_data["color_score"]
        aroma = batch_data["aroma_score"]
        defects = batch_data["defect_percentage"]

        moisture_score = max(0, 100 - abs(moisture - 12) * 5)
        color_score = color * 10
        aroma_score = aroma * 10
        defect_score = max(0, 100 - defects * 2)

        total_score = (
            moisture_score * 0.25
            + color_score * 0.25
            + aroma_score * 0.3
            + defect_score * 0.2
        )
        return min(100, max(0, total_score))

    def _generate_recommendations(
        self, batch_data: Dict[str, Any], grade: str
    ) -> List[str]:
        recommendations = []
        moisture = batch_data["moisture_level"]
        color = batch_data["color_score"]
        aroma = batch_data["aroma_score"]
        defects = batch_data["defect_percentage"]

        if moisture > 15:
            recommendations.append(
                "Reduce moisture content to <15% for better preservation"
            )
        elif moisture < 8:
            recommendations.append(
                "Moisture content is low, ensure proper storage conditions"
            )
        if color < 6:
            recommendations.append(
                "Improve color quality through better processing methods"
            )
        if aroma < 6:
            recommendations.append(
                "Enhance aroma profile through optimized curing/drying"
            )
        if defects > 10:
            recommendations.append(
                "Implement better quality control to reduce defects"
            )
        if grade == "A":
            recommendations.append("Excellent quality! Consider premium pricing")
        elif grade == "B":
            recommendations.append("Good quality with room for improvement")
        else:
            recommendations.append("Quality needs significant improvement")
        return recommendations

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_trained:
            self.load_model()
        return dict(zip(self.feature_columns, self.model.feature_importances_))

    def batch_grade_multiple(self, batches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for batch in batches:
            try:
                result = self.grade_batch(batch)
                result["batch_code"] = batch.get("batch_code", "unknown")
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "batch_code": batch.get("batch_code", "unknown"),
                        "error": str(e),
                    }
                )
        return results


quality_grader = QualityGrader()


def test_quality_grader():
    print("[TEST] Quality Grader")
    test_batch = {
        "batch_code": "TEST001",
        "product_type": "coffee",
        "moisture_level": 11.5,
        "color_score": 8.2,
        "aroma_score": 8.7,
        "defect_percentage": 2.1,
        "weight_per_unit": 205.0,
    }
    result = quality_grader.grade_batch(test_batch)
    print(f"  Grade: {result['grade']} confidence={result['confidence']}")
    high_grade = {
        "batch_code": "HIGH",
        "product_type": "organic",
        "moisture_level": 8,
        "color_score": 9,
        "aroma_score": 8.5,
        "defect_percentage": 3,
        "weight_per_unit": 150,
    }
    r2 = quality_grader.grade_batch(high_grade)
    print(f"  High-quality sample: {r2['grade']} confidence={r2['confidence']} probs={r2['grade_probabilities']}")


if __name__ == "__main__":
    test_quality_grader()
