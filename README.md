# LSEMS
> This is the manual for LSEMS (Data Hub system)

##Tutorial
This tutorial will lead you through the pipeline with examples of the system's key functionalities.
### Registration
- After connecting to VPN, type <http://10.2.2.31> to open the main page of GitLab for registration.

![gitlab](image/gitlab.png)
### Make a New Project
- Click `new Project` button to make a new project.
- You can find all your projects in GitLab.

![project](image/project.png)

### Enter into Data Hub IPython Notebook Web Server

- After connecting to VPN, type <http://10.2.2.32:7777> to open the data hub IPython Notebook Web Server.

![ipython](image/ipython_main.png)

- The file `sample.ipynb` under the current directory is a tutorial of Data Hub. Click the `new` button on the upper-right corner, you can create a folder named with your Gitlab account name.

![new_folder](image/new_ipython.png)

- Enter the new folder and create an IPython Notebook (click the `Python 2` in the above column). The following view will come up:
![start_ipython](image/start_ipython.png)

### Inspect Data Set

- First, enter directory `~/LSEMS`

![cd_LSEMS](image/cd_LSEMS.png)

- Then, `import query` and create a Query object.

![import_query](image/import_query.png)

- by enter `q.` and press `tab` you can check the `query` functions available.

![q_tab](image/q_tab.png)

- after completion of function name, enter `?` to see related documents and examples. e.g. enter `q.importData?` will get the following information.

![query_docs](image/query_docs.png)

- another e.g. enter `q.showData()` will return the names of registered data sets in the database.

![q_showdata](image/q_showdata.png)

### Inspect Data Set Info and Dependencies

- enter `q.showDescription("data_set_name")` will return the data set's information including dependencies, e.g. `parent` attribute.

![q_showDescription](image/q_showDescription.png)

- Some of the attribute in the description may be complicated, enter the attribute's name for detailed information.

![q_showDescription_commit](image/q_showDescription_commit.png)

- enter `q.showData("data_set_name")` will return the data set's metadata.

![q_showData_all](image/q_showData_all.png)

### Join Operation of Data Sets

- There are circumstances when multiple data sets with the same primary key recorded metadata of same experiment, then we can join them for a better view of the data set.

![q_join](image/q_join.png)

### Experiment Submission

- Initiate experiment repository and prepare the data set.

- Since LSEMS manage "data" and "metadata" separately, you need to download a sample of the experiment data set when you do the coding and testing. Access the FTP server at <ftp://10.2.2.146:12314/> (name: `user`, pass: `abc123`) for these sample datas.

![ftp_1](image/ftp_1.png)

![ftp_2](image/ftp_2.png)

- while submitting code, the repository should have directory structure as follows:

		/exp_name/
				  src/
				 	  example.py
				 	  outAPI.py
				 	  ...
				  exp.json

- where `exp.json` should meet up with following requirements:
    - Required entries:
        - `data_set`: the input data set you are using, which should have been registerd in the database.
        - `src`: the source file of your program, the one will be run by the system.- `type`: the type of language using.
        - `param`: parameters for this run, set an empty dict if none.
    - Optional entries:
        - `out`: name of the data set your code would generate for registation.
- here's an example `exp.json` file:

![exp_json](image/exp_json.png)

- src contains 2 files:
    - `outAPI.py`, the output api provided to suit the system output recording mechanism. (will be providing package support, won't be in use soon)
    - `gedatest.py`, users main experiment code, which will read in a `scv` data set, add a new attribute to it and out put as a new data set.

            from pandas import *
            from outAPI import *

            def main():
                df = read_csv("../data/sentiment_data.tsv", delimiter='\t', quoting=1)
                df['attr'] = range(len(df))
                fp = open('outfile_test.csv', 'w')
                fp.write(df.to_csv())
                fp.close()
                O = Outer()
                O.jout_exp({'description':'testing generation of datasets.'})
                O.generate()

            if __name__ == "__main__":
                main()


##Structure
The system is developed on two open source project:

- [Gitlab](http://about.gitlab.com)
- [MongoDB](http://www.mongodb.org)

with the help of other python packages, such as

- web.py
- pymongo
- pandas

The system contains 4 parts, as shown in the graph.

- User communicate with the ___System Core___ for information and operations, e.g. import data set, get experiment information.
- User manage their experiment codes on ___Gitlab Server___ while each push operation triggers _System Core_ to clone and run the code if necessary.
- The _System Core_ communicates with ___MongoDB Server___ for management of data set and experiment data (metadata).
- The _System Core_ may access to a ___Large Scale Cluster___ for more computational power.

##Pipeline
The code manage and auto-run system runs in a pipeline as shown in the graph.

- User pushes code to GitLab Server, the server POST to system core through web hook.
- System core clones the repository to local directory.
- Read experiment info from `exp.json` and upload it into `users` db in MongoDB server.
- Copy experiment code to sandbox and run.
- Record output metadata from `output.json` into database in MongoDB server.
- Import output dataset (if any) into `datas` db in MongoDB server.
- Finishes.
