class RecursiveFilepathCollector:
    def __init__(self, base_path):
        self.base_path = base_path

    def collect_filepaths(self):
        import os
        filepaths = []
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".bin", ".exe", ".dll", ".class", ".pyc")):
                    continue
                if "/news/" in file_path:
                    continue
                filepaths.append(file_path)
        return filepaths