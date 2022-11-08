from collections import namedtuple

from data_process.CommitUtil import preprocess
from enum import Enum


class CommitCategory(namedtuple('CommitCategory', 'name regex_exp'), Enum):
    """
    Enum class for each category, in which name attribute (the first one) is the unique name for the category. And the
    regex_exp is the regular expression of the pattern for the category
    """
    DESCRIBE_ERROR_SCENARIO = "describe_error_scenario", "*"
    TO_FIX_DEFECTS = "to_fix_defects", "*"

    def __str__(self) -> str:
        return self.name


def pattern_match(pattern: CommitCategory, commit_msg: str) -> bool:
    """
    return true if commit_msg matched pattern
    """

    return True


def commit_classifier(commit_msg: str) -> list:
    """
    return list of categories for commit_msg
    """

    res: list = []

    for pattern in CommitCategory:
        if pattern_match(pattern, commit_msg):
            res.append(pattern)

    return res


if __name__ == "__main__":
    """
    pipeline for classifying a single commit message
    """
    commit_msg_test: str = "any commit msg"

    # preprocess commit msg
    commit_msg_test = preprocess(commit_msg_test)

    # get the list of Patterns that the commit message can be classified to
    category: list = commit_classifier(commit_msg_test)

    print("Commit Message: {} belongs to {} categories".format(commit_msg_test, ", ".join([str(e) for e in category])))
