from pathlib import Path
import pandas as pd
import luigi
import gokart
import urllib
import tarfile

class DownloadLivedoorCourpus(gokart.TaskOnKart):
    url: str = "https://www.rondhuit.com/download/ldcc-20140209.tar.gz"
    def run(self):
        dir = self.local_temporary_directory
        Path(dir).mkdir(exist_ok=True)
        local_filename, headers = urllib.request.urlretrieve(self.url, dir + "ldcc-20140209.tar.gz")
        extract_dir = self.local_temporary_directory + "ldcc-20140209"
        with tarfile.open(local_filename, "r:gz") as tar:
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, extract_dir)
        self.dump(extract_dir)


class LivedoorCourpusData(gokart.TaskOnKart):
    def requires(self):
        return DownloadLivedoorCourpus()
    def output(self):
        return self.make_target("livedoor/data.parquet")
    def run(self):
        extract_dir = Path(self.load())
        df = pd.DataFrame(columns=["category", "url", "time", "title", "text"])
        for txt_path in extract_dir.glob('text/*/*.txt'):
            file_name = txt_path.name
            category_name = txt_path.parent.name

            if file_name in ["CHANGES.txt", "README.txt", "LICENSE.txt"]:
                continue

            text_all = txt_path.read_text()
            text_lines = text_all.split("\n")
            url, time, title, *article = text_lines
            article = "\n".join(article)

            df.loc[file_name] = [category_name, url, time, title, article]

        df.reset_index(inplace=True)
        df.rename(columns={"index": "filename"}, inplace=True)
        self.dump(df)
        
class LivedoorCourpusNumOfCategories(gokart.TaskOnKart):
    def requires(self):
        return LivedoorCourpusData()
    def run(self):
        df = self.load()
        self.dump(len(df.category.unique()))