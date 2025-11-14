def transform_data(data, available_labels):
    """
    Transform data between two formats:
    - If input data is a list of label sets (e.g., [["cat", "dog"], ["dog"]]),
      convert it into a binary matrix representation (one-hot encoding).
    - If input data is already in binary matrix form, convert it back to label sets.

    Args:
        data (list): A nested list of annotations.
                     Format: data[annotator][item][label or binary]
        available_labels (list): List of all possible labels.

    Returns:
        list: Transformed data (either one-hot encoding or label sets).
    """
    if data[0][0][0] != 0 and data[0][0][0] != 1:
        # Transform from label sets to binary one-hot vectors
        for i, annotator in enumerate(data):
            for j, item in enumerate(annotator):
                transformed_item = [1 if label in item else 0 for label in available_labels]
                data[i][j] = transformed_item
    else:
        # Transform from binary matrix to label sets
        for i, annotator in enumerate(data):
            for j, item in enumerate(annotator):
                data[i][j] = [available_labels[ij] for ij, label in enumerate(item) if label]

    return data


def _calculate_pairwise_item_overlap(a1_item_decisions, a2_item_decisions):
    """
    Calculate the number of labels where two annotators agree for a single item.

    Args:
        a1_item_decisions (list[int]): Binary decisions for annotator 1 on a single item.
        a2_item_decisions (list[int]): Binary decisions for annotator 2 on the same item.

    Returns:
        int: Number of matching labels.
    """
    agreements = 0
    for i, a1_label in enumerate(a1_item_decisions):
        if a1_label == a2_item_decisions[i]:
            agreements += 1
    return agreements


def _calculate_total_item_overlap(all_item_decisions):
    """
    Calculate the total number of label agreements across all annotator pairs for a single item.

    Args:
        all_item_decisions (list[list[int]]): Binary decisions for all annotators on one item.

    Returns:
        int: Total label agreements across all annotator pairs.
    """
    agreements = 0
    for i, decision in enumerate(all_item_decisions):
        for j in range(i + 1, len(all_item_decisions)):
            agreements += _calculate_pairwise_item_overlap(decision, all_item_decisions[j])
    return agreements


def _calculate_number_handshakes(number_annotators):
    """
    Calculate the number of unique annotator pairs.

    Args:
        number_annotators (int): Number of annotators.

    Returns:
        float: Number of annotator pairs (n choose 2).
    """
    return (number_annotators * (number_annotators - 1)) / 2


def _calculate_observed_item_agreement(total_item_overlap, number_handshakes, number_labels):
    """
    Calculate observed agreement for a single item across annotators.

    Args:
        total_item_overlap (int): Total label agreements across annotator pairs.
        number_handshakes (int): Total annotator pairs.
        number_labels (int): Number of labels.

    Returns:
        float: Observed agreement score.
    """
    return total_item_overlap / (number_labels * number_handshakes)


def _get_number_annotators(all_decisions):
    """
    Get the number of annotators.

    Args:
        all_decisions (list): Nested list of all annotator decisions.

    Returns:
        int: Number of annotators.
    """
    return len(all_decisions)


def _get_number_items(all_decisions):
    """
    Get the number of items annotated by each annotator.
    Raises an error if annotators have different numbers of items.

    Args:
        all_decisions (list): Nested list of all annotator decisions.

    Returns:
        int: Number of items.
    """
    number_items = len(all_decisions[0])
    for i, annotator in enumerate(all_decisions[1:]):
        if len(annotator) != number_items:
            raise ValueError(f"Mismatch in number of items between annotator1 and annotator{i + 1}")
    return number_items


def _get_number_labels(all_decisions):
    """
    Get the number of labels for each item.
    Raises an error if items have different label lengths.

    Args:
        all_decisions (list): Nested list of all annotator decisions.

    Returns:
        int: Number of labels.
    """
    number_labels = len(all_decisions[0][0])
    for i, annotator in enumerate(all_decisions):
        for j, item in enumerate(annotator):
            if len(item) != number_labels:
                raise ValueError(
                    f"Mismatch in number of labels between the first item of annotator1 and item{j} of annotator{i + 1}")
    return number_labels


def _get_item_decisions(all_decisions, item):
    """
    Get all annotator decisions for a single item.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        item (int): Index of the item.

    Returns:
        list[list[int]]: List of binary decisions for the item.
    """
    return [annotator[item] for annotator in all_decisions]


def _count_set_labels(all_decisions, label):
    """
    Count how many times a specific label was assigned (set to 1) across all annotators and items.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        label (int): Label index.

    Returns:
        int: Total count of the label being set.
    """
    set_labels = 0
    for annotator in all_decisions:
        for item in annotator:
            set_labels += item[label]
    return set_labels


def calculate_label_prevalence(all_decisions, label):
    """
    Calculate the prevalence (frequency) of a label across all annotations.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        label (int): Label index.

    Returns:
        float: Label prevalence.
    """
    number_annotators = _get_number_annotators(all_decisions)
    number_items = _get_number_items(all_decisions)
    set_labels = _count_set_labels(all_decisions, label)
    return set_labels / (number_annotators * number_items)


def calculate_raw_prevalence(all_decisions):
    """
    Calculate the average raw prevalence of all labels.

    Args:
        all_decisions (list): Nested list of annotator decisions.

    Returns:
        float: Average label prevalence.
    """
    raw_prevalence = 0
    number_labels = _get_number_labels(all_decisions)
    for i in range(number_labels):
        raw_prevalence += calculate_label_prevalence(all_decisions, i)
    return raw_prevalence / number_labels


def _calculate_expected_label_agreement(method, prevalence):
    """
    Calculate expected agreement for a label given its prevalence.

    Args:
        method (str): Agreement method ('k', 'ac1', or 'pabak').
        prevalence (float): Label prevalence.

    Returns:
        float: Expected label agreement.
    """
    if method == "k":
        return prevalence * prevalence + (1 - prevalence) * (1 - prevalence)
    elif method == "ac1":
        return (prevalence * 2) * (1 - prevalence)
    elif method == "pabak":
        return 0.5
    else:
        raise ValueError(f"Method {method} is not supported. Try k, ac1 or pabak")


def calculate_total_expected_agreement(all_decisions, method):
    """
    Calculate total expected agreement across all labels.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        method (str): Agreement method ('k', 'ac1', or 'pabak').

    Returns:
        float: Average expected agreement across labels.
    """
    total_expected_agreement = 0
    number_labels = _get_number_labels(all_decisions)
    for i in range(number_labels):
        prevalence = calculate_label_prevalence(all_decisions, i)
        total_expected_agreement += _calculate_expected_label_agreement(method, prevalence)
    return total_expected_agreement / number_labels


def calculate_observed_item_agreement(all_decisions, item):
    """
    Calculate observed agreement for a single item across all annotators.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        item (int): Index of the item.

    Returns:
        float: Observed item agreement.
    """
    number_labels = _get_number_labels(all_decisions)
    number_annotators = _get_number_annotators(all_decisions)
    item_decisions = _get_item_decisions(all_decisions, item)
    total_item_overlap = _calculate_total_item_overlap(item_decisions)
    number_handshakes = _calculate_number_handshakes(number_annotators)
    return _calculate_observed_item_agreement(total_item_overlap, number_handshakes, number_labels)


def _kappa_normalization(observed_agreement, expected_agreement):
    """
    Compute Cohen's kappa-style normalization.

    Args:
        observed_agreement (float): Observed agreement value.
        expected_agreement (float): Expected agreement value.

    Returns:
        float: Normalized agreement (kappa).
    """
    # Perfect-agreement corner
    if expected_agreement == 1.0:
        return 1.0 if observed_agreement == expected_agreement else float('nan')

    # Normal case
    return (observed_agreement - expected_agreement) / (1.0 - expected_agreement)


def calculate_item_multi_label_agreement(all_decisions, item, method):
    """
    Calculate the multi-label agreement for a single item using a given method.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        item (int): Index of the item.
        method (str): Agreement method ('k', 'ac1', or 'pabak').

    Returns:
        float: Multi-label agreement score for the item.
    """
    observed_item_agreement = calculate_observed_item_agreement(all_decisions, item)
    expected_agreement = calculate_total_expected_agreement(all_decisions, method)
    return _kappa_normalization(observed_item_agreement, expected_agreement)


def calculate_total_multi_label_agreement(all_decisions, method):
    """
    Calculate the overall multi-label agreement across all items.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        method (str): Agreement method ('k', 'ac1', or 'pabak').

    Returns:
        float: Average multi-label agreement across all items.
    """
    number_items = _get_number_items(all_decisions)
    total_agreement = 0
    for i in range(number_items):
        total_agreement += calculate_item_multi_label_agreement(all_decisions, i, method)
    return total_agreement / number_items


def calculate_minimum_prevalence_agreement(all_decisions, method):
    """
    Calculate the minimum prevalence-adjusted agreement.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        method (str): Agreement method ('k', 'ac1', or 'pabak').

    Returns:
        float: Minimum prevalence-adjusted agreement value.
    """
    n_annotators = _get_number_annotators(all_decisions)
    n_items = _get_number_items(all_decisions)
    n_labels = _get_number_labels(all_decisions)
    n_pairs = _calculate_number_handshakes(n_annotators)

    if method == "pabak":
        ao_min = (n_annotators - 2) / (2 * (n_annotators - 1)) if n_annotators % 2 == 0 else (n_annotators - 1) / (
                    2 * n_annotators)
    else:
        ao_min = 0
        for i in range(n_labels):
            total_ones = _count_set_labels(all_decisions, label=i)
            m = total_ones // n_items
            t = total_ones - m * n_items
            f_floor = (m * (m - 1)) / 2 + (n_annotators - m) * (n_annotators - m - 1) / 2
            f_ceil = ((m + 1) * m) / 2 + (n_annotators - m - 1) * (n_annotators - m - 2) / 2
            ao_min += (((n_items - t) * f_floor) + (t * f_ceil)) / (n_items * n_pairs)
        ao_min = ao_min / n_labels

    expected_agreement = calculate_total_expected_agreement(all_decisions, method)
    return _kappa_normalization(ao_min, expected_agreement)


def calcuate_observed_label_agreement(all_decisions, label):
    """
    Calculate observed agreement for a single label across all items.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        label (int): Label index.

    Returns:
        float: Observed label agreement score.
    """
    agreements = 0
    number_items = _get_number_items(all_decisions)
    for item in range(number_items):
        all_item_decisions = _get_item_decisions(all_decisions, item)
        for i, decision in enumerate(all_item_decisions):
            for j in range(i + 1, len(all_item_decisions)):
                if decision[label] == all_item_decisions[j][label]:
                    agreements += 1
    return agreements / (number_items * _calculate_number_handshakes(_get_number_annotators(all_decisions)))


def calcuate_label_agreement(all_decisions, label, method):
    """
    Calculate agreement for a specific label using a given method.

    Args:
        all_decisions (list): Nested list of annotator decisions.
        label (int): Label index.
        method (str): Agreement method ('k', 'ac1', or 'pabak').

    Returns:
        float: Label agreement score.
    """
    observed_label_agreement = calcuate_observed_label_agreement(all_decisions, label)
    expected_label_agreement = _calculate_expected_label_agreement(method,
                                                                   calculate_label_prevalence(all_decisions, label))
    return _kappa_normalization(observed_label_agreement, expected_label_agreement)

__all__ = [
    'transform_data',
    'calculate_label_prevalence',
    'calculate_raw_prevalence',
    'calculate_total_expected_agreement',
    'calculate_observed_item_agreement',
    'calculate_item_multi_label_agreement',
    'calculate_total_multi_label_agreement',
    'calculate_minimum_prevalence_agreement',
    'calcuate_observed_label_agreement',
    'calcuate_label_agreement',
]
