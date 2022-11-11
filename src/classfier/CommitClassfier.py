from collections import namedtuple

from data_process.CommitUtil import preprocess
from enum import Enum

import re

from util.FileUtil import getKeywordFromFile
from project_path import ROOT_DIR

TO_FIX_DEFECTS_KEYWORD_FILE = "{}/data/pattern/to_fix_defects_keyword.txt".format(ROOT_DIR)
LINK_ISSUE_VERB_KEYWORD_FILE = "{}/data/pattern/link_issue_verb_keyword.txt".format(ROOT_DIR)
OUT_OF_DATE_KEYWORD_FILE = "{}/data/pattern/out_of_date_keyword.txt".format(ROOT_DIR)

class CommitCategory(namedtuple('CommitCategory', 'name regex_exp'), Enum):
    """
    Enum class for each category, in which name attribute (the first one) is the unique name for the category. And the
    regex_exp is the regular expression of the pattern for the category
    """
    DESCRIBE_ERROR_SCENARIO = "describe_error_scenario", ".*error.*"
    TO_FIX_DEFECTS = "to_fix_defects", "({})+".format(getKeywordFromFile(TO_FIX_DEFECTS_KEYWORD_FILE))
    ISSUE_LINK = "issue_link", "https"
    INTRODUCE_ISSUE_PR_REFERENCE = "introduce_issue_PR_reference", \
                                   "(?P<link_issue_verb>{})?.*?(issue|review)?.*?(?P<issue_link>\#\d+)+".format(getKeywordFromFile(LINK_ISSUE_VERB_KEYWORD_FILE))
    OUT_OF_DATE = "out_of_date", "({})+".format(getKeywordFromFile(OUT_OF_DATE_KEYWORD_FILE))

    def __str__(self) -> str:
        return self.name


def pattern_match(pattern: CommitCategory, commit_msg: str, verbose: bool = False) -> bool:
    """
    return true if commit_msg matched pattern
    """

    if re.search(pattern.regex_exp, commit_msg):
        if verbose:
            info(pattern.name, commit_msg, re.findall(pattern.regex_exp, commit_msg))
        return True

    return False


def info(pattern_name: str, commit_msg: str, all_found_patterns: list):
    print("Commit Message: {}, Pattern: {}\nFound patterns: {}\n".format(commit_msg, pattern_name,
                                                                         all_found_patterns))


def commit_classifier(commit_msg: str) -> list:
    """
    return list of categories for commit_msg
    """

    res: list = []

    for pattern in CommitCategory:
        if pattern_match(pattern, commit_msg, True):
            res.append(pattern)

    return res


if __name__ == "__main__":
    """
    pipeline for classifying a single commit message
    """
    commit_msg_test: str = "actually deprecate stuff"

    # preprocess commit msg
    commit_msg_test = preprocess(commit_msg_test)

    # get the list of Patterns that the commit message can be classified to
    category: list = commit_classifier(commit_msg_test)

    print("Commit Message: {} belongs to {} categories".format(commit_msg_test, ", ".join([str(e) for e in category])))