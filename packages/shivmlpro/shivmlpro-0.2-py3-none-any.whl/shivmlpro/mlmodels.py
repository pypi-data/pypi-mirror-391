# mlmodels.py
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Optional: XGBoost
try:
    from xgboost import XGBClassifier, XGBRegressor
except ImportError:
    XGBClassifier = XGBRegressor = None


# ------------------------------ Helper: Preprocessing ------------------------------
def preprocess_data(X, y=None):
    X = X.copy()
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = LabelEncoder().fit_transform(X[col])
    if y is not None and y.dtype == 'O':
        y = LabelEncoder().fit_transform(y)
    X = X.fillna(X.mean(numeric_only=True))
    X = pd.DataFrame(StandardScaler().fit_transform(X), columns=X.columns)
    return X, y


# ------------------------------ Supervised Models ------------------------------
def train_supervised(X, y, model_name):
    X, y = preprocess_data(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "linear": LinearRegression(),
        "logistic": LogisticRegression(),
        "decisiontree": DecisionTreeClassifier(),
        "randomforest": RandomForestClassifier(),
        "naivebayes": GaussianNB(),
        "svm": SVC(probability=True),
        "knn": KNeighborsClassifier(n_neighbors=5),
        "xgboost": XGBClassifier(use_label_encoder=False, eval_metric='logloss') if XGBClassifier else None
    }

    model = models.get(model_name.lower())
    if model is None:
        print(f"❌ Unknown model name: {model_name}")
        print("Available models:", list(models.keys()))
        return None

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    average = 'binary' if len(np.unique(y)) == 2 else 'macro'
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average=average)
    rec = recall_score(y_test, y_pred, average=average)
    f1 = f1_score(y_test, y_pred, average=average)
    cm = confusion_matrix(y_test, y_pred)

    print("\n✅ Model Trained Successfully!")
    print(f"Model Used: {model_name.upper()}")
    print(f"Accuracy: {acc:.3f}")
    print(f"Precision: {prec:.3f}")
    print(f"Recall: {rec:.3f}")
    print(f"F1 Score: {f1:.3f}")
    print("Confusion Matrix:\n", cm)

    # Feature Importance (if available)
    if hasattr(model, 'feature_importances_'):
        feat_imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
        plt.figure(figsize=(8, 4))
        feat_imp.head(10).plot(kind='bar', title="Top 10 Feature Importances")
        plt.tight_layout()
        plt.show()

    return model


# ------------------------------ Unsupervised Models ------------------------------
def train_unsupervised(X, model_name, clusters=3):
    X, _ = preprocess_data(X)
    if model_name.lower() == 'kmeans':
        model = KMeans(n_clusters=clusters, random_state=42)
        model.fit(X)
        print("✅ KMeans Model Trained Successfully!")
        print("Cluster Centers:\n", model.cluster_centers_)
        print("Labels:", np.unique(model.labels_))

        plt.figure(figsize=(5, 4))
        plt.scatter(X.iloc[:, 0], X.iloc[:, 1], c=model.labels_, cmap='rainbow')
        plt.title("KMeans Clustering Visualization")
        plt.show()
        return model
    else:
        print("❌ Unknown unsupervised model. Available: ['kmeans']")
        return None


# ------------------------------ Reinforcement Learning (Q-Learning) ------------------------------
def q_learning(env_states=5, actions=2, episodes=500, alpha=0.1, gamma=0.9):
    Q = np.zeros((env_states, actions))
    for _ in range(episodes):
        state = np.random.randint(0, env_states)
        done = False
        while not done:
            action = np.random.choice(actions)
            next_state = np.random.randint(0, env_states)
            reward = np.random.choice([0, 1])
            Q[state, action] += alpha * (reward + gamma * np.max(Q[next_state, :]) - Q[state, action])
            done = np.random.rand() > 0.9
    print("✅ Q-Learning Completed!\nQ-Table:\n", Q)
    return Q


# ------------------------------ Main Controller ------------------------------
def train_model(data, target=None, model_name="randomforest", task="supervised"):
    if isinstance(data, str):
        df = pd.read_csv(data)
    else:
        df = data.copy()

    if task == "supervised":
        if target is None:
            raise ValueError("Please specify target column for supervised learning.")
        X = df.drop(columns=[target])
        y = df[target]
        return train_supervised(X, y, model_name)

    elif task == "unsupervised":
        return train_unsupervised(df, model_name)

    elif task == "reinforcement":
        return q_learning()

    else:
        raise ValueError("Task must be 'supervised', 'unsupervised', or 'reinforcement'.")
