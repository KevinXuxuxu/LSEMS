import data

class Query:
    def __init__(self, name):
        self.data = data.Database()
        self.user = data.Database(db = "users")
        self.name = name

    def showData(self, dataName = None, attribute = None):
        '''
        Show all the name of data sets or one specific data set.

        Parameters
        ----------
        dataName : str
            The name of one specific data set.

        attribute : str
            The attribute of thie data set.

        Example
        ----------
        >>> showData()
        >>> showData("sentiment_data")
        >>> showData("testData", "sentiment")
        '''
        import pandas as pd
        if dataName == None:
            return pd.DataFrame(self.data.DB.collection_names())
        else:
            dataset = self.data.get_data(dataName)
            res = pd.DataFrame(dataset.show_all()[1:])
            if attribute == None:
                return res
            else:
                return pd.concat([res["id"], pd.DataFrame(res[attribute].tolist())], axis=1)

    def showDataDescription(self, dataName = None, attribute = None):
        '''
        Show the description of one data set.

        Parameters
        ----------
        dataName : str
            The name of this data set.
        attribute : str
            The attribute of your data description

        Example
        ----------
        >>> showDataDescription("sentiment_data")
        >>> showDataDescription("testData", attribute = "commit_ids")
        '''
        import pandas as pd
        dataset = self.data.get_data(dataName)
        if attribute == None:
            return pd.DataFrame(dataset.show_all()[:1])
        else:
            return pd.DataFrame(pd.DataFrame(dataset.show_all()[:1])[attribute][0])

    def showUser(self):
        '''
        Show all the users in the system.

        Example
        ----------
        >>> showUser()
        '''
        import pandas as pd
        return pd.DataFrame(self.user.DB.collection_names())

    def showMyExp(self, exp_name = None, attribute = None):
        '''
        Show all your experiment records

        Parameters
        ----------
        exp_name : str
            The name of your experiment
        attribute : str
            The attribute of your experiment information

        Example
        ----------
        >>> showMyExp()
        >>> showMyExp('gedatest')
        '''
        u = self.user.get_data(self.name)
        import pandas as pd
        df = pd.DataFrame(u.show_all())
        if exp_name == None:
            return df
        else:
            if attribute == None:
                return pd.DataFrame(u.show_all()[df[df["exp_name"] == exp_name].index[0]]["exp_records"])
            else:
                return pd.DataFrame(pd.DataFrame(u.show_all()[df[df["exp_name"] == exp_name].index[0]]["exp_records"])[attribute])


    def importData(self, dataName = None, description = "", parent = "", ignore = [], it = None, _type = ""):
        '''
        Import your data set into system.

        Parameters
        ----------
        dataName : str
            The name of your data set (with dir path).
        description : str
            The description of this data set.
        parent : str
            Paratent data set of this new data set.
        ignore : list
            Attributes that want to be ignored.
        it : class file
            The python class to import data iterativly.
        _type : str
            The type of import data set.

        Example
        ----------
        >>> ImportData("sentiment_result2.csv", parent="sentiment_result1_data", ignore=["review"])
        '''
        self.data.import_data(dataName, description, parent, ignore, it, _type)

    def joinView(self, dataName, name_list, key):
        '''
        Joint two or more datasets with a specific key.

        Parameters
        ----------
        dataName : str
            The name of dataset you want to be joined
        name_list : list
            The name list of datasets you want to join
        key : str
            The primary key

        Example
        ----------
        >>> joinView("sentiment_result2", name_list=['sentiment_data'], key='id')
        '''
        import data
        v = data.View(self.data, dataName, name_list = name_list, key = key)
        joint_view = v.dump()
        import pandas as pd
        return pd.DataFrame(joint_view[1:])


    def diffExp(self, expName = None):
        '''
        Check the difference between the last two experiments.

        Parameters
        ----------
        expName : str
            The name of your experiment.

        Example
        ----------
        >>> diffExp("gedatest")
        '''
        u = self.user.get_data(self.name)
        return u.diff(expName)


'''
q = Query("Bob")
q.showData()
q.showDataDescription("sentiment_result2")
q.showDataDescription("testData", "commit_ids")
q.diffExp("gedatest")
'''
'''
q.showData("sentiment_data")
q.joinView("sentiment_result2", name_list=['sentiment_data'], key='id')
q.showUser()
q.showMyExp()
q.showMyExp(exp_name = "gedatest")
'''
