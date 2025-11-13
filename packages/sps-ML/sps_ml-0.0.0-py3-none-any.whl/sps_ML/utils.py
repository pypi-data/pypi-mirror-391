import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    ConfusionMatrixDisplay, 
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    roc_auc_score,
    roc_curve
)
from sklearn.model_selection import validation_curve
from sklearn.preprocessing import label_binarize

def print_evaluation_metrics(y_test, y_pred, title, class_names):
    """
    Prints a standard set of classification metrics and plots a confusion matrix.
    """
    print(f"\n--- Results for: {title} ---")
    
    # 1. Main Metrics
    print(f"Accuracy (Overall): {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision (Macro):  {precision_score(y_test, y_pred, average='macro', zero_division=0):.4f}")
    print(f"Recall (Macro):     {recall_score(y_test, y_pred, average='macro', zero_division=0):.4f}")
    print(f"F1-Score (Macro):   {f1_score(y_test, y_pred, average='macro', zero_division=0):.4f}")
    
    # 2. Classification Report
    print("\n--- Detailed Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=class_names, zero_division=0))
    
    # 3. Confusion Matrix Plot
    try:
        fig, ax = plt.subplots(figsize=(max(8, len(class_names)), max(8, len(class_names))))
        ConfusionMatrixDisplay.from_predictions(
            y_test, y_pred, ax=ax, 
            display_labels=class_names, 
            xticks_rotation='vertical',
            cmap='Blues'
        )
        plt.title(f"Confusion Matrix: {title}")
        plt.show()
    except Exception as e:
        print(f"Could not plot confusion matrix: {e}")

def plot_validation_curve(estimator, title, X, y, param_name, param_range, cv=5, scoring="accuracy"):
    """
    Helper function to plot a validation curve.
    """
    try:
        train_scores, test_scores = validation_curve(
            estimator, X, y, 
            param_name=param_name, 
            param_range=param_range,
            cv=cv, scoring=scoring, n_jobs=-1
        )
        
        train_scores_mean = np.mean(train_scores, axis=1)
        train_scores_std = np.std(train_scores, axis=1)
        test_scores_mean = np.mean(test_scores, axis=1)
        test_scores_std = np.std(test_scores, axis=1)

        plt.figure(figsize=(10, 6))
        plt.title(title)
        plt.xlabel(param_name)
        plt.ylabel("Score")
        plt.ylim(0.0, 1.1)
        
        # Use log scale for wide-ranging parameters (like 'C' or 'alpha')
        if np.issubdtype(param_range.dtype, np.number) and (np.max(param_range) / np.min(param_range) > 100):
             plt.semilogx(param_range, train_scores_mean, label="Training score", color="darkorange", lw=2)
        else:
            plt.plot(param_range, train_scores_mean, label="Training score", color="darkorange", lw=2)

        plt.fill_between(param_range, train_scores_mean - train_scores_std,
                         train_scores_mean + train_scores_std, alpha=0.2,
                         color="darkorange", lw=2)
        
        if np.issubdtype(param_range.dtype, np.number) and (np.max(param_range) / np.min(param_range) > 100):
            plt.semilogx(param_range, test_scores_mean, label="Cross-validation score", color="navy", lw=2)
        else:
            plt.plot(param_range, test_scores_mean, label="Cross-validation score", color="navy", lw=2)
            
        plt.fill_between(param_range, test_scores_mean - test_scores_std,
                         test_scores_mean + test_scores_std, alpha=0.2,
                         color="navy", lw=2)
        
        plt.legend(loc="best")
        plt.show()
        
    except Exception as e:
        print(f"Could not plot validation curve for {title}: {e}")

def get_full_metrics(y_test, y_pred, y_prob, title, class_names):
    """
    Prints a comprehensive set of metrics for imbalance analysis.
    """
    print(f"\n--- Results for: {title} ---")
    
    # 1. Main Metrics
    print(f"Accuracy (Overall): {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision (Macro):  {precision_score(y_test, y_pred, average='macro', zero_division=0):.4f}")
    print(f"Recall (Macro):     {recall_score(y_test, y_pred, average='macro', zero_division=0):.4f}")
    print(f"F1-Score (Macro):   {f1_score(y_test, y_pred, average='macro', zero_division=0):.4f}")
    
    # 2. Per-Class Metrics (TPR, TNR)
    print("\n--- Detailed Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=class_names, zero_division=0))
    
    cm = confusion_matrix(y_test, y_pred)
    tpr_per_class = {}
    tnr_per_class = {}
    
    for i, class_name in enumerate(class_names):
        tp = cm[i, i]
        fn = np.sum(cm[i, :]) - tp
        fp = np.sum(cm[:, i]) - tp
        tn = np.sum(cm) - (tp + fp + fn)
        
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # Recall
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0  # Specificity
        
        tpr_per_class[class_name] = tpr
        tnr_per_class[class_name] = tnr

    print("\n--- True Positive/Negative Rates ---")
    print(f"{'Class':<15} | {'TPR (Recall)':<15} | {'TNR (Specificity)':<15}")
    print("-" * 47)
    for class_name in class_names:
        print(f"{class_name:<15} | {tpr_per_class[class_name]:<15.4f} | {tnr_per_class[class_name]:<15.4f}")

    # 3. AUC Score
    try:
        n_classes = len(class_names)
        if n_classes == 2:
            auc = roc_auc_score(y_test, y_prob[:, 1])
            print(f"\nAUC (Area Under Curve): {auc:.4f}")
        else:
            auc = roc_auc_score(y_test, y_prob, multi_class='ovr', average='macro')
            print(f"\nAUC (Macro Avg, One-vs-Rest): {auc:.4f}")
    except ValueError as e:
        print(f"\nCould not calculate AUC (is y_prob available?): {e}")

    # 4. Confusion Matrix Plot
    try:
        fig, ax = plt.subplots(figsize=(max(10, n_classes), max(10, n_classes)))
        ConfusionMatrixDisplay.from_predictions(
            y_test, y_pred, ax=ax, 
            display_labels=class_names, 
            xticks_rotation='vertical',
            cmap='Blues'
        )
        plt.title(f"Confusion Matrix: {title}")
        plt.show()
    except Exception as e:
        print(f"Could not plot confusion matrix: {e}")