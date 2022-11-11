def getKeywordFromFile(file_path: str) -> str:
    f = open(file_path)
    keywords = f.read().splitlines()
    return "|".join(keywords)
