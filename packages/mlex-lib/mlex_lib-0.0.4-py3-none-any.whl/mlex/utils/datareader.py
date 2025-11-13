import pandas as pd


class DataReader():
    def __init__(self, data_path, target_columns, filter_dict=None, dtype_dict=None, preprocessing_func=None):
        self.data_path = data_path
        self.target_columns = target_columns if isinstance(target_columns, list) else [target_columns]
        self.filter_dict = filter_dict
        self.X = None
        self.y = None

        self.dtype_dict = dtype_dict
        self.preprocessing_func = preprocessing_func

    def read_df(self):
        df = pd.read_csv(
            self.data_path,
            sep=';',
            decimal=',',
            dtype=self.dtype_dict,
            low_memory=False
        )

        df = df.loc[~df.duplicated()]

        if self.preprocessing_func:
            df = self.preprocessing_func(df)

        if self.filter_dict:
            for col, val in self.filter_dict.items():
                df = df[df[col] == val]

        return df.reset_index(drop=True)

    def get_X_y(self):
        df = self.read_df()
        self.y = df[self.target_columns]
        self.X = df.drop(columns=self.target_columns, axis=1)
        return self.X, self.y

    def get_X(self):
        return self.X

    def get_y(self):
        return self.y
