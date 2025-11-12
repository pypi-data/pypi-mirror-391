# AutoML Optuna Demo

An easy and lightweight demonstration of **Automated Machine Learning (AutoML)** using **Optuna** and **Scikit-learn**.  
This project automatically tunes hyperparameters of a `RandomForestClassifier` on the **Iris dataset** to find the best configuration for maximum accuracy.

---

## 📘 Overview

Manual hyperparameter tuning can be slow and confusing — especially when you don’t know which values work best for your model.

This package automates that process using **Optuna**, a fast and intelligent hyperparameter optimization framework.  
It uses **Scikit-learn**’s `RandomForestClassifier` and **Iris dataset** as an example to demonstrate how AutoML works in practice.

---

## 🧠 What It Does

- Loads the Iris dataset using Scikit-learn  
- Splits the dataset into training and testing sets  
- Defines an *objective function* for Optuna that:
  - Chooses random values for hyperparameters (`n_estimators`, `max_depth`)
  - Trains a Random Forest model
  - Evaluates accuracy on the test set  
- Optuna runs multiple trials and **automatically finds the best hyperparameters**
- Finally, the function returns:
  - ✅ Best hyperparameters  
  - 📈 Best accuracy score  

---

## 🧩 Installation

You can install this package directly from PyPI once uploaded:

```bash
pip install automl-optuna-demo
```

Or if you have cloned this repository locally, navigate to the folder and install in development mode:

```bash
pip install -e .
```

This ensures that you can make edits and re-run the package easily.

---

## 🖥️ Usage

After installation, you can use this package in two ways:

### ▶️ Option 1: Run directly in Python

```python
from automl_optuna_demo.main import run_automl

# Run with default 10 trials
best_params, best_value = run_automl()

print("Best Parameters:", best_params)
print("Best Accuracy:", best_value)
```

### ▶️ Option 2: Run with more trials

You can specify how many optimization trials you want Optuna to perform (more trials = better results, but slower):

```python
best_params, best_value = run_automl(trials=30)
print(best_params, best_value)
```

### ▶️ Option 3: Run from Command Line (if added later)

If you add a CLI entry point, you could run:
```bash
python -m automl_optuna_demo.main
```

---

## ⚙️ How It Works (Step-by-Step)

1. **Dataset Loading**  
   Uses `load_iris()` from Scikit-learn, a built-in dataset with 150 samples of 3 flower species.

2. **Data Splitting**  
   Splits data into training (80%) and testing (20%) using `train_test_split()`.

3. **Objective Function**  
   Inside the code, the objective function defines two tunable parameters:
   ```python
   n_estimators = trial.suggest_int('n_estimators', 10, 200)
   max_depth = trial.suggest_int('max_depth', 2, 32)
   ```
   Optuna will choose random combinations of these values across trials.

4. **Model Training**  
   A RandomForestClassifier is trained on the training set using these values.

5. **Evaluation**  
   The model predicts test data and returns accuracy as a numeric score to Optuna.

6. **Optimization**  
   Optuna runs multiple trials, compares accuracies, and selects the hyperparameters that gave the highest accuracy.

---

## 🧾 Example Output

Running:
```python
from automl_optuna_demo.main import run_automl
params, score = run_automl(trials=20)
print(params)
print(score)
```

might produce:

```
{'n_estimators': 132, 'max_depth': 7}
0.9666666667
```

Meaning Optuna found the best configuration after 20 trials that gave about **96.7% accuracy**.

---

## 📂 Project Structure

```
automl_optuna_demo/
├── __init__.py          # Makes it a Python package
├── main.py              # Core logic for AutoML optimization
setup.py                 # Packaging configuration for PyPI
setup.cfg                # Additional package metadata
README.md                # You are here
```

---

## 🧰 Requirements

This project depends on:

- [Optuna](https://optuna.org/)
- [Scikit-learn](https://scikit-learn.org/stable/)

Install manually (if needed):
```bash
pip install optuna scikit-learn
```

---

## ⚡ Troubleshooting

| Problem | Possible Cause | Solution |
|----------|----------------|-----------|
| `ModuleNotFoundError` | You didn’t install the package | Run `pip install -e .` in your project folder |
| `optuna not found` | Optuna not installed | Run `pip install optuna` |
| `no attribute run_automl` | Wrong import | Use `from automl_optuna_demo.main import run_automl` |
| Very low accuracy | Too few trials | Increase `trials` value in `run_automl(trials=50)` |

---

## 🧑‍💻 Future Improvements

- Add command-line interface (CLI) for easy execution  
- Add support for more models (e.g., SVM, XGBoost, Logistic Regression)  
- Visualize Optuna optimization history  
- Allow loading custom datasets instead of Iris  

---

## 🪪 License

MIT License © 2025 Vaishnav Naik  
Feel free to use and modify this code for learning or projects!

---

## 💬 Author

**Vaishnav Naik**  
GitHub: [your-github-profile]  
Email: [your-email-if-you-want-to-add]

---

### 🌟 Support

If you like this project, star it on GitHub or share it with others learning Optuna or AutoML!
