from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import time
from .utils import print_evaluation_metrics

def run_mlp(X_train, y_train, X_test, y_test, class_names):
   
   
    print("\n" + "="*50)
    print("--- Running Multi-Layer Perceptron (MLP) ---")
    print("="*50)
    
    # Define a simple MLP
    # (100, 50) = Two hidden layers with 100 and 50 neurons
    mlp = MLPClassifier(
        hidden_layer_sizes=(100, 50),
        max_iter=300, # Increase if it doesn't converge
        alpha=1e-4,
        solver='adam',
        verbose=False, # Set to True for convergence logs
        random_state=42,
        early_stopping=True, # Helps prevent overfitting
        n_iter_no_change=10
    )
    
    print("Training MLP... This may take some time.")
    start_time = time.time()
    mlp.fit(X_train, y_train)
    end_time = time.time()
    print(f"MLP training completed in {end_time - start_time:.2f} seconds.")

    # Evaluate
    y_pred = mlp.predict(X_test)
    
    print_evaluation_metrics(y_test, y_pred, title="MLP", class_names=class_names)
    
    # Plot loss curve
    plt.figure(figsize=(10, 6))
    plt.plot(mlp.loss_curve_)
    plt.title("MLP Loss Curve (Training)")
    plt.xlabel("Iteration")
    plt.ylabel("Loss")
    plt.show()