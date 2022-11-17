from collections import namedtuple
from enum import Enum
from util.CommitUtil import *
from util.FileUtil import getKeywordFromFile
from project_path import ROOT_DIR

TO_FIX_DEFECTS_KEYWORD_FILE = "{}/data/pattern/to_fix_defects_keyword.txt".format(ROOT_DIR)
LINK_ISSUE_VERB_KEYWORD_FILE = "{}/data/pattern/link_issue_verb_keyword.txt".format(ROOT_DIR)
OUT_OF_DATE_KEYWORD_FILE = "{}/data/pattern/out_of_date_keyword.txt".format(ROOT_DIR)
TEST_VERB_KEYWORD_FILE = "{}/data/pattern/test_verb_keyword.txt".format(ROOT_DIR)
ANNOTATION_NOUN_KEYWORD_FILE = "{}/data/pattern/annotation_noun_keyword.txt".format(ROOT_DIR)
EDITING_VERB_KEYWORD_FILE = "{}/data/pattern/editing_verb_keyword.txt".format(ROOT_DIR)
TEXT_FILE_NOUN_KEYWORD_FILE = "{}/data/pattern/text_file_noun_keyword.txt".format(ROOT_DIR)
CONVENTIONS_AND_STANDARDS_KEYWORD_FILE = "{}/data/pattern/conventions_and_standards.txt".format(ROOT_DIR)
ORDERING_SYMBOL_FILE = "{}/data/pattern/ordering_symbol.txt".format(ROOT_DIR)
CHANGE_INDICATOR_FILE = "{}/data/pattern/change_indicator.txt".format(ROOT_DIR)
POSITIVE_OUTCOME_KEYWORD_FILE = "{}/data/pattern/positive_outcome_keyword.txt".format(ROOT_DIR)
CODE_CHANGE_TYPE_KEYWORD_FILE = "{}/data/pattern/code_change_type_keyword.txt".format(ROOT_DIR)
UNDESIRED_BEHAVIOR_KEYWORD_FILE = "{}/data/pattern/undesired_behavior_keyword.txt".format(ROOT_DIR)
PREDEFINED_PROGRAMMING_KEYWORD = "{}/data/pattern/predefined_programming_keyword.txt".format(ROOT_DIR)

test_verb_keyword_lst = getKeywordFromFile(TEST_VERB_KEYWORD_FILE)
annotation_noun_keyword_lst = getKeywordFromFile(ANNOTATION_NOUN_KEYWORD_FILE)
editing_verb_keyword_lst = getKeywordFromFile(EDITING_VERB_KEYWORD_FILE)
text_file_noun_keyword_lst = getKeywordFromFile(TEXT_FILE_NOUN_KEYWORD_FILE)
ordering_symbol_lst = getKeywordFromFile(ORDERING_SYMBOL_FILE)


class CommitCategory(namedtuple('CommitCategory', 'name regex_exp'), Enum):
    """
    Enum class for each category, in which name attribute (the first one) is the unique name for the category. And the
    regex_exp is the regular expression of the pattern for the category
    """
    # why_subcategories
    DESCRIBE_ERROR_SCENARIO = "describe_error_scenario", ".*error.*"
    INTRODUCE_ISSUE_PR_REFERENCE = "introduce_issue_PR_reference", "(?P<link_issue_verb>{})?\W.*?(issue|review)?\W.*?(?P<issue_link>\#\d+)+".format(
        getKeywordFromFile(LINK_ISSUE_VERB_KEYWORD_FILE))

    OUT_OF_DATE = "out_of_date", "({})+\W".format(getKeywordFromFile(OUT_OF_DATE_KEYWORD_FILE))

    TO_FIX_DEFECTS = "to_fix_defects", "({})+".format(getKeywordFromFile(TO_FIX_DEFECTS_KEYWORD_FILE))

    CONVENTIONS_AND_STANDARDS = "conventions_and_standards", "({})+".format(
        getKeywordFromFile(CONVENTIONS_AND_STANDARDS_KEYWORD_FILE))

    ISSUE_LINK = "issue_link", "https"

    TEST_CASES = "test_cases", "((\S*?test)+\W.*?({})+\W)|(({})+\W.*?(\S*?test)+\W)".format(
        test_verb_keyword_lst, test_verb_keyword_lst)
    TYPOGRAPHIC_FIXES = "typographic_fixes", "(typo|typographic|typograph)+"
    TEXT_FILE_CHANGES = "text_file_changes", "(({})+\W.*?({})+\W)|(({})+\W.*?({})+\W)".format(
        text_file_noun_keyword_lst, editing_verb_keyword_lst, editing_verb_keyword_lst, text_file_noun_keyword_lst)
    ANNOTATION_CHANGES = "annotation_changes", "(({})+\W.*?({})+\W)|(({})+\W.*?({})+\W)".format(
        annotation_noun_keyword_lst, editing_verb_keyword_lst, editing_verb_keyword_lst, annotation_noun_keyword_lst)

    # what_subcategories
    CHANGE_LIST = "change_list", "(^[{}].*)([{}].*)".format(ordering_symbol_lst, ordering_symbol_lst) + "{1,}"
    CONTRAST_BEFORE_AFTER = "contrast_before_after", "{}".format(getKeywordFromFile(CHANGE_INDICATOR_FILE))
    CHARACTERISTICS_CHANGE = "characteristics_change", "({})+|({})+({})*".format(
        getKeywordFromFile(POSITIVE_OUTCOME_KEYWORD_FILE), getKeywordFromFile(CODE_CHANGE_TYPE_KEYWORD_FILE),
        getKeywordFromFile(UNDESIRED_BEHAVIOR_KEYWORD_FILE))

    illustrate_function = "illustrate_function", "^((?!{}).)*$".format(
        getKeywordFromFile(PREDEFINED_PROGRAMMING_KEYWORD).lower())

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
            # tokenized_msg = remove_stop_words(tokenized_msg)
            tokenized_msg = denoise(tokenized_msg)
            self.preprocessed_msgs.append(tokenized_msg)
            if self.verbose:
                print('raw string: {}, preprocessed string: {}\n'.format(commit_msg, tokenized_msg))

    def classify(self):
        self.preprocess()
        for commit_msg in self.preprocessed_msgs:
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
        for commit_msg in self.preprocessed_msgs:
            categories = self.commit_category_dict[commit_msg]
            print("Commit Message: {}, Categories: {}".format(commit_msg, ", ".join([str(e) for e in categories])))


if __name__ == "__main__":
    """
    pipeline for classifying a single commit message
    """
    commit_msg_test = ["fixed error feat:", "Follow the rule and conventions please",
                       "* do something.\n* do something else", "revert the change", "clearer code documentation",
                       "fix crashes in the program", "fix crashes in the program, otherwise too fragile",
                       "Make the code cleaner"]

    commit_classifier = CommitClassifier(commit_msg_test, False)
    commit_classifier.classify()
    commit_classifier.pretty_print()
