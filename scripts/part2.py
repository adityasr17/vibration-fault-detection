import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import tensorflow as tf
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
from tensorflow.keras import layers, models


# Load CSV
df = pd.read_csv("features.csv")

# Inspect class distribution
print("Class counts:\n", df['label'].value_counts())

# Check for classes with at least 2 samples
min_samples = 2
counts = df['label'].value_counts()
valid_classes = counts[counts >= min_samples].index.tolist()
print("Valid classes for training:", valid_classes)

# Keep only valid classes
df = df[df['label'].isin(valid_classes)]

if df.shape[0] == 0:
    raise ValueError("No valid samples left after filtering. Check your dataset.")

# Features and labels
X = df.drop('label', axis=1).values.astype(np.float32)
y = df['label'].values

# Encode labels to integers
le = LabelEncoder()
y_int = le.fit_transform(y)

# One-hot encode
y_onehot = tf.keras.utils.to_categorical(y_int, num_classes=len(le.classes_))
print("One-hot labels shape:", y_onehot.shape)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_onehot, test_size=0.2, random_state=42, stratify=y_int
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Reshape for 1D CNN
X_train_cnn = X_train_scaled[..., np.newaxis]
X_test_cnn = X_test_scaled[..., np.newaxis]

print("Training samples:", X_train_cnn.shape[0])
print("Test samples:", X_test_cnn.shape[0])
print("Number of classes:", len(le.classes_))

# Number of classes
num_classes = len(le.classes_)
"""
# 1D CNN Architecture
model = models.Sequential([
    layers.Conv1D(32, kernel_size=3, activation='relu', input_shape=(X_train_cnn.shape[1], 1)),
    layers.BatchNormalization(),
    layers.MaxPooling1D(pool_size=2),

    layers.Conv1D(64, kernel_size=3, activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling1D(pool_size=2),

    layers.Flatten(),

    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),

    layers.Dense(num_classes, activation='softmax')
])

model.summary()

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)



history = model.fit(
    X_train_cnn, y_train,
    validation_split=0.2,
    epochs=30,
    batch_size=16,
    verbose=1
)


loss, acc = model.evaluate(X_test_cnn, y_test, verbose=0)
print(f"Test Accuracy: {acc:.4f}")

plt.plot(history.history['accuracy'], label='Train Acc')
plt.plot(history.history['val_accuracy'], label='Val Acc')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.savefig("learning_curve.png")
"""
# -----------------------------
# Train Random Forest
# -----------------------------
rf = RandomForestClassifier(
    n_estimators=300,     # number of trees
    max_depth=None,       # let trees grow
    random_state=42,
    class_weight="balanced"  # good for uneven classes
)

rf.fit(X_train_scaled, np.argmax(y_train, axis=1))  # y_train is one-hot → convert back to ints

# -----------------------------
# Predictions
# -----------------------------
y_pred_rf = rf.predict(X_test_scaled)

# -----------------------------
# Evaluation
# -----------------------------
print("\n=== Random Forest Performance ===\n")
print("Accuracy:", accuracy_score(np.argmax(y_test, axis=1), y_pred_rf))
print("\nClassification Report:\n")
print(classification_report(np.argmax(y_test, axis=1), y_pred_rf, target_names=le.classes_))

# -----------------------------
# Confusion Matrix
# -----------------------------
cm = confusion_matrix(np.argmax(y_test, axis=1), y_pred_rf)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.title("Random Forest Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.savefig("random_forest.png")


# Save Random Forest model
joblib.dump(rf, "random_forest_model.pkl")

# Save scaler (you MUST save this for correct prediction later)
joblib.dump(scaler, "scaler.pkl")

# Save label encoder (to decode output labels)
joblib.dump(le, "label_encoder.pkl")
