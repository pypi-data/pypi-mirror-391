from sklearn.svm import SVC
from sklearn.metrics import classification_report
import numpy as np
import pandas as pd
from .utils import print_evaluation_metrics

def run_svm_classifier(X_train, y_train, X_test, y_test, class_names):
    """
    Trains and evaluates SVM with different kernels.
    Assumes scaled data.
    """
    print("\n" + "="*50)
    print("--- Running Support Vector Machine (SVM) Classifier ---")
    print("="*50)
    
    
    X_train_sub = X_train
    y_train_sub = y_train

    models = {
        "SVM (Linear Kernel)": SVC(kernel='linear', random_state=42, probability=True),
        "SVM (RBF Kernel)": SVC(kernel='rbf', random_state=42, probability=True)
    }
    
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        if "RBF" in name:
            model.fit(X_train_sub, y_train_sub)
        else:
            model.fit(X_train, y_train)
            
        y_pred = model.predict(X_test)
        print_evaluation_metrics(y_test, y_pred, title=name, class_names=class_names)
        
        