import numpy as np
import pandas as pd
from sklearn.linear_model import Perceptron, LogisticRegression, LinearRegression, SGDClassifier
from sklearn.metrics import classification_report, mean_squared_error
from .utils import print_evaluation_metrics

def run_linear_classification_models(X_train, y_train, X_test, y_test, class_names):
    
    models = {
        "Perceptron": Perceptron(max_iter=1000, tol=1e-3, random_state=42, n_jobs=-1),
        "Adaline (SGD)": SGDClassifier(loss='hinge', max_iter=1000, tol=1e-3, random_state=42, n_jobs=-1),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42, multi_class='auto', n_jobs=-1)
    }
    
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        print_evaluation_metrics(y_test, y_pred, title=name, class_names=class_names)
        

def run_linear_regression(X_train, y_train, X_test, y_test):
    if X_train.shape[1] > 1:
        y_reg_train = X_train.iloc[:, 0]
        y_reg_test = X_test.iloc[:, 0]
        X_reg_train = X_train.iloc[:, 1:]
        X_reg_test = X_test.iloc[:, 1:]

        model = LinearRegression(n_jobs=-1)
        model.fit(X_reg_train, y_reg_train)
        y_pred = model.predict(X_reg_test)
        
        mse = mean_squared_error(y_reg_test, y_pred)
        print(f"Mean Squared Error (dummy task): {mse:.4f}")
        print("Inference: Linear Regression models the linear relationship between features and a continuous target.")
    else:
        print("Skipping Linear Regression example: not enough features for dummy task.")