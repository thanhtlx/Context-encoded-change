**Generate Context-encoded change** 

1. **Requirement**

   Repo 

   - cloned in  folder ../repo

   Library 

     -  ```pip install -r requirements.txt```

2. **Get commit message**

   Get all commit message and commit hash of repos in folder ../repo

   ```python get_commit_message.py```
   
3. **Get commit info**

   Use Pydriller to get information of a commit including source code before, after, git diff, line added, line deleted

   ```python get_commit_info.py```

4. **Gen Code property graph**

   Use Joern to parse Code property graph of each version source code 

   ```python parser_cpg.py```

5. **Generate Context-encoded change**

   From cpg to extract all statement that have impact or are impacted to changed code
   
   ```python generate_data.py```

6. **convert to State-Of-The-Art  format**

   ```python convert_data.py```
