import json
import pandas as pd
import numpy as np
from scipy.stats import norm
from cumulus_library_kidney_transplant.accuracy import kappa

# scale invariant
# NUM_SAMPLES chosen to make it easy to pick INTEGER
NUM_SAMPLES = 100 * 1000

def confusion_matrix(f1_score=0.95, prevalence=0.5, n=NUM_SAMPLES) -> dict:
    return {'balanced': confusion_matrix_balanced(f1_score, prevalence, n),
            'max_precision': confusion_matrix_max_precision(f1_score, prevalence, n),
            'max_recall': confusion_matrix_max_recall(f1_score, prevalence, n)}

def confusion_matrix_balanced(f1_score=0.95, prevalence=0.5, n=NUM_SAMPLES) -> dict:
    """
    Balanced: Precision = Recall = F1
    """
    positives = int(n * prevalence)
    negatives = n - positives

    tp = int(round(f1_score * positives))
    fn = positives - tp
    fp = int(round(tp * (1 - f1_score) / f1_score))
    tn = negatives - fp

    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn}


def confusion_matrix_max_precision(f1_score=0.95, prevalence=0.5, n=NUM_SAMPLES) -> dict:
    """
    Max precision: Precision = 1.0, solve Recall from F1
    """
    positives = int(n * prevalence)
    negatives = n - positives

    recall = f1_score / (2 - f1_score)  # solved above
    tp = int(round(recall * positives))
    fn = positives - tp
    fp = 0  # precision = 1 means no false positives
    tn = negatives - fp

    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn}


def confusion_matrix_max_recall(f1_score=0.95, prevalence=0.5, n=NUM_SAMPLES):
    """
    Max recall: Recall = 1.0, solve Precision from F1
    """
    positives = int(n * prevalence)
    negatives = n - positives

    precision = f1_score / (2 - f1_score)  # solved above
    tp = positives  # recall = 1 means all positives captured
    fn = 0
    # Solve FP from precision = TP / (TP+FP)
    fp = int(round(tp * (1 - precision) / precision))
    tn = negatives - fp

    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn}

def calc_confusion_matrix_dict(matrix:dict) -> dict:
    return calc_confusion_matrix(
        tp=matrix["TP"],
        fp=matrix["FP"],
        fn=matrix["FN"],
        tn=matrix["TN"])

def calc_confusion_matrix(tp:int, fp:int, fn:int, tn:int) -> dict:
    """
    Calculate Cohen's Kappa, F1, PPV, Recall, and Precision
    from a 2x2 confusion matrix.

    Parameters:
        tp (int): True Positives (TP)
        fp (int): False Positives (FP)
        fn (int): False Negatives (FN)
        tn (int): True Negatives (TN)

    **notice** TN is LAST because it True Negatives are the least important!
    F1, Recall, and PPV dont even measure True Negatives (TN).
    The common order is tp, fp, fn, tn for that reason in accuracy calculations.
    This is non-obvious so documenting here explicitly.

    :return dict of calculated Cohen's Kappa, F1, PPV, Recall, and Precision
    """
    # Totals
    n = tp + fp + fn + tn
    if n == 0:
        raise ValueError("Confusion matrix is empty.")

    # Observed agreement
    po = (tp + tn) / n

    # Expected agreement
    p_yes_true = (tp + fn) / n
    p_yes_pred = (tp + fp) / n
    p_no_true = (fp + tn) / n
    p_no_pred = (fn + tn) / n
    pe = p_yes_true * p_yes_pred + p_no_true * p_no_pred

    # Cohen's kappa
    kappa_k = (po - pe) / (1 - pe) if (1 - pe) != 0 else 0.0

    # Recall (Sensitivity)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # Precision (PPV)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    # Specificity
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    # F1-score
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)

    return {
        "kappa_k": kappa_k,
        "kappa_enum": str(kappa.agree_interpret(kappa_k)),
        "f1": f1,
        "ppv": precision,  # synonym
        "recall": recall,
        "specificity": specificity
    }

def json_to_csv(filename_json:str):
    with open(filename_json, "r") as f:
        content = json.load(f)
    df = pd.json_normalize(content)
    df.columns = df.columns.str.replace(r"\.", "_", regex=True)
    return df.to_csv(f'{filename_json}.csv', index=False)

#####################################################################################################################
"""
Minimal sample size calculators using numpy/scipy.
"""
#####################################################################################################################

def n_single_prevalence(p: float, margin_error: float, alpha: float = 0.05, fpc_N: int | None = None, deff: float = 1.0) -> float:
    z = norm.ppf(1 - alpha/2.0)
    n = (z**2) * p * (1 - p) / (margin_error**2)
    n *= deff
    if fpc_N is not None:
        n = (n * fpc_N) / (n + fpc_N - 1)
    return n

def n_two_proportions(p1: float, p2: float, alpha: float = 0.05, power: float = 0.80, ratio: float = 1.0, deff: float = 1.0) -> tuple[float, float]:
    z_alpha = norm.ppf(1 - alpha/2.0)
    z_beta  = norm.ppf(power)
    k = ratio
    p_bar = (p1 + k*p2) / (1 + k)
    q_bar = 1 - p_bar
    se0 = np.sqrt((1 + 1/k) * p_bar * q_bar)
    se1 = np.sqrt(p1*(1-p1) + (p2*(1-p2))/k)
    delta = abs(p1 - p2)
    n1 = ((z_alpha*se0 + z_beta*se1) / delta) ** 2
    n1 *= deff
    n2 = k * n1
    return n1, n2


def write_sample_size_requirements_csv():
    """
    Create an output file (JSON or CSV) of sample size requirements for given F1 accuracy and % prevalence of phenotype
    """
    output = list()
    for f1_score in [0.80, 0.85, 0.9, 0.95]:
        for prevalence in [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:

            matrix = confusion_matrix(f1_score=f1_score, prevalence=prevalence)

            balanced = matrix['balanced']
            max_precision  = matrix['max_precision']
            max_recall = matrix['max_recall']

            output.append({
                'f1':f1_score,
                'prevalence':prevalence,
                'balanced': {'matrix': balanced, 'calc': calc_confusion_matrix_dict(balanced)},
                'precision': {'matrix': max_precision, 'calc': calc_confusion_matrix_dict(max_precision)},
                'recall': {'matrix': max_recall, 'calc': calc_confusion_matrix_dict(max_recall)},
            })
    print(output)
    with open('sample_size.json', 'w') as f:
        json.dump(output, f, indent=4)

    json_to_csv('sample_size.json')


if __name__ == '__main__':
    write_sample_size_requirements_csv()
