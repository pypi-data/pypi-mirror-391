# Utility: Read file if it exists, else return None
import os
def read_file_if_exists(path, encoding='utf-8'):
	if path and os.path.isfile(path):
		try:
			with open(path, encoding=encoding) as f:
				return f.read()
		except Exception:
			return None
	return None

def cap(value: int, max_value: int) -> int:
    """
    Cap a metric value to avoid exceeding its maximum possible weight.
    """
    return min(value, max_value)


def normalize_score(raw_value: int, weight: int, threshold: int) -> int:
    """
    Normalize a raw metric value based on its threshold and weight.
    Computes weignted normalized score.
    """
    if threshold <= 0:
        return 0
    normalized = min(raw_value, threshold) / threshold
    return round(normalized * weight)


def compute_weighted_scores(component_scores: dict, weights: dict, max_metric_value: int = 4):
    weighted = {k: (v / max_metric_value) * weights[k] for k, v in component_scores.items()}
    total = sum(weighted.values())
    return weighted, total
