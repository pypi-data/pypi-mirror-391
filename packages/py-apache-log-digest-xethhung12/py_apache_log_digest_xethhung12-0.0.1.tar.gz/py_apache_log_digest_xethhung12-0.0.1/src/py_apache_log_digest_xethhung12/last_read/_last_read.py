import json
from dataclasses import dataclass
import os

    
class LastRead:
    def __init__(self, file, repo):
        self.file=file
        self.repo=repo
        self.staged=None

    @staticmethod
    def tryRead(file: str, repo: str):
        if not os.path.exists(repo):
            with open(repo, "w", encoding='utf-8') as f:
                f.write(json.dumps({}, indent=2))
        
        with open(repo, "r", encoding='utf-8') as f:
            repo_data = json.load(f)
            if file in repo_data:
                last_read=repo_data[file]
                return last_read
            else:
                return None

    @staticmethod
    def saveRead(file: str, repo: str, data: dict):
        if not os.path.exists(repo):
            with open(repo, "w", encoding='utf-8') as f:
                f.write(json.dumps({}, indent=2))
        
        with open(repo, "r", encoding='utf-8') as f:
            repo_data = json.load(f)
        repo_data.update({file: data})
        with open(repo, "w", encoding='utf-8') as f:
            f.write(json.dumps(repo_data, indent=2))

    def read(self, process):
        file = self.file
        repo = self.repo
        staged = LastRead.tryRead(file, repo)
        f = open(file, "r", encoding='utf-8')
        if staged is None:
            print("Start from new")
            staged={"last_line": 0, "last_line_len":0, "total": 0}
        else:
            print(f"Start from {staged["last_line"]}")
        
        s = os.path.getsize(file)

        if s < staged['total']:
            print("Reset for new file")
            staged={"last_line": 0, "last_line_len":0, "total": 0}
        
        if s > staged['total']:
            to_be_skipped=staged["last_line"]
            sum = 0
            for l in f:
                length=len(l)
                last_line_len=staged["last_line_len"]
                if to_be_skipped > 0:
                    sum += length
                    to_be_skipped-=1
                    if to_be_skipped == 0 and length > last_line_len:
                        staged["last_line_len"]=length
                        yield process(l)
                    continue

                sum += length
                yield process(l)
                staged["last_line_len"]=length
                staged["last_line"]+=1
            staged['total']=sum
        self.staged=staged

    def save_this(self):
        LastRead.saveRead(self.file, self.repo, self.staged)
       
        # return staged


