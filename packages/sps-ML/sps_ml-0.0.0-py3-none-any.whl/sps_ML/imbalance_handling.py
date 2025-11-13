'''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from collections import Counter

# Import models
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.dummy import DummyClassifier

# Import metrics and utils
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import label_binarize
from .utils import get_full_metrics

def run_imbalance_experiment(X_train, y_train, X_test, y_test, label_encoder):
    """
    Runs the full experiment comparing class imbalance techniques.
    """
    print("\n" + "="*50)
    print("=== STARTING CLASS IMBALANCE EXPERIMENT ===")
    print("="*50 + "\n")
    
    class_names = label_encoder.classes_
    
    # --- 1. Define Classifiers ---
    # Using 4 classifiers + 1 ensemble
    classifiers = {
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Naive Bayes": GaussianNB(),
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000, multi_class='auto', n_jobs=-1),
        "Random Forest (Ensemble)": RandomForestClassifier(random_state=42, n_jobs=-1, n_estimators=50) # Fewer trees for speed
    }
    
    # --- 2. Define Sampling Techniques ---
    techniques = {
        "Baseline (No Sampling)": ImbPipeline(steps=[
            ('model', DummyClassifier()) # Placeholder
        ]),
        "Random Under-Sampling": ImbPipeline(steps=[
            ('sampler', RandomUnderSampler(random_state=42)),
            ('model', DummyClassifier())
        ]),
        "Random Over-Sampling": ImbPipeline(steps=[
            ('sampler', RandomOverSampler(random_state=42)),
            ('model', DummyClassifier())
        ]),
        "SMOTE (Over-Sampling)": ImbPipeline(steps=[
            ('sampler', SMOTE(random_state=42, n_jobs=-1)),
            ('model', DummyClassifier())
        ])
    }
    
    # --- 3. Run Pipeline Experiments ---
    results = {}

    for tech_name, pipeline in techniques.items():
        print(f"\n\n{'='*20} TESTING TECHNIQUE: {tech_name} {'='*20}")
        
        for model_name, model in classifiers.items():
            
            full_title = f"{model_name} with {tech_name}"
            full_pipeline = ImbPipeline(steps=pipeline.steps[:-1] + [('model', model)])
            
            print(f"\nTraining {full_title}...")
            start_time = time.time()
            
            full_pipeline.fit(X_train, y_train)
            y_pred = full_pipeline.predict(X_test)
            try:
                y_prob = full_pipeline.predict_proba(X_test)
            except AttributeError:
                y_prob = label_binarize(y_pred, classes=np.unique(y_train))
                if y_prob.shape[1] == 1 and len(class_names) == 2: # Handle binary case
                    y_prob = np.hstack((1 - y_prob, y_prob))

            end_time = time.time()
            print(f"Training/Prediction took {end_time - start_time:.2f} seconds.")

            # Overfitting/Underfitting Check
            train_score = full_pipeline.score(X_train, y_train)
            test_score = accuracy_score(y_test, y_pred)
            print(f"  - Train Accuracy: {train_score:.4f} | Test Accuracy: {test_score:.4f}")
            if train_score > (test_score + 0.15):
                print("  - WARNING: Potential OVERFITTING detected.")
            
            # Store and Print Metrics
            get_full_metrics(y_test, y_pred, y_prob, full_title, class_names)
            results[full_title] = {'F1 (Macro)': f1_score(y_test, y_pred, average='macro', zero_division=0)}

    # --- 4. Anomaly/Rare Event Detection Algorithms ---
    print(f"\n\n{'='*20} TESTING RARE EVENT ALGORITHMS {'='*20}")
    
    try:
        # Find the 'normal' class label. This is a common heuristic.
        # Assumes 'Benign' or the majority class is 'normal'.
        normal_label_str = Counter(label_encoder.inverse_transform(y_train)).most_common(1)[0][0]
        normal_label_int = label_encoder.transform([normal_label_str])[0]
        print(f"Anomaly Detection: Using '{normal_label_str}' (ID: {normal_label_int}) as the 'normal' class.")
        
        X_train_normal = X_train[y_train == normal_label_int]
        # Binary target: 0 for normal, 1 for anomaly
        y_test_binary = (y_test != normal_label_int).astype(int)

        anomaly_models = {
            "One-Class SVM": OneClassSVM(gamma='auto', nu=0.01), # nu = expected fraction of anomalies
            "Isolation Forest": IsolationForest(contamination='auto', random_state=42, n_jobs=-1)
        }

        for name, model in anomaly_models.items():
            print(f"\nTraining {name}...")
            if name == "One-Class SVM":
                model.fit(X_train_normal) # Train *only* on normal data
            else:
                model.fit(X_train) # Isolation Forest trains on all data
            
            # Predict: +1 for inlier (normal), -1 for outlier (anomaly)
            y_pred_raw = model.predict(X_test)
            y_pred_binary = (y_pred_raw == -1).astype(int) # Convert to 0/1
            
            # Dummy prob
            y_prob_binary = label_binarize(y_pred_binary, classes=[0,1])
            y_prob_binary = np.hstack((1 - y_prob_binary, y_prob_binary))

            get_full_metrics(y_test_binary, y_pred_binary, y_prob_binary, name, ['Normal', 'Anomaly'])
            results[name] = {'F1 (Macro)': f1_score(y_test_binary, y_pred_binary, average='macro', zero_division=0)}

    except Exception as e:
        print(f"Could not run anomaly detection. Error: {e}")

    # --- 5. Final Comparison ---
    print("\n\n" + "="*50)
    print("=== FINAL IMBALANCE EXPERIMENT RESULTS (F1-Score Macro) ===")
    print("="*50 + "\n")
    
    results_df = pd.DataFrame.from_dict(results, orient='index')
    results_df = results_df.sort_values(by='F1 (Macro)', ascending=False)
    
    print(results_df)
    
    plt.figure(figsize=(15, 10))
    results_df['F1 (Macro)'].plot(kind='barh')
    plt.title('Comparison of Models and Sampling Techniques (Macro F1-Score)')
    plt.xlabel('F1-Score (Macro Average)')
    plt.gca().invert_yaxis()
    plt.show()'''