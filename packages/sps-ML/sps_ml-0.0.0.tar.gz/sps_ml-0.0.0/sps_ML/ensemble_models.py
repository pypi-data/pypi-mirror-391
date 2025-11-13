from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    BaggingClassifier,
    ExtraTreesClassifier
)
from lightgbm import LGBMClassifier
from .utils import print_evaluation_metrics
import time

def run_ensemble_models(X_train, y_train, X_test, y_test, class_names):
    
    print("\n" + "="*50)
    print("--- Running Ensemble Learning Algorithms ---")
    print("="*50)

    models = {
        "Random Forest": RandomForestClassifier(
            random_state=42, n_jobs=-1, n_estimators=100
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            random_state=42, n_estimators=100
        ),
        "AdaBoost": AdaBoostClassifier(
            random_state=42, n_estimators=100
        ),
        "Bagging": BaggingClassifier(
            random_state=42, n_estimators=100, n_jobs=-1
        ),
        "Extra Trees": ExtraTreesClassifier(
            random_state=42, n_jobs=-1, n_estimators=100
        ),
        "LightGBM": LGBMClassifier(
            random_state=42, n_estimators=100, n_jobs=-1
        ),
    }

    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        start_time = time.time()
        model.fit(X_train, y_train)
        end_time = time.time()
        print(f"Training completed in {end_time - start_time:.2f} seconds.")
        
        y_pred = model.predict(X_test)
        print_evaluation_metrics(y_test, y_pred, title=name, class_names=class_names)
