from collections import namedtuple
from enum import Enum
import pandas as pd

from project_path import ROOT_DIR
from util.CommitUtil import *
from util.FileUtil import getKeywordFromFile

PATTERN_DIR = "{}/data/pattern/".format(ROOT_DIR)
TO_FIX_DEFECTS_KEYWORD_FILE = PATTERN_DIR + "to_fix_defects_keyword.txt"
LINK_ISSUE_VERB_KEYWORD_FILE = PATTERN_DIR + "link_issue_verb_keyword.txt"
OUT_OF_DATE_KEYWORD_FILE = PATTERN_DIR + "out_of_date_keyword.txt"
TEST_VERB_KEYWORD_FILE = PATTERN_DIR + "test_verb_keyword.txt"
ANNOTATION_NOUN_KEYWORD_FILE = PATTERN_DIR + "annotation_noun_keyword.txt"
EDITING_VERB_KEYWORD_FILE = PATTERN_DIR + "editing_verb_keyword.txt"
TEXT_FILE_NOUN_KEYWORD_FILE = PATTERN_DIR + "text_file_noun_keyword.txt"
CONVENTIONS_AND_STANDARDS_KEYWORD_FILE = PATTERN_DIR + "conventions_and_standards.txt"
CONFORMITY_MODAL = PATTERN_DIR + "conformity_modal.txt"
ORDERING_SYMBOL_FILE = PATTERN_DIR + "ordering_symbol.txt"
CHANGE_INDICATOR_FILE = PATTERN_DIR + "change_indicator.txt"
POSITIVE_OUTCOME_KEYWORD_FILE = PATTERN_DIR + "positive_outcome_keyword.txt"
CODE_CHANGE_TYPE_KEYWORD_FILE = PATTERN_DIR + "code_change_type_keyword.txt"
UNDESIRED_BEHAVIOR_KEYWORD_FILE = PATTERN_DIR + "undesired_behavior_keyword.txt"
PREDEFINED_PROGRAMMING_KEYWORD = PATTERN_DIR + "predefined_programming_keyword.txt"
NEGATION_KEYWORD = PATTERN_DIR + "negation.txt"

fix_defects_keyword_list = getKeywordFromFile(TO_FIX_DEFECTS_KEYWORD_FILE)
test_verb_keyword_lst = getKeywordFromFile(TEST_VERB_KEYWORD_FILE)
annotation_noun_keyword_lst = getKeywordFromFile(ANNOTATION_NOUN_KEYWORD_FILE)
editing_verb_keyword_lst = getKeywordFromFile(EDITING_VERB_KEYWORD_FILE)
text_file_noun_keyword_lst = getKeywordFromFile(TEXT_FILE_NOUN_KEYWORD_FILE)
ordering_symbol_lst = getKeywordFromFile(ORDERING_SYMBOL_FILE)


class WhyCategory(namedtuple("CommitCategory", "name regex_exp"), Enum):
    """
    Enum class for each category, in which name attribute (the first one) is the unique name for the category. And the
    regex_exp is the regular expression of the pattern for the category
    """

    # why_subcategories
    MISSING = "Missing Why", ""
    DESCRIBE_ERROR_SCENARIO = "Describe error scenario", ".*error.*"

    INTRODUCE_ISSUE_PR_REFERENCE = (
        "Introduce issue/PR reference",
        "(?P<link_issue_verb>{})?\W.*?(issue|review)?\W.*?(?P<issue_link>\#\d+)+".format(
            getKeywordFromFile(LINK_ISSUE_VERB_KEYWORD_FILE)
        ),
    )

    OUT_OF_DATE = "Out of date", "({})+\W".format(
        getKeywordFromFile(OUT_OF_DATE_KEYWORD_FILE)
    )

    TO_FIX_DEFECTS = "To fix defects", "({})+".format(fix_defects_keyword_list)

    CONVENTIONS_AND_STANDARDS = "Conventions and standards", "({})*({})+({})*".format(
        getKeywordFromFile(CONFORMITY_MODAL),
        getKeywordFromFile(CONVENTIONS_AND_STANDARDS_KEYWORD_FILE),
        getKeywordFromFile(CONFORMITY_MODAL),
    )

    TEST_CASES = (
        "Test cases",
        "((\S*?test)+\W.*?({})+\W)|(({})+\W.*?(\S*?test)+\W)".format(
            test_verb_keyword_lst, test_verb_keyword_lst
        ),
    )

    TYPOGRAPHIC_FIXES = "Typographic fixes", "(typo|typographic|typograph)+"

    TEXT_FILE_CHANGES = (
        "Text file changes",
        "(({})+\W.*?({})+\W)|(({})+\W.*?({})+\W)".format(
            text_file_noun_keyword_lst,
            editing_verb_keyword_lst,
            editing_verb_keyword_lst,
            text_file_noun_keyword_lst,
        ),
    )

    ANNOTATION_CHANGES = (
        "Annotation changes",
        "(({})+\W.*?({})+\W)|(({})+\W.*?({})+\W)".format(
            annotation_noun_keyword_lst,
            editing_verb_keyword_lst,
            editing_verb_keyword_lst,
            annotation_noun_keyword_lst,
        ),
    )

    def __str__(self) -> str:
        return self.name


class WhatCategory(namedtuple("CommitCategory", "name regex_exp"), Enum):
    """
    Enum class for each category, in which name attribute (the first one) is the unique name for the category. And the
    regex_exp is the regular expression of the pattern for the category
    """

    # what_subcategories
    MISSING = "Missing What", ""
    CHANGE_LIST = (
        "change_list",
        "(^[{}].*)([{}].*)".format(ordering_symbol_lst, ordering_symbol_lst) + "{1,}",
    )

    CONTRAST_BEFORE_AFTER = "contrast_before_after", "{}".format(
        getKeywordFromFile(CHANGE_INDICATOR_FILE)
    )

    CHARACTERISTICS_CHANGE = "characteristics_change", "({})+|({})+({})*".format(
        getKeywordFromFile(POSITIVE_OUTCOME_KEYWORD_FILE),
        getKeywordFromFile(CODE_CHANGE_TYPE_KEYWORD_FILE),
        getKeywordFromFile(UNDESIRED_BEHAVIOR_KEYWORD_FILE),
    )

    ILLUSTRATE_FUNCTION = "illustrate_function", "({})|({}+.*{}+)".format(
        fix_defects_keyword_list,
        getKeywordFromFile(NEGATION_KEYWORD),
        UNDESIRED_BEHAVIOR_KEYWORD_FILE,
    )

    def __str__(self) -> str:
        return self.name


class CommitClassifier:
    def __init__(self, commit_msgs: list[str], verbose: bool = False):
        """
        return list of categories for commit_msg
        """
        self.commit_msgs = commit_msgs
        self.preprocessed_msgs = []
        self.what_subcategory = []
        self.why_subcategory = []
        self.results = None
        self.verbose = verbose

    def preprocess(self):
        """
        preprocess commit_msg
        """
        for commit_msg in self.commit_msgs:
            tokenized_lst = stem_tokenize(commit_msg)
            tokenized_msg = " ".join(tokenized_lst)
            # tokenized_msg = remove_stop_words(tokenized_msg)
            tokenized_msg = denoise(tokenized_msg)
            self.preprocessed_msgs.append(tokenized_msg)
            if self.verbose:
                print(
                    "raw string: {}, preprocessed string: {}\n".format(
                        commit_msg, tokenized_msg
                    )
                )

    def match_category(self, category_factory, commit_msg):
        commit_categories = []
        matched_substrings = []
        matched_pattern = None
        for pattern in category_factory:
            if re.search(pattern.regex_exp, commit_msg):
                if self.verbose:
                    matched_substrings.append(
                        re.findall(pattern.regex_exp, commit_msg)
                    )
                matched_pattern = pattern
        if matched_pattern is None:
            matched_pattern = category_factory.MISSING
        commit_categories.append(matched_pattern.name)
        return commit_categories, matched_substrings

    def classify(self):
        self.preprocess()
        for commit_msg in self.preprocessed_msgs:
            why_commit_categories, why_matched_substrings = self.match_category(WhyCategory, commit_msg)
            what_commit_categories, what_matched_substrings = self.match_category(WhatCategory, commit_msg)
            if self.verbose:
                print(
                    "Preprocessed: {}, Why Categories: {} Why Matched substrings: {}\n What Categories: {} What Matched substrings: {}\n"
                    .format(commit_msg, why_commit_categories, why_matched_substrings, what_commit_categories,
                            what_matched_substrings
                            )
                )
            self.why_subcategory.append(why_commit_categories)
            self.what_subcategory.append(what_commit_categories)
        self.save_results()

    def save_results(self):
        d = {'message': self.commit_msgs,
             'preprocessed': self.preprocessed_msgs,
             'why_subcategory': self.why_subcategory,
             'what_subcategory': self.what_subcategory}
        df = pd.DataFrame(d)
        df['good_classified'] = df.apply(lambda x: len(x.why_subcategory) != 0 and len(x.what_subcategory) != 0
                                                   and WhyCategory.MISSING.name not in x.why_subcategory
                                                   and WhatCategory.MISSING.name not in x.what_subcategory, axis=1)
        self.results = df

    def get_results(self):
        return self.results.copy()

    def pretty_print(self):
        for row in self.results.itertuples(index=True, name='Pandas'):
            print('Message: {}, Preprocessed: {} \nGood:{}, Why Category: {}, What Category: {}\n'.format(
                row.message, row.preprocessed, row.good_classified, row.why_subcategory, row.what_subcategory
            ))


if __name__ == "__main__":
    """
    pipeline for classifying a single commit message
    """
    commit_msg_test = [
        "fixed error feat:",
        "Follow the rule and conventions please",
        "* Add the submit function.\n* Delete the old documentation",
        "revert the change",
        "clearer code documentation",
        "fix crashes in the program",
        "Make the code cleaner",
        "categoryTest add"
    ]

    commit_classifier = CommitClassifier(commit_msg_test, False)
    commit_classifier.classify()
    commit_classifier.pretty_print()
