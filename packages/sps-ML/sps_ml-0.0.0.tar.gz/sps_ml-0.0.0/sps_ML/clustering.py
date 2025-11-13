from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

def run_clustering(X_processed, n_clusters_guess):
    
    
    print("\n" + "="*50)
    print("--- Running Clustering Algorithms (Unsupervised) ---")
    print("="*50)
    

    X_sub = X_processed


    print("\n--- K-Means ---")

    print("Running Elbow Method to find optimal k...")
    sse = []
    k_range = range(2, 11)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_sub)
        sse.append(kmeans.inertia_)
    
    plt.figure(figsize=(10, 6))
    plt.plot(k_range, sse, 'bo-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Sum of Squared Errors (SSE)')
    plt.title('K-Means Elbow Method')
    plt.show()
    print(f"Elbow plot generated. Choose the 'k' at the 'elbow' (bend) of the curve.")


    print(f"\nRunning K-Means with k={n_clusters_guess} (from target classes)...")
    kmeans = KMeans(n_clusters=n_clusters_guess, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(X_sub)
    
    silhouette_avg = silhouette_score(X_sub, kmeans_labels)
    print(f"K-Means (k={n_clusters_guess}) Cluster Distribution: {Counter(kmeans_labels)}")
    print(f"Silhouette Score: {silhouette_avg:.4f}")
    print("Inference: Silhouette Score (near 1 is good) measures cluster separation.")

    # 2. DBSCAN
    print("\n--- DBSCAN ---")


    dbscan = DBSCAN(eps=2.0, min_samples=10, n_jobs=-1)
    dbscan_labels = dbscan.fit_predict(X_sub)
    
    n_clusters_db = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
    n_noise = list(dbscan_labels).count(-1)
    
    print(f"DBSCAN found {n_clusters_db} clusters and {n_noise} noise points (label -1).")
    print(f"DBSCAN Cluster Distribution: {Counter(dbscan_labels)}")
    print("Inference: DBSCAN is density-based and finds arbitrarily shaped clusters.")
    print("It is excellent at identifying outliers (noise).")