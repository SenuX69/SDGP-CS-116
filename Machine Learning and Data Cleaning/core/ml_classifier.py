"""
PathFinder+ — Hybrid ML Classification Layer
=============================================
Sits alongside SBERT embeddings to add structured ML signal to the pipeline.

Architecture:
    Assessment Vector (structured features)
            │
            ├─► RandomForestClassifier  ──► Career Segment (Entry/Mid/Senior/Exec)
            │                                Used to: filter course levels precisely
            │
            ├─► GradientBoostingClassifier ─► Course Level Fit Score
            │                                 Combined with SBERT: hybrid_score = 0.6*sbert + 0.4*ml
            │
            └─► KNeighborsClassifier (k=5) ─► Similar Profile Lookup
                                               "Profiles like yours went into X"

Why this hybrid approach?
    SBERT understands SEMANTICS (what the words mean).
    These ML models understand STRUCTURE (experience level, budget, band, etc.)
    Together they fix common failures: a BSc grad getting MSc-level courses,
    or a 10-year professional getting "Junior" recommendations.

Author: PathFinder+ ML Team (SDGP CS-116)
"""

import numpy as np
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Graceful sklearn import — engine loads fine even if sklearn is somehow missing
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ─────────────────────────────────────────────────────────────
#  Feature Engineering
# ─────────────────────────────────────────────────────────────

# Maps assessment string values → numeric features
EDUCATION_ENCODING = {
    "gcse": 0, "o/l": 0, "secondary": 0, "school": 0,
    "a/l": 1, "a-level": 1, "higher secondary": 1,
    "diploma": 2, "hnd": 2, "foundation": 2,
    "bachelor": 3, "bsc": 3, "degree": 3, "undergraduate": 3,
    "master": 4, "msc": 4, "mba": 4, "postgraduate": 4,
    "phd": 5, "doctorate": 5
}

BUDGET_ENCODING = {
    "< 50k": 0, "<50k": 0,
    "50k-200k": 1,
    "200k-500k": 2,
    "500k+": 3
}

TIME_ENCODING = {
    "< 5 hours": 0, "<5": 0, "less than 5": 0,
    "5-10 hours": 1,
    "10-20 hours": 2,
    "20+ hours": 3
}

# Career segment labels (what RF predicts)
CAREER_SEGMENTS = ["Entry", "Graduate", "Professional", "Senior", "Executive"]

# Course level encoding (what GBM uses as features + target)
COURSE_LEVEL_ENCODING = {
    "Beginner": 0, "Mid-Level": 1, "Professional": 2,
    "Academic (Diploma)": 2, "Academic (Degree)": 3, "Postgraduate": 4
}


def encode_education(value: str) -> int:
    """Converts free-text education string to numeric level 0-5."""
    v = str(value).lower().strip()
    for keyword, code in EDUCATION_ENCODING.items():
        if keyword in v:
            return code
    return 1  # Default: A/L equivalent if unknown


def encode_budget(value: str) -> int:
    """Converts budget string to numeric tier 0-3."""
    v = str(value).strip()
    return BUDGET_ENCODING.get(v, 1)


def encode_time(value: str) -> int:
    """Converts weekly availability string to numeric tier 0-3."""
    v = str(value).strip()
    for k, code in TIME_ENCODING.items():
        if k in v.lower():
            return code
    return 1


def vector_to_features(assessment_vector: Dict[str, Any]) -> np.ndarray:
    """
    Converts a processed assessment vector dict into a fixed-length numpy feature array.

    Features (8 dimensions):
        [0] experience_years     — 0, 1.5, 4, 8, 12 (raw numeric)
        [1] responsibility_band  — 0-4
        [2] status_level         — 0-3 (Student=0 → Senior=3)
        [3] problem_solving_score— 0-3
        [4] adaptability_score   — 0-3
        [5] education_encoded    — 0-5 (see EDUCATION_ENCODING)
        [6] budget_encoded       — 0-3
        [7] time_encoded         — 0-3
    """
    return np.array([
        float(assessment_vector.get("experience_years", 0)),
        float(assessment_vector.get("responsibility_band", 0)),
        float(assessment_vector.get("status_level", 0)),
        float(assessment_vector.get("problem_solving_score", 1)),
        float(assessment_vector.get("adaptability_score", 1)),
        encode_education(assessment_vector.get("highest_education", "")),
        encode_budget(str(assessment_vector.get("budget_category", "50k-200k"))),
        encode_time(str(assessment_vector.get("time_commitment", "10-20 hours"))),
    ], dtype=float)


# ─────────────────────────────────────────────────────────────
#  Training Data Generation
# ─────────────────────────────────────────────────────────────

def _generate_training_data(n_samples: int = 2500) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates synthetic training samples for the career segment classifier.

    Strategy: We encode the domain knowledge that already lives in the engine's
    rule-based logic into labelled training examples. Each sample is a realistic
    user profile; the label is the correct career segment per the rules.

    This gives us a TRAINED model that generalises the rules, making future
    predictions smoother and less brittle than pure if/else chains.

    Segments:
        0 = Entry      (school leavers, O/L, A/L, < 1yr exp)
        1 = Graduate   (fresh degree, 0-2 yrs, BSc)
        2 = Professional (2-5 yrs, BSc or more)
        3 = Senior     (5-10 yrs, BSc/MSc)
        4 = Executive  (10+ yrs, typically MSc/PhD)
    """
    rng = np.random.default_rng(42)
    X, y = [], []

    # ── Segment 0: Entry (school leaver / O/L / A/L) ──
    for _ in range(n_samples // 5):
        exp   = rng.choice([0, 0, 0, 1.5])
        band  = rng.integers(0, 2)
        status = rng.integers(0, 2)      # 0 or 1
        ps    = rng.integers(0, 3)
        ad    = rng.integers(0, 3)
        edu   = rng.integers(0, 2)       # O/L or A/L
        bud   = rng.integers(0, 3)
        time  = rng.integers(0, 4)
        X.append([exp, band, status, ps, ad, edu, bud, time])
        y.append(0)

    # ── Segment 1: Graduate (fresh BSc, 0-2 yrs) ──
    for _ in range(n_samples // 5):
        exp   = rng.choice([0, 0, 1.5, 1.5])
        band  = rng.integers(0, 2)
        status = rng.choice([1, 2])
        ps    = rng.integers(1, 4)
        ad    = rng.integers(1, 4)
        edu   = rng.integers(2, 4)       # Diploma or BSc
        bud   = rng.integers(0, 4)
        time  = rng.integers(1, 4)
        X.append([exp, band, status, ps, ad, edu, bud, time])
        y.append(1)

    # ── Segment 2: Professional (2-5 yrs, BSc) ──
    for _ in range(n_samples // 5):
        exp   = rng.choice([1.5, 4, 4, 4])
        band  = rng.integers(1, 3)
        status = rng.choice([2, 2, 3])
        ps    = rng.integers(1, 4)
        ad    = rng.integers(1, 4)
        edu   = rng.integers(3, 5)       # BSc or MSc
        bud   = rng.integers(1, 4)
        time  = rng.integers(1, 4)
        X.append([exp, band, status, ps, ad, edu, bud, time])
        y.append(2)

    # ── Segment 3: Senior (5-10 yrs) ──
    for _ in range(n_samples // 5):
        exp   = rng.choice([4, 8, 8, 8])
        band  = rng.integers(2, 5)
        status = rng.choice([2, 3, 3])
        ps    = rng.integers(2, 4)
        ad    = rng.integers(2, 4)
        edu   = rng.integers(3, 6)       # BSc, MSc, or PhD
        bud   = rng.integers(1, 4)
        time  = rng.integers(0, 4)
        X.append([exp, band, status, ps, ad, edu, bud, time])
        y.append(3)

    # ── Segment 4: Executive (10+ yrs) ──
    for _ in range(n_samples // 5):
        exp   = rng.choice([8, 12, 12, 12])
        band  = rng.integers(3, 5)
        status = rng.choice([2, 3, 3])
        ps    = rng.integers(2, 4)
        ad    = rng.integers(2, 4)
        edu   = rng.integers(4, 6)       # MSc or PhD
        bud   = rng.integers(2, 4)
        time  = rng.integers(0, 3)
        X.append([exp, band, status, ps, ad, edu, bud, time])
        y.append(4)

    return np.array(X, dtype=float), np.array(y)


def _generate_course_fit_data(n_samples: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates training data for the GBM course level fit classifier.

    Each sample = (user_features + course_level_numeric + sbert_score)
    Label = 1 if this course level is a GOOD fit for this user, 0 if not.

    Rules encoded:
        - Entry/Graduate users → Diploma & Degree are good (levels 2-3)
        - Professional users  → Professional certs & Postgrad are good (levels 2-4)
        - Senior/Executive    → Postgraduate is ideal (level 4)
        - O/L student         → Diploma & Foundation only (levels 0-2)
    """
    rng = np.random.default_rng(123)
    X, y = [], []

    segment_labels = [0, 1, 2, 3, 4]
    course_levels  = [0, 1, 2, 3, 4]  # Beginner → Postgraduate

    # Good level mapping per segment
    good_levels = {
        0: {0, 1, 2},        # Entry: Beginner, Mid, Diploma
        1: {2, 3},           # Graduate: Diploma, Degree
        2: {2, 3, 4},        # Professional: Cert, Degree, PG
        3: {3, 4},           # Senior: Degree (top-up), Postgrad
        4: {4},              # Executive: Postgrad only
    }

    for _ in range(n_samples):
        seg       = rng.choice(segment_labels)
        cl        = rng.choice(course_levels)
        sbert     = float(rng.uniform(0.3, 1.0))
        exp       = float(rng.choice([0, 0, 1.5, 4, 8, 12]))
        band      = float(rng.integers(0, 5))
        edu       = float(rng.integers(0, 6))
        bud       = float(rng.integers(0, 4))
        label     = 1 if cl in good_levels[seg] else 0
        # Add noise to make the model generalise
        if rng.random() < 0.08:
            label = 1 - label

        X.append([seg, cl, sbert, exp, band, edu, bud])
        y.append(label)

    return np.array(X, dtype=float), np.array(y)


# ─────────────────────────────────────────────────────────────
#  HybridMLLayer
# ─────────────────────────────────────────────────────────────

class HybridMLLayer:
    """
    Hybrid ML classification layer for PathFinder+.

    Combines structured machine learning models with SBERT semantic similarity
    to produce more accurate, career-stage-aware recommendations.

    Usage (inside RecommendationEngine):
        ml = HybridMLLayer(models_dir=Path("models/"))
        ml.load()          # tries to load from .pkl
        if not ml.is_trained:
            ml.train()     # generates synthetic data and trains
            ml.save()

        segment_result = ml.predict_segment(assessment_vector)
        hybrid_score   = ml.score_course_fit(assessment_vector, "Postgraduate", 0.75)
        similar        = ml.find_similar_profiles(assessment_vector)
    """

    MODEL_FILENAME = "ml_classifier.pkl"

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = Path(models_dir) if models_dir else Path(__file__).parent.parent / "models"
        self.is_trained = False
        self.training_accuracy: Dict[str, float] = {}
        self.cv_scores: Dict[str, float] = {}

        # The three models
        self.segment_clf  = None   # RandomForest — career segment
        self.fit_clf      = None   # GradientBoosting — course fit
        self.profile_knn  = None   # KNN — similar profile lookup
        self._profile_X   = None   # Stored training vectors for KNN lookup labels
        self._profile_y   = None

        if not SKLEARN_AVAILABLE:
            print("[HybridML] ⚠ scikit-learn not available — ML layer disabled.")

    # ── Training ────────────────────────────────────────────────

    def train(self, force: bool = False, verbose: bool = True) -> Dict[str, float]:
        """
        Trains all three models on synthetically generated career data.

        Returns dict of model accuracies (useful for viva / report).
        Training takes ~15-30 seconds.
        """
        if not SKLEARN_AVAILABLE:
            return {}

        if self.is_trained and not force:
            return self.training_accuracy

        if verbose:
            print("\n" + "="*60)
            print("   PathFinder+ — Hybrid ML Layer Training")
            print("="*60)

        # ── 1. Career Segment Classifier (Random Forest) ──────────
        if verbose: print("\n[1/3] Training Career Segment Classifier (Random Forest)...")
        X_seg, y_seg = _generate_training_data(n_samples=2500)
        X_tr, X_te, y_tr, y_te = train_test_split(X_seg, y_seg, test_size=0.2, random_state=42, stratify=y_seg)

        self.segment_clf = RandomForestClassifier(
            n_estimators=200,       # 200 trees for stable predictions
            max_depth=8,
            min_samples_split=4,
            min_samples_leaf=2,
            class_weight="balanced",  # handles imbalanced segments
            random_state=42,
            n_jobs=-1
        )
        self.segment_clf.fit(X_tr, y_tr)
        seg_acc = accuracy_score(y_te, self.segment_clf.predict(X_te))
        seg_cv  = cross_val_score(self.segment_clf, X_seg, y_seg, cv=5, scoring="accuracy").mean()

        if verbose:
            print(f"   ✓ Accuracy : {seg_acc:.1%}  |  CV (5-fold): {seg_cv:.1%}")
            print(f"   Features  : [exp_yrs, resp_band, status, prob_solving, adaptability, edu, budget, time]")

        self.training_accuracy["segment_rf"] = round(seg_acc, 4)
        self.cv_scores["segment_rf"] = round(seg_cv, 4)

        # ── 2. Course Fit Ranker (Gradient Boosting) ──────────────
        if verbose: print("\n[2/3] Training Course Fit Ranker (Gradient Boosting)...")
        X_fit, y_fit = _generate_course_fit_data(n_samples=2000)
        X_tr2, X_te2, y_tr2, y_te2 = train_test_split(X_fit, y_fit, test_size=0.2, random_state=42)

        self.fit_clf = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=4,
            min_samples_split=5,
            subsample=0.85,         # stochastic GB for better generalisation
            random_state=42
        )
        self.fit_clf.fit(X_tr2, y_tr2)
        fit_acc = accuracy_score(y_te2, self.fit_clf.predict(X_te2))
        fit_cv  = cross_val_score(self.fit_clf, X_fit, y_fit, cv=5, scoring="accuracy").mean()

        if verbose:
            print(f"   ✓ Accuracy : {fit_acc:.1%}  |  CV (5-fold): {fit_cv:.1%}")
            print(f"   Features  : [segment, course_level, sbert_score, exp_yrs, band, edu, budget]")

        self.training_accuracy["fit_gbm"] = round(fit_acc, 4)
        self.cv_scores["fit_gbm"] = round(fit_cv, 4)

        # ── 3. Similar Profile Finder (KNN) ───────────────────────
        if verbose: print("\n[3/3] Training Profile Similarity Matcher (KNN, k=5)...")
        # KNN trained on segment features — used to find nearest neighbours at inference
        self.profile_knn = KNeighborsClassifier(
            n_neighbors=5,
            metric="euclidean",
            weights="distance"      # closer profiles have more influence
        )
        self.profile_knn.fit(X_seg, y_seg)
        self._profile_X = X_seg
        self._profile_y = y_seg
        knn_acc = cross_val_score(self.profile_knn, X_seg, y_seg, cv=5, scoring="accuracy").mean()

        if verbose:
            print(f"   ✓ CV Accuracy : {knn_acc:.1%}  |  k=5, metric=euclidean")

        self.training_accuracy["profile_knn"] = round(knn_acc, 4)
        self.cv_scores["profile_knn"] = round(knn_acc, 4)

        self.is_trained = True

        if verbose:
            print("\n" + "─"*60)
            print(f"   Segment RF  : {self.training_accuracy['segment_rf']:.1%} accuracy")
            print(f"   Course GBM  : {self.training_accuracy['fit_gbm']:.1%} accuracy")
            print(f"   Profile KNN : {self.training_accuracy['profile_knn']:.1%} CV accuracy")
            print("─"*60 + "\n")

        return self.training_accuracy

    # ── Inference ────────────────────────────────────────────────

    def predict_segment(self, assessment_vector: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts the career segment for a user's assessment vector.

        Returns:
            {
                "segment":    "Senior",          # one of CAREER_SEGMENTS
                "segment_id": 3,                 # 0-4
                "confidence": 0.89,              # max class probability
                "all_probs":  {...}              # probability for each segment
            }
        """
        if not self.is_trained or not SKLEARN_AVAILABLE:
            # Rule-based fallback (same as current engine)
            exp    = assessment_vector.get("experience_years", 0)
            status = assessment_vector.get("status_level", 0)
            if exp == 0 and status <= 1: return {"segment": "Entry",        "segment_id": 0, "confidence": 1.0}
            if exp <= 4 and status <= 2: return {"segment": "Graduate",     "segment_id": 1, "confidence": 1.0}
            if exp <= 8:                 return {"segment": "Professional",  "segment_id": 2, "confidence": 1.0}
            if exp <= 12:                return {"segment": "Senior",        "segment_id": 3, "confidence": 1.0}
            return {"segment": "Executive", "segment_id": 4, "confidence": 1.0}

        features = vector_to_features(assessment_vector).reshape(1, -1)
        pred_id  = int(self.segment_clf.predict(features)[0])
        probs    = self.segment_clf.predict_proba(features)[0]

        return {
            "segment":    CAREER_SEGMENTS[pred_id],
            "segment_id": pred_id,
            "confidence": round(float(probs[pred_id]), 3),
            "all_probs":  {seg: round(float(p), 3) for seg, p in zip(CAREER_SEGMENTS, probs)}
        }

    def score_course_fit(
        self,
        assessment_vector: Dict[str, Any],
        course_level: str,
        sbert_score: float,
        segment_id: Optional[int] = None
    ) -> float:
        """
        Returns a HYBRID score combining SBERT semantic similarity with
        the GBM structural fit prediction.

        Formula: hybrid = 0.60 * sbert_score + 0.40 * ml_fit_probability

        Args:
            assessment_vector: Processed assessment dict
            course_level:      e.g. "Postgraduate", "Academic (Degree)"
            sbert_score:       Raw cosine similarity from SentenceTransformer
            segment_id:        Optional pre-computed segment (avoids recompute)

        Returns:
            float: hybrid score in [0, 1]
        """
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return float(sbert_score)  # fall back to pure SBERT if not trained

        if segment_id is None:
            seg_result = self.predict_segment(assessment_vector)
            segment_id = seg_result["segment_id"]

        course_level_num = COURSE_LEVEL_ENCODING.get(course_level, 1)
        features = vector_to_features(assessment_vector)
        fit_features = np.array([[
            segment_id,
            course_level_num,
            float(sbert_score),
            float(features[0]),   # exp_years
            float(features[1]),   # band
            float(features[5]),   # education
            float(features[6]),   # budget
        ]])

        fit_proba  = float(self.fit_clf.predict_proba(fit_features)[0][1])  # P(good fit)
        hybrid     = 0.60 * float(sbert_score) + 0.40 * fit_proba

        return round(hybrid, 4)

    def find_similar_profiles(
        self,
        assessment_vector: Dict[str, Any],
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Finds the top_n most similar career profiles to the user's assessment.
        Returns human-readable labels useful for UI ("People like you went into…").

        Returns:
            List of dicts: [{"segment": "Professional", "distance": 0.23}, ...]
        """
        if not self.is_trained or self._profile_X is None or not SKLEARN_AVAILABLE:
            return []

        features = vector_to_features(assessment_vector).reshape(1, -1)
        distances, indices = self.profile_knn.kneighbors(features, n_neighbors=top_n)

        results = []
        seen = set()
        for dist, idx in zip(distances[0], indices[0]):
            seg_label = CAREER_SEGMENTS[int(self._profile_y[idx])]
            if seg_label not in seen:
                results.append({
                    "segment":  seg_label,
                    "distance": round(float(dist), 3),
                    "note":     f"Similar profile in the '{seg_label}' career band"
                })
                seen.add(seg_label)

        return results[:top_n]

    # ── Persistence ──────────────────────────────────────────────

    def save(self, path: Optional[Path] = None) -> Path:
        """Saves all trained models to a single .pkl file."""
        save_path = Path(path) if path else self.models_dir / self.MODEL_FILENAME
        save_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "segment_clf":       self.segment_clf,
            "fit_clf":           self.fit_clf,
            "profile_knn":       self.profile_knn,
            "_profile_X":        self._profile_X,
            "_profile_y":        self._profile_y,
            "training_accuracy": self.training_accuracy,
            "cv_scores":         self.cv_scores,
            "is_trained":        self.is_trained,
        }
        with open(save_path, "wb") as f:
            pickle.dump(payload, f)

        print(f"[HybridML] ✓ Models saved → {save_path}")
        return save_path

    def load(self, path: Optional[Path] = None) -> bool:
        """
        Loads pre-trained models from .pkl.
        Returns True if successful, False if file not found (triggers retrain).
        """
        load_path = Path(path) if path else self.models_dir / self.MODEL_FILENAME

        if not load_path.exists():
            return False

        try:
            with open(load_path, "rb") as f:
                payload = pickle.load(f)

            self.segment_clf       = payload["segment_clf"]
            self.fit_clf           = payload["fit_clf"]
            self.profile_knn       = payload["profile_knn"]
            self._profile_X        = payload["_profile_X"]
            self._profile_y        = payload["_profile_y"]
            self.training_accuracy = payload.get("training_accuracy", {})
            self.cv_scores         = payload.get("cv_scores", {})
            self.is_trained        = payload.get("is_trained", True)

            return True
        except Exception as e:
            print(f"[HybridML] ⚠ Load failed ({e}) — will retrain.")
            return False

    def __repr__(self) -> str:
        if not self.is_trained:
            return "HybridMLLayer(not trained)"
        acc = self.training_accuracy
        return (
            f"HybridMLLayer("
            f"RF={acc.get('segment_rf', 0):.1%}, "
            f"GBM={acc.get('fit_gbm', 0):.1%}, "
            f"KNN={acc.get('profile_knn', 0):.1%})"
        )


# ─────────────────────────────────────────────────────────────
#  Quick standalone test
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ml = HybridMLLayer()

    # Test training
    accuracies = ml.train(verbose=True)
    ml.save()

    # Test with a realistic assessment vector
    test_vectors = [
        {
            "name": "Fresh Graduate (BSc CS, 0 yrs)",
            "vector": {"experience_years": 0, "responsibility_band": 0, "status_level": 1,
                       "problem_solving_score": 2, "adaptability_score": 1,
                       "highest_education": "Bachelor's Degree", "budget_category": "50k-200k",
                       "time_commitment": "20+ hours"}
        },
        {
            "name": "Senior Manager (MSc, 8 yrs)",
            "vector": {"experience_years": 8, "responsibility_band": 3, "status_level": 2,
                       "problem_solving_score": 3, "adaptability_score": 3,
                       "highest_education": "Master's / PhD", "budget_category": "500k+",
                       "time_commitment": "5-10 hours"}
        },
        {
            "name": "Career Switcher (BSc, 4 yrs in diff field)",
            "vector": {"experience_years": 4, "responsibility_band": 2, "status_level": 3,
                       "problem_solving_score": 2, "adaptability_score": 3,
                       "highest_education": "Bachelor's Degree", "budget_category": "200k-500k",
                       "time_commitment": "10-20 hours"}
        }
    ]

    print("\n── Inference Tests ──")
    for t in test_vectors:
        seg = ml.predict_segment(t["vector"])
        hybrid_postgrad = ml.score_course_fit(t["vector"], "Postgraduate", 0.75, seg["segment_id"])
        hybrid_diploma  = ml.score_course_fit(t["vector"], "Academic (Diploma)", 0.75, seg["segment_id"])
        print(f"\n{t['name']}")
        print(f"  Segment   : {seg['segment']} (confidence: {seg['confidence']:.1%})")
        print(f"  Postgrad  : hybrid={hybrid_postgrad:.3f}  vs SBERT=0.750")
        print(f"  Diploma   : hybrid={hybrid_diploma:.3f}  vs SBERT=0.750")
        similar = ml.find_similar_profiles(t["vector"])
        print(f"  Similar   : {[s['segment'] for s in similar]}")
