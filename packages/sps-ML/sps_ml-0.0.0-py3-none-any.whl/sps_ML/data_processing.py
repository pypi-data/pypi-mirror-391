import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import io
import warnings

# --- Main Function for Processing ---
def load_explore_preprocess(csv_path, target_column):
    
    # === 1. DATA LOADING ===
    print("--- 1. Data Loading ---")
    try:
        # Attempt to load the dataset
        df = pd.read_csv(csv_path)
        print(f"Successfully loaded data from '{csv_path}'.")
        print("\nData Head:")
        print(df.head())
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        print("Please check the FILE_PATH variable.")
        return None, None, None, None
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None, None, None, None
    
    # Handle potential infinite values which can cause errors in scalers
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    print("\n" + "="*50 + "\n")

    # === 2. DATA VISUALIZATION & EXPLORATION ===
    print("--- 2. Data Exploration & Visualization ---")
    
    # Data Shape
    print(f"\nData Shape (rows, columns): {df.shape}")
    
    # Data Info (Dtypes, Non-null counts)
    print("\nData Info (Column Types, Nulls):")
    # Use buffer to capture print output of df.info()
    buf = io.StringIO()
    df.info(buf=buf)
    print(buf.getvalue())
    
    # Descriptive Statistics for numeric columns
    print("\nDescriptive Statistics (Numeric Features):")
    print(df.describe())
    
    # Missing values count
    print("\nMissing Values per Column:")
    print(df.isnull().sum())
    
    # Target Class Visualization
    if target_column in df.columns:
        print(f"\nTarget Variable: '{target_column}'")
        print("Class Distribution (Value Counts):")
        print(df[target_column].value_counts())
        
        # Plot class distribution
        try:
            plt.figure(figsize=(10, 6))
            sns.countplot(x=target_column, data=df, order=df[target_column].value_counts().index)
            plt.title(f'Distribution of Target Class: {target_column}')
            plt.xlabel('Class')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.show()
        except Exception as e:
            print(f"Could not plot target distribution. Error: {e}")
    else:
        print(f"Error: Target column '{target_column}' not found. Cannot proceed.")
        return None, None, None, None
    
    print("\n" + "="*50 + "\n")
    
    # === 3. DATA PREPROCESSING ===
    print("--- 3. Data Preprocessing ---")
    
    # Separate features (X) and target (y)
    try:
        X = df.drop(columns=[target_column])
        y_raw = df[target_column]
    except KeyError:
        # This check is redundant if the one above passed, but good for safety
        print(f"Error: Target column '{target_column}' not found. Cannot proceed.")
        return None, None, None, None

    # Identify numeric and categorical features
    numeric_features = X.select_dtypes(include=np.number).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns

    print(f"Identified {len(numeric_features)} numeric features: {list(numeric_features)}")
    print(f"Identified {len(categorical_features)} categorical features: {list(categorical_features)}")
    
    # --- Create Preprocessing Pipelines ---
    
    # Pipeline for Numeric Features:
    # 1. Impute missing values with the median (more robust to outliers)
    # 2. Scale features to have zero mean and unit variance (simplifies computation for many models)
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # Pipeline for Categorical Features:
    # 1. Impute missing values with the most frequent value (mode)
    # 2. One-Hot Encode the features, ignoring unknown categories
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # --- Combine pipelines with ColumnTransformer ---
    # This applies the correct transformer to the correct columns
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough' # Keep any other columns we might have missed
    )

    # --- Apply the preprocessing ---
    print("\nApplying preprocessing (Imputing, Scaling, One-Hot Encoding)...")
    X_processed = preprocessor.fit_transform(X)
    
    # Get feature names after OHE for a clean DataFrame
    try:
        # Get feature names from OHE
        ohe_feature_names = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_features)
        
        # Get names of columns that were passed through
        remainder_cols = [X.columns[i] for i in preprocessor.named_transformers_['remainder']._remainder_idx]

        # Combine all feature names in order
        all_feature_names = list(numeric_features) + list(ohe_feature_names) + list(remainder_cols)
        
    except Exception as e:
        print(f"Warning: Could not get detailed feature names. Using generic names. Error: {e}")
        all_feature_names = [f"feat_{i}" for i in range(X_processed.shape[1])]

    # Convert the processed numpy array back into a DataFrame
    X_processed_df = pd.DataFrame(X_processed, columns=all_feature_names)
    
    print("Preprocessing complete.")
    print(f"Original feature shape: {X.shape}")
    print(f"Processed feature shape: {X_processed_df.shape} (One-Hot Encoding may expand columns)")
    
    print("\nProcessed Features Head:")
    print(X_processed_df.head())

    # --- Preprocess Target Variable (y) ---
    # Convert target to numeric labels (e.g., 'Yes'/'No' -> 1/0)
    # This is necessary for most ML models.
    print("\nProcessing target variable (Label Encoding)...")
    le = LabelEncoder()
    y_processed = le.fit_transform(y_raw)
    
    print("Target processing complete.")
    print(f"Original target values: {y_raw.unique()}")
    print(f"Encoded target values: {np.unique(y_processed)}")
    print("Target Classes Mapping:", dict(zip(le.classes_, le.transform(le.classes_))))
    
    print("\n" + "="*50 + "\n")
    
    return X_processed_df, pd.Series(y_processed, name=target_column), le, preprocessor

# --- This block allows the script to be run directly ---
if __name__ == "__main__":
    # --- !!! IMPORTANT: EDIT THESE TWO LINES !!! ---
    FILE_PATH = 'path/to/your/dataset.csv'  # <-- SET YOUR CSV FILE PATH HERE
    TARGET_COLUMN = 'your_target_column_name' # <-- SET YOUR TARGET COLUMN NAME HERE
    # ----------------------------------------------

    # Suppress warnings for cleaner output
    warnings.filterwarnings('ignore')
    sns.set(style="whitegrid")

    # --- Run the entire process ---
    X_processed, y_processed, target_encoder, feature_preprocessor = load_explore_preprocess(FILE_PATH, TARGET_COLUMN)

    if X_processed is not None:
        print("--- Process Finished ---")
        print("\nFinal Processed Features (X):")
        print(X_processed.head())
        print("\nFinal Processed Target (y):")
        print(y_processed.head())
        
        # Example of splitting the processed data:
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y_processed, 
            test_size=0.3, 
            random_state=42, 
            stratify=y_processed
        )
        print(f"\nCreated training and testing sets:")
        print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
        print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")
    else:
        print("Data processing failed. Please check the file path and target column name.")