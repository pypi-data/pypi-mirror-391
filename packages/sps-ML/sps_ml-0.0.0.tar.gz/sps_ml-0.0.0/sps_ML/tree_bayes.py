import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.naive_bayes import CategoricalNB, GaussianNB
from sklearn.preprocessing import OrdinalEncoder
from .utils import print_evaluation_metrics

def run_toy_dataset_demo():
    """
    Implements Decision Tree and Naive Bayes on the 'Buys_Computer' toy dataset.
    """
    print("\n" + "="*50)
    print("--- Running Toy Dataset Demo (Decision Tree & Naive Bayes) ---")
    print("="*50)
    
    # 1. Create the toy dataset
    data = {
        'age': ['<=30', '<=30', '31-40', '>40', '>40', '>40', '31-40', '<=30', '<=30', '>40', '<=30', '31-40', '31-40', '>40'],
        'income': ['high', 'high', 'high', 'medium', 'low', 'low', 'low', 'medium', 'low', 'medium', 'medium', 'medium', 'high', 'medium'],
        'student': ['no', 'no', 'no', 'no', 'yes', 'yes', 'yes', 'no', 'yes', 'yes', 'yes', 'no', 'yes', 'no'],
        'credit_rating': ['fair', 'excellent', 'fair', 'fair', 'fair', 'excellent', 'excellent', 'fair', 'fair', 'fair', 'excellent', 'excellent', 'fair', 'excellent'],
        'buys_computer': ['no', 'no', 'yes', 'yes', 'yes', 'no', 'yes', 'no', 'yes', 'yes', 'yes', 'yes', 'yes', 'no']
    }
    df = pd.DataFrame(data)
    
    # 2. Preprocess the data
    X = df.drop('buys_computer', axis=1)
    y = df['buys_computer']
    
    # Use OrdinalEncoder to convert categorical features to numbers
    encoder = OrdinalEncoder()
    X_encoded = encoder.fit_transform(X)
    
    # 3. Decision Tree
    print("\n--- Decision Tree Demo ---")
    dt = DecisionTreeClassifier(criterion='entropy', random_state=42)
    dt.fit(X_encoded, y)
    
    print("Decision Tree Structure (Text-based):")
    tree_rules = export_text(dt, feature_names=list(X.columns))
    print(tree_rules)
    print("\nInference: The tree splits data based on features that provide the most information gain (lowest entropy).")

    # 4. Naive Bayes
    print("\n--- Naive Bayes Demo (Categorical) ---")
    nb = CategoricalNB()
    nb.fit(X_encoded, y)
    
    # Test a new sample: [age='<=30', income='medium', student='yes', credit_rating='fair']
    test_sample_raw = [['<=30', 'medium', 'yes', 'fair']]
    test_sample_encoded = encoder.transform(test_sample_raw)
    
    prediction = nb.predict(test_sample_encoded)
    probabilities = nb.predict_proba(test_sample_encoded)
    
    print(f"Test Sample: {test_sample_raw[0]}")
    print(f"Prediction: {prediction[0]}")
    print(f"Probabilities (no, yes): {probabilities[0]}")
    print("\nInference: Naive Bayes calculates the probability of each class given the features,")
    print("assuming features are 'naively' (independently) conditional on the class.")

def run_real_data_demo(X_train, y_train, X_test, y_test, class_names):
    """
    Runs Decision Tree and Gaussian Naive Bayes on a real dataset.
    """
    print("\n--- Running DT & GNB on Real Dataset ---")
    
    models = {
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Gaussian Naive Bayes": GaussianNB()
    }

    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print_evaluation_metrics(y_test, y_pred, title=name, class_names=class_names)