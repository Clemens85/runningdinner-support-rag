class RecursiveFilepathCollector:
    def __init__(self, base_path):
        self.base_path = base_path

    def collect_filepaths(self):
        import os
        filepaths = []
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                filepaths.append(os.path.join(root, file))
        return filepaths