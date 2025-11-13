from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif, RFE
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def run_feature_selection_and_reduction(X_train, y_train, X_test):
    
    
    print("\n" + "="*50)
    print("--- Running Feature Selection & Reduction ---")
    print("="*50)
    
    feature_names = X_train.columns
    
    print("\n--- Method 1: VarianceThreshold (Remove low-variance features) ---")
    selector = VarianceThreshold(threshold=0.01) # Removes features with < 1% variance
    selector.fit(X_train)
    print(f"Original features: {X_train.shape[1]}")
    print(f"Features after VarianceThreshold: {selector.get_support().sum()}")
    
    print("\n--- Method 2: SelectKBest (ANOVA F-test) ---")
    k = 20
    selector_kbest = SelectKBest(f_classif, k=k)
    X_train_kbest = selector_kbest.fit_transform(X_train, y_train)
    
    selected_indices = selector_kbest.get_support(indices=True)
    selected_features = feature_names[selected_indices]
    
    print(f"Top {k} features selected by f_classif: {selected_features.tolist()}")



    print("\n--- Method 3: RFE (Recursive Feature Elimination) ---")
    model = LogisticRegression(max_iter=100, solver='liblinear') # Fast estimator for RFE
    rfe_selector = RFE(estimator=model, n_features_to_select=k, step=0.1) # Remove 10% each step
    
    print(f"Running RFE to select {k} features... This may take a moment.")
    rfe_selector.fit(X_train, y_train)
    
    selected_rfe_indices = rfe_selector.get_support(indices=True)
    selected_rfe_features = feature_names[selected_rfe_indices]
    
    print(f"Top {k} features selected by RFE: {selected_rfe_features.tolist()}")
    print("Inference: RFE iteratively removes the weakest features, considering feature interactions via the model.")

    print("\n--- Method 4: PCA (Feature Reduction) ---")
    pca = PCA(n_components=0.95) 
    X_train_pca = pca.fit_transform(X_train)
    
    print(f"Original features: {X_train.shape[1]}")
    print(f"Features after PCA (to 95% variance): {pca.n_components_}")
    
    plt.figure(figsize=(10, 6))
    pca_full = PCA().fit(X_train)
    plt.plot(np.cumsum(pca_full.explained_variance_ratio_))
    plt.xlabel('Number of Components')
    plt.ylabel('Cumulative Explained Variance')
    plt.title('PCA Explained Variance')
    plt.grid(True)
    plt.axhline(y=0.95, color='r', linestyle='--')
    plt.show()
    print("Inference: PCA creates new, uncorrelated features (components) that capture most of the data's variance.")

    X_train_selected = X_train[selected_rfe_features]
    X_test_selected = X_test[selected_rfe_features]
    
    return X_train_selected, X_test_selected, selected_rfe_features