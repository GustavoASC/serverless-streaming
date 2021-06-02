class Music:
    def __init__(self):
        self.name = ""
        self.author = ""
        self.binary_content = []

    def name(self, name):
        self.name = name
        return self

    def author(self, author):
        self.author = author
        return self

    def binary_content(self, binary_content):
        self.binary_content = binary_content
        return self

