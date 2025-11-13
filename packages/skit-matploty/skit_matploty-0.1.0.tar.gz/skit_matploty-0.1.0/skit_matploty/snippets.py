# This file stores all the code snippets as raw strings.

EX1_EDA = """
# ML EX-1: Simplified EDA code

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load dataset
# df = pd.read_csv("your_dataset.csv")

# Basic info
print("Shape:", df.shape, "\n")
print(df.info(), "\n")
print(df.head(), "\n")

# 2. Missing values & statistics
print("Missing Values:\n", df.isnull().sum(), "\n")
print("Descriptive Stats:\n", df.describe(include='all'), "\n")

# Numeric & categorical columns
num_cols = df.select_dtypes(include='number').columns
cat_cols = df.select_dtypes(include=['object', 'category']).columns

# 3. Correlation heatmap
if len(num_cols) > 1:
    sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm')
    plt.title("Correlation Heatmap")
    plt.show()

# 4. Distributions
for col in num_cols:
    sns.histplot(df[col], kde=True)
    plt.title(f"{col} Distribution")
    plt.show()

# 5. Categorical count plots
for col in cat_cols:
    sns.countplot(y=col, data=df, order=df[col].value_counts().index)
    plt.title(f"{col} Count Plot")
    plt.show()

# 6. Boxplots for outliers
for col in num_cols:
    sns.boxplot(x=df[col])
    plt.title(f"{col} Boxplot")
    plt.show()

# 7. Pairplot (only if few numeric columns)
if len(num_cols) <= 5 and len(num_cols) > 1:
    sns.pairplot(df[num_cols])
    plt.suptitle("Pairwise Relationships", y=1.02)
    plt.show()
"""

EX2_PREPROCESSING = """
# EX-2: Simplified Data Preprocessing Code

# Import the needed libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from warnings import filterwarnings

filterwarnings('ignore') # Hide any warning messages

# 1. Load the dataset
# data = pd.read_csv('sensor-readings.csv')

# 2. Basic information about the data
print("Data Loaded Successfully!\n")
print("Number of Rows and Columns:", data.shape)
print("\nColumn Names:", list(data.columns))
print("\n--- Dataset Info ---")
print(data.info())

# 3. Check for missing (empty) values
missing_values = data.isnull().sum()
print("\n--- Missing Values in Each Column ---")
print(missing_values[missing_values > 0])

# 4. Fill missing values in numeric columns with their column mean
numeric_columns = data.select_dtypes(include=['number']).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())

# 5. Convert any text (categorical) columns into numeric using One-Hot Encoding
categorical_columns = data.select_dtypes(exclude=['number']).columns
if not categorical_columns.empty:
    data = pd.get_dummies(data, columns=categorical_columns, drop_first=True)

# 6. Show a simple statistical summary of all numeric columns
print("\n--- Statistical Summary ---")
print(data.describe())

# 7. Visualize numeric columns using boxplot (to see data spread and outliers)
plt.figure(figsize=(8, 4))
sns.boxplot(data=data[numeric_columns])
plt.title("Boxplot of Numeric Columns")
plt.show()

# 8. Show correlation between numeric columns using a heatmap
plt.figure(figsize=(6, 4))
sns.heatmap(data[numeric_columns].corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation Heatmap of Numeric Columns")
plt.show()

print("\nData Preprocessing Completed!")
"""

EX3_LINEAR_REGRESSION = """
# EX 3: Linear Regression - Works for Any Dataset

# 1. import Libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# 2. load Dataset
# Replace 'your_dataset.csv' with your file name
# data = pd.read_csv("your_dataset.csv")
print("Dataset Preview:\n", data.head())

# 3. Automatically detect target column (last column)
X = data.iloc[:, :-1] # all columns except last -> features
y = data.iloc[:, -1] # last column -> target

# 4. Split Data (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train Model
model = LinearRegression().fit(X_train, y_train)

# 6. Predict & Evaluate
y_pred = model.predict(X_test)

print("\nActual vs Predicted (first 5):\n", list(zip(y_test[:5], y_pred[:5])))
print("\nMean Squared Error:", mean_squared_error(y_test, y_pred))
print("R² Score:", r2_score(y_test, y_pred))

# 7. Plot Results
plt.scatter(y_test, y_pred, color='purple')
plt.xlabel("Actual Values")
plt.ylabel("Predicted Values")
plt.title("Actual vs Predicted (Linear Regression)")
plt.show()
"""

EX4_CLASSIFICATION_PIPELINE = """
# EX 4: General Classification Pipeline

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# ==== Load dataset ====
# Change 'your_dataset.csv' and 'target_column' accordingly
# data = pd.read_csv('your_dataset.csv')
# target_column = 'target' # <-- change this

# ==== Preprocessing ====
data = data.dropna() # remove missing values

# Encode categorical columns
for col in data.select_dtypes(include='object').columns:
    if col != target_column:
        data[col] = LabelEncoder().fit_transform(data[col])

# Split features and target
X = data.drop(columns=[target_column])
y = data[target_column]

# Scale features
X = StandardScaler().fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==== Classifiers ====
models = {
    "Logistic Regression": LogisticRegression(),
    "Decision Tree": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier(),
    "Naive Bayes": GaussianNB()
}

# ==== Training & Evaluation ====
results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    results.append((name, acc))
    
    print(f"\n--- {name} ---")
    print("Accuracy:", round(acc * 100, 2), "%")
    print(classification_report(y_test, y_pred))

# ==== Compare Accuracies ====
results_df = pd.DataFrame(results, columns=["Model", "Accuracy"])
print("\n=== Model Comparison ===")
print(results_df.sort_values('Accuracy', ascending=False))

# ==== Optional Confusion Matrix for Best Model ====
best_model_name = results_df.sort_values('Accuracy', ascending=False).iloc[0, 0]
best_model = models[best_model_name]
y_pred_best = best_model.predict(X_test)

plt.figure(figsize=(5, 4))
sns.heatmap(confusion_matrix(y_test, y_pred_best), annot=True, fmt='d', cmap='Blues')
plt.title(f'Confusion Matrix - {best_model_name}')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()
"""

EX5_NAIVE_BAYES = """
# EX-5: Naive Bayes (Iris Dataset)

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB # very simple baseline
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn import tree

# Load data
iris = datasets.load_iris()
X, y = iris.data, iris.target
labels = iris.target_names

# Split
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)

# Train Naive Bayes
clf = GaussianNB()
clf.fit(X_tr, y_tr)

# Evaluate Naive Bayes
y_pred = clf.predict(X_te)
print(f"Test accuracy (GaussianNB): {accuracy_score(y_te, y_pred):.3f}\n")
print(classification_report(y_te, y_pred, target_names=labels))

ConfusionMatrixDisplay.from_predictions(y_te, y_pred, display_labels=labels, cmap="Blues")
plt.title("Iris - Confusion Matrix (GaussianNB)")
plt.tight_layout()
plt.show()

# Predict sample
sample = [[5.1, 3.5, 1.4, 0.2]] # sepal len, sepal wid, petal len, petal wid
print("Predicted class:", labels[clf.predict(sample)[0]])

# Train Decision Tree (for comparison)
decision_model = tree.DecisionTreeClassifier()
decision_model.fit(X_tr, y_tr)
prediction = decision_model.predict(X_te)
print("\nDecision Tree Predictions (for comparison):\n", prediction)
"""

EX6_RF_REGRESSOR = """
# EX 6: Random Forest Regressor

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

# Load dataset
# df = pd.read_csv(input("Enter dataset file name (.csv): "))
print(df.shape); print(df.head())

# Choose target
# y_col = input("Enter target column: ")
X, y = pd.get_dummies(df.drop(y_col, axis=1), drop_first=True), df[y_col]

# Basic plots
if X.shape[1] >= 2:
    plt.scatter(X.iloc[:, 0], X.iloc[:, 1]); plt.show()
X.plot(kind='density', subplots=True, layout=(2, 3), figsize=(8, 5)); plt.show()
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm'); plt.show()

# Train & Test
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=1)
m = RandomForestRegressor(random_state=1).fit(Xtr, ytr)
yp = m.predict(Xte)

# Metrics
print("R2:", r2_score(yte, yp))
print("MSE:", mean_squared_error(yte, yp))
"""
