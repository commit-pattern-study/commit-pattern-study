import os
import pandas as pd
import ast

from classfier.CommitClassfier import CommitClassifier

categories = ['why_category', 'why_subcategory', 'what_category', 'what_subcategory']


def trim_category(category_series):
    trimmed_categories = []
    for category in category_series:
        category_lst = category.split("; ")
        category_lst = [name.replace(u'\ufeff', '') for name in category_lst]
        trimmed_categories.append(category_lst)
    return trimmed_categories


def preprocess_data(file_name: str) -> pd.DataFrame:
    df = pd.read_csv(file_name)
    df = df.iloc[:, :9].dropna(how='any', axis=0)
    assert not df.isnull().values.any()
    df = df.apply(lambda x: trim_category(x) if x.name in ['why_category', 'why_subcategory', 'what_category',
                                                           'what_subcategory'] else x)
    return df


def prepare_train_test_sets(train_file, test_file):
    train_df = preprocess_data(train_file)
    test_df = preprocess_data(test_file)
    test_df.to_excel('test_set.xlsx', index=False)
    train_df.to_excel('train_set.xlsx', index=False)


def get_train_test_set(train_file, test_file):
    train_df = pd.read_excel(train_file, index_col=None)
    test_df = pd.read_excel(test_file, index_col=None)
    train_df.iat[241, 4] = '+ Stock Photos Tools \nStock Photos Tools \nZoommy'
    assert not train_df['message'].isna().any()
    for col in categories:
        train_df[col] = train_df[col].apply(lambda x: ast.literal_eval(x))
        test_df[col] = test_df[col].apply(lambda x: ast.literal_eval(x))
    print('train set size: {}, test set size: {}'.format(train_df.shape, test_df.shape))
    return train_df, test_df


class ClassifierEvaluation:
    def __init__(self, train_data, test_data):
        self.train_data = train_data
        self.test_data = test_data
        self.train_classifer = None
        self.test_classifer = None
        self.train_results = None
        self.test_results = None

    def classify(self):
        self.train_classifer = CommitClassifier(self.train_data['message'], False)
        self.train_classifer.classify()
        self.test_classifer = CommitClassifier(self.test_data['message'], False)
        self.test_classifer.classify()
        self.train_results = self.train_classifer.get_results()
        self.test_results = self.test_classifer.get_results()


def get_acc(results, ground_truth):
    acc = []
    for true_category, classified_category in zip(ground_truth['why_subcategory'],
                                                  results['why_subcategory']):
        acc.append(any(item in classified_category for item in true_category))
    print('# of correctly labelled: {}, total: {}, acc: {}'.format(sum(acc), len(acc), sum(acc) / len(acc)))
    return sum(acc) / len(acc)


if __name__ == '__main__':
    os.chdir('../../data/eval')
    # prepare_train_test_sets('train_set.csv', 'test_set.csv')
    train_df, test_df = get_train_test_set('train_set.xlsx', 'test_set.xlsx')
    classifer_evaluation = ClassifierEvaluation(train_df, test_df)
    classifer_evaluation.classify()
    acc_train = get_acc(classifer_evaluation.train_results, classifer_evaluation.train_data)
    acc_test = get_acc(classifer_evaluation.test_results, classifer_evaluation.test_data)
