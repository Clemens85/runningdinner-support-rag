class CodeFileReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = filepath.split('/')[-1]

    # def read_lines(self):
    #     with open(self.filepath, 'r') as file:
    #         return file.readlines()

    def read_content(self):
        with open(self.filepath, 'r') as file:
            return file.read()
        
    def to_prompt_format(self):
        content = self.read_content()
        return f"{self.filename}\n{content}"