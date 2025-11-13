import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression, Perceptron
from .utils import plot_validation_curve

def run_overfitting_experiments(X_train, y_train):
    
    print("\n" + "="*50)
    print("--- Running Overfitting/Underfitting Experiments ---")
    print("="*50)
    print("Plotting validation curves. This may take some time...")

    
    X_sub = X_train
    y_sub = y_train

    # 1. KNN (Varying n_neighbors)
    param_range_knn = np.arange(1, 41, step=3)
    plot_validation_curve(
        KNeighborsClassifier(n_jobs=-1), 
        "Validation Curve: KNN (n_neighbors)", 
        X_sub, y_sub, 
        param_name="n_neighbors", 
        param_range=param_range_knn
    )
    
    

    # 2. Decision Tree (Varying max_depth)
    param_range_dt = np.arange(1, 21)
    plot_validation_curve(
        DecisionTreeClassifier(random_state=42),
        "Validation Curve: Decision Tree (max_depth)",
        X_sub, y_sub,
        param_name="max_depth",
        param_range=param_range_dt
    )
    
    
    
    # 3. Logistic Regression (Varying C - inverse regularization strength)
    param_range_lr = np.logspace(-3, 3, 7)
    plot_validation_curve(
        LogisticRegression(max_iter=1000, random_state=42, multi_class='auto', n_jobs=-1),
        "Validation Curve: Logistic Regression (C)",
        X_sub, y_sub,
        param_name="C",
        param_range=param_range_lr
    )
   
   
    
    # 4. Perceptron (Varying alpha - regularization)
    param_range_perc = np.logspace(-6, 1, 8)
    plot_validation_curve(
        Perceptron(max_iter=1000, tol=1e-3, random_state=42, n_jobs=-1),
        "Validation Curve: Perceptron (alpha)",
        X_sub, y_sub,
        param_name="alpha",
        param_range=param_range_perc
    )
    
    