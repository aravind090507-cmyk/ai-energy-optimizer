"""
ml_engine.py
Machine Learning engine for:
1. Load Forecasting
2. Anomaly Detection
3. Usage Classification
"""

import numpy as np

from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier,
    GradientBoostingRegressor,
    GradientBoostingClassifier,
    IsolationForest
)
from sklearn.svm import OneClassSVM

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc
)

FEATURES = [
    "hour",
    "day_of_week",
    "is_weekend",
    "peak_hour_flag",
    "voltage",
    "global_intensity"
]


class EnergyMLEngine:

    def __init__(self):

        # Forecasters
        self.rf_reg = RandomForestRegressor(
            n_estimators=10,
            max_depth=6,
            random_state=42,
            n_jobs=1
        )
        self.gb_reg = GradientBoostingRegressor(
            n_estimators=15,
            max_depth=4,
            random_state=42
        )

        # Classifiers
        self.rf_clf = RandomForestClassifier(
            n_estimators=10,
            max_depth=6,
            random_state=42,
            n_jobs=1
        )
        self.gb_clf = GradientBoostingClassifier(
            n_estimators=15,
            max_depth=4,
            random_state=42
        )

        # Anomaly Detectors
        self.iso_forest = IsolationForest(
            contamination=0.03,
            random_state=42
        )
        self.oc_svm = OneClassSVM(
            nu=0.03,
            kernel='rbf',
            gamma='scale'
        )

        # Active Model References
        self.active_reg_model = self.rf_reg
        self.active_reg_name = "Random Forest Regressor"
        self.active_reg_rmse = 0.15

        self.active_clf_model = self.rf_clf
        self.active_clf_name = "Random Forest Classifier"

        self.active_iso_model = self.iso_forest
        self.active_iso_name = "Isolation Forest"
        self.active_iso_scaled = False

    # -----------------------------
    # Forecasting
    # -----------------------------
    def train_forecaster(self, df):

        X = df[FEATURES]

        y = df["global_active_power"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        # Train Random Forest Regressor
        self.rf_reg.fit(X_train, y_train)
        rf_predictions = self.rf_reg.predict(X_test)
        rf_metrics = {
            "r2": round(r2_score(y_test, rf_predictions), 4),
            "mae": round(mean_absolute_error(y_test, rf_predictions), 4),
            "rmse": round(np.sqrt(mean_squared_error(y_test, rf_predictions)), 4)
        }

        # Train Gradient Boosting Regressor
        self.gb_reg.fit(X_train, y_train)
        gb_predictions = self.gb_reg.predict(X_test)
        gb_metrics = {
            "r2": round(r2_score(y_test, gb_predictions), 4),
            "mae": round(mean_absolute_error(y_test, gb_predictions), 4),
            "rmse": round(np.sqrt(mean_squared_error(y_test, gb_predictions)), 4)
        }

        # Select Best Model
        if gb_metrics["r2"] > rf_metrics["r2"]:
            self.active_reg_model = self.gb_reg
            self.active_reg_name = "Gradient Boosting Regressor"
            self.active_reg_rmse = gb_metrics["rmse"]
        else:
            self.active_reg_model = self.rf_reg
            self.active_reg_name = "Random Forest Regressor"
            self.active_reg_rmse = rf_metrics["rmse"]

        metrics = {
            "rf": rf_metrics,
            "gb": gb_metrics,
            "active": self.active_reg_name
        }

        print("\n========== FORECAST MODEL METRICS ==========")
        print(f"Random Forest - R2: {rf_metrics['r2']}, RMSE: {rf_metrics['rmse']}")
        print(f"Gradient Boosting - R2: {gb_metrics['r2']}, RMSE: {gb_metrics['rmse']}")
        print(f"Active Forecaster: {self.active_reg_name}")
        print("============================================\n")

        return metrics

    # -----------------------------
    # Anomaly Detection
    # -----------------------------
    def detect_anomalies(self, df):

        cols = [
            "global_active_power",
            "voltage",
            "global_intensity",
            "hour"
        ]

        # Train Isolation Forest
        self.iso_forest.fit(df[cols])
        if_preds = self.iso_forest.predict(df[cols])
        if_anomalies = (if_preds == -1).astype(int)

        # Train One-Class SVM
        svm_cols = ["global_active_power", "global_intensity"]
        scaled_svm = (df[svm_cols] - df[svm_cols].mean()) / (df[svm_cols].std() + 1e-8)
        self.oc_svm.fit(scaled_svm)
        svm_preds = self.oc_svm.predict(scaled_svm)
        svm_anomalies = (svm_preds == -1).astype(int)

        # Evaluate against IQR-based outliers
        y_true = df["is_outlier"].values

        # Isolation Forest Metrics & Confusion Matrix
        if_acc = accuracy_score(y_true, if_anomalies)
        if_prec = precision_score(y_true, if_anomalies, zero_division=0)
        if_rec = recall_score(y_true, if_anomalies, zero_division=0)
        if_f1 = f1_score(y_true, if_anomalies, zero_division=0)
        if_cm = confusion_matrix(y_true, if_anomalies).tolist()

        # One-Class SVM Metrics & Confusion Matrix
        svm_acc = accuracy_score(y_true, svm_anomalies)
        svm_prec = precision_score(y_true, svm_anomalies, zero_division=0)
        svm_rec = recall_score(y_true, svm_anomalies, zero_division=0)
        svm_f1 = f1_score(y_true, svm_anomalies, zero_division=0)
        svm_cm = confusion_matrix(y_true, svm_anomalies).tolist()

        # ROC Curve & AUC computation
        # Isolation Forest decision scores
        if_scores = -self.iso_forest.score_samples(df[cols])
        if_fpr, if_tpr, _ = roc_curve(y_true, if_scores)
        if_auc = float(auc(if_fpr, if_tpr))

        # One-Class SVM decision scores
        svm_scores = -self.oc_svm.score_samples(scaled_svm)
        svm_fpr, svm_tpr, _ = roc_curve(y_true, svm_scores)
        svm_auc = float(auc(svm_fpr, svm_tpr))

        # Downsample ROC curve data to a 100-point grid for optimized API payload and smooth drawing
        fpr_grid = np.linspace(0, 1, 100)
        if_tpr_interp = np.interp(fpr_grid, if_fpr, if_tpr)
        svm_tpr_interp = np.interp(fpr_grid, svm_fpr, svm_tpr)

        roc_curve_points = []
        for f, t_if, t_svm in zip(fpr_grid, if_tpr_interp, svm_tpr_interp):
            roc_curve_points.append({
                "fpr": round(float(f), 3),
                "if_tpr": round(float(t_if), 3),
                "svm_tpr": round(float(t_svm), 3)
            })

        # Select Best Model
        if svm_f1 > if_f1:
            self.active_iso_model = self.oc_svm
            self.active_iso_name = "One-Class SVM"
            self.active_iso_scaled = True
            active_anomalies = svm_anomalies
        else:
            self.active_iso_model = self.iso_forest
            self.active_iso_name = "Isolation Forest"
            self.active_iso_scaled = False
            active_anomalies = if_anomalies

        result = df.copy()
        result["is_anomaly"] = active_anomalies
        result["anomaly_score"] = 0
        result["anomaly_reason"] = np.where(
            result["is_anomaly"] == 1,
            "Unusual power usage",
            "Normal"
        )

        self.anomaly_metrics = {
            "if": {
                "accuracy": round(float(if_acc), 4),
                "precision": round(float(if_prec), 4),
                "recall": round(float(if_rec), 4),
                "f1": round(float(if_f1), 4),
                "total_anomalies": int(np.sum(if_anomalies)),
                "confusion_matrix": if_cm,
                "auc": round(if_auc, 4)
            },
            "svm": {
                "accuracy": round(float(svm_acc), 4),
                "precision": round(float(svm_prec), 4),
                "recall": round(float(svm_rec), 4),
                "f1": round(float(svm_f1), 4),
                "total_anomalies": int(np.sum(svm_anomalies)),
                "confusion_matrix": svm_cm,
                "auc": round(svm_auc, 4)
            },
            "active": self.active_iso_name,
            "roc_curve": roc_curve_points
        }

        print("\n========== ANOMALY DETECTION MODEL METRICS ==========")
        print(f"Isolation Forest - Accuracy: {self.anomaly_metrics['if']['accuracy']}, F1: {self.anomaly_metrics['if']['f1']}")
        print(f"One-Class SVM - Accuracy: {self.anomaly_metrics['svm']['accuracy']}, F1: {self.anomaly_metrics['svm']['f1']}")
        print(f"Active Anomaly Detector: {self.active_iso_name}")
        print("======================================================\n")

        return result

    # -----------------------------
    # Usage Classification
    # -----------------------------
    def train_classifier(self, df):

        q1 = df["global_active_power"].quantile(0.33)
        q2 = df["global_active_power"].quantile(0.66)

        def classify(power):

            if power <= q1:
                return "Low"

            elif power <= q2:
                return "Medium"

            return "High"

        y = df["global_active_power"].apply(
            classify
        )

        X = df[FEATURES]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        # Train Random Forest Classifier
        self.rf_clf.fit(X_train, y_train)
        rf_preds = self.rf_clf.predict(X_test)
        rf_cm = confusion_matrix(y_test, rf_preds, labels=["Low", "Medium", "High"]).tolist()
        rf_metrics = {
            "accuracy": round(accuracy_score(y_test, rf_preds), 4),
            "precision": round(float(precision_score(y_test, rf_preds, average="macro", zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, rf_preds, average="macro", zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, rf_preds, average="macro", zero_division=0)), 4),
            "confusion_matrix": rf_cm
        }

        # Train Gradient Boosting Classifier
        self.gb_clf.fit(X_train, y_train)
        gb_preds = self.gb_clf.predict(X_test)
        gb_cm = confusion_matrix(y_test, gb_preds, labels=["Low", "Medium", "High"]).tolist()
        gb_metrics = {
            "accuracy": round(accuracy_score(y_test, gb_preds), 4),
            "precision": round(float(precision_score(y_test, gb_preds, average="macro", zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, gb_preds, average="macro", zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, gb_preds, average="macro", zero_division=0)), 4),
            "confusion_matrix": gb_cm
        }

        # Select Best Model
        if gb_metrics["accuracy"] > rf_metrics["accuracy"]:
            self.active_clf_model = self.gb_clf
            self.active_clf_name = "Gradient Boosting Classifier"
        else:
            self.active_clf_model = self.rf_clf
            self.active_clf_name = "Random Forest Classifier"

        # Calculate One-vs-Rest Multiclass ROC Curve & AUC for the Active Model
        probs = self.active_clf_model.predict_proba(X_test)
        class_to_idx = {cls: idx for idx, cls in enumerate(self.active_clf_model.classes_)}
        fpr_grid = np.linspace(0, 1, 100)

        # Low vs Rest
        low_idx = class_to_idx["Low"]
        low_fpr, low_tpr, _ = roc_curve((y_test == "Low").astype(int), probs[:, low_idx])
        low_auc = float(auc(low_fpr, low_tpr))
        low_tpr_interp = np.interp(fpr_grid, low_fpr, low_tpr)

        # Medium vs Rest
        med_idx = class_to_idx["Medium"]
        med_fpr, med_tpr, _ = roc_curve((y_test == "Medium").astype(int), probs[:, med_idx])
        med_auc = float(auc(med_fpr, med_tpr))
        med_tpr_interp = np.interp(fpr_grid, med_fpr, med_tpr)

        # High vs Rest
        high_idx = class_to_idx["High"]
        high_fpr, high_tpr, _ = roc_curve((y_test == "High").astype(int), probs[:, high_idx])
        high_auc = float(auc(high_fpr, high_tpr))
        high_tpr_interp = np.interp(fpr_grid, high_fpr, high_tpr)

        roc_curve_points = []
        for i, f in enumerate(fpr_grid):
            roc_curve_points.append({
                "fpr": round(float(f), 3),
                "low_tpr": round(float(low_tpr_interp[i]), 3),
                "med_tpr": round(float(med_tpr_interp[i]), 3),
                "high_tpr": round(float(high_tpr_interp[i]), 3)
            })

        auc_values = {
            "low": round(low_auc, 4),
            "med": round(med_auc, 4),
            "high": round(high_auc, 4)
        }

        metrics = {
            "rf": rf_metrics,
            "gb": gb_metrics,
            "active": self.active_clf_name,
            "roc_curve": roc_curve_points,
            "auc": auc_values
        }

        print("\n========== CLASSIFIER MODEL METRICS ==========")
        print(f"Random Forest - Accuracy: {rf_metrics['accuracy']}, F1: {rf_metrics['f1']}")
        print(f"Gradient Boosting - Accuracy: {gb_metrics['accuracy']}, F1: {gb_metrics['f1']}")
        print(f"Active Classifier: {self.active_clf_name}")
        print("==============================================\n")

        return metrics

    # -----------------------------
    # Prediction API
    # -----------------------------
    def predict_load(self, df):

        return self.active_reg_model.predict(
            df[FEATURES]
        )

    def classify(self, df):

        return self.active_clf_model.predict(
            df[FEATURES]
        )