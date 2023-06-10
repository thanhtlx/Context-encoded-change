**generate dataset** 

**require**
   repo 
      cloned in  folder ../repo
   library 
      pip install -r requirements.txt 

1. **get commit message**
   get all commit message and commit hash of repos in folder ../repo
   ```python get_commit_message.py```
   
2. **get commit info**
   use pydriller to get information of a commit including source code before, after, git diff, line added, line deleted
   file get_commit_info.py (function main())

3. **parser pdg**
   use joern to parse Code property graph of each version source code 

   python parser_cpg.py

4. **generate pdg data**
   from cpg to extract all statement that have impact or are impacted to changed code
   python generate_data.py

5. **convert to State-Of-The-Art  format**
   python convert_data.py
