from collections import namedtuple

from util.CommitUtil import *
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


class CommitClassifier():
    def __init__(self, commit_msg: str):
        """
            return list of categories for commit_msg
            """

        self.res: list = []
        self.commit_msg = commit_msg

    def preprocess(self):
        """
        preprocess commit_msg
        """
        tokenized_lst = stem_tokenize(self.commit_msg)
        self.commit_msg = ' '.join(tokenized_lst)
        self.commit_msg = remove_stop_words(self.commit_msg)
        self.commit_msg = denoise(self.commit_msg)

    def pattern_match(self, pattern: CommitCategory, verbose: bool = False) -> bool:
        """
        return true if commit_msg matched pattern
        """
        if re.search(pattern.regex_exp, self.commit_msg):
            if verbose:
                self.info(pattern.name, re.findall(pattern.regex_exp, self.commit_msg))
            return True

        return False

    def classify(self) -> list:
        self.preprocess()
        for pattern in CommitCategory:
            if self.pattern_match(pattern, True):
                self.res.append(pattern)
        return self.res

    def info(self, pattern_name: str, all_found_patterns: list):
        print("Commit Message: {},Category: {}\nMatched patterns: {}\n".format(self.commit_msg, pattern_name,
                                                                             ", ".join(all_found_patterns)))


if __name__ == "__main__":
    """
    pipeline for classifying a single commit message
    """
    commit_msg_test: str = "fixed error feat:"
    commit_classifer = CommitClassifier(commit_msg_test)
    commit_classifer.preprocess()
    print('raw string: {}, preprocessed string: {}'.format(commit_msg_test, commit_classifer.commit_msg))

    # get the list of Patterns that the commit message can be classified to
    category: list = commit_classifer.classify()
    print("Commit Message: {} belongs to {} categories".format(commit_msg_test, ", ".join([str(e) for e in category])))
