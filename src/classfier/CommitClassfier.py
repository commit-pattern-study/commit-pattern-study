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
                                   "(?P<link_issue_verb>{})?.*?(issue|review)?.*?(?P<issue_link>\#\d+)+".format(
                                       getKeywordFromFile(LINK_ISSUE_VERB_KEYWORD_FILE))
    OUT_OF_DATE = "out_of_date", "({})+".format(getKeywordFromFile(OUT_OF_DATE_KEYWORD_FILE))

    def __str__(self) -> str:
        return self.name


class CommitClassifier:
    def __init__(self, commit_msgs: list[str], verbose: bool = False):
        """
            return list of categories for commit_msg
            """

        self.commit_category_dict = {}
        self.commit_msgs = commit_msgs
        self.preprocessed_msgs = []
        self.verbose = verbose

    def preprocess(self):
        """
        preprocess commit_msg
        """
        for commit_msg in self.commit_msgs:
            tokenized_lst = stem_tokenize(commit_msg)
            tokenized_msg = ' '.join(tokenized_lst)
            tokenized_msg = remove_stop_words(tokenized_msg)
            tokenized_msg = denoise(tokenized_msg)
            self.preprocessed_msgs.append(tokenized_msg)
            if self.verbose:
                print('raw string: {}, preprocessed string: {}\n'.format(commit_msg, tokenized_msg))

    def classify(self):
        self.preprocess()
        for commit_msg in self.commit_msgs:
            commit_categories = []
            matched_substrings = []
            for pattern in CommitCategory:
                if re.search(pattern.regex_exp, commit_msg):
                    if self.verbose:
                        matched_substrings.append(re.findall(pattern.regex_exp, commit_msg))
                    commit_categories.append(pattern)
            if self.verbose:
                print("Commit Message: {}, Categories: {}\n Matched substrings: {}\n".format(commit_msg,
                                                                                             commit_categories,
                                                                                             matched_substrings))
            self.commit_category_dict[commit_msg] = commit_categories

    def pretty_print(self):
        for commit_msg in self.commit_msgs:
            categories = self.commit_category_dict[commit_msg]
            print("Commit Message: {}, Categories: {}".format(commit_msg, ", ".join([str(e) for e in categories])))


if __name__ == "__main__":
    """
    pipeline for classifying a single commit message
    """
    commit_msg_test: str = "fixed error feat:"
    commit_msg_test2: str = "fixes #20"
    commit_classifer = CommitClassifier([commit_msg_test, commit_msg_test2], False)
    commit_classifer.classify()
    commit_classifer.pretty_print()
