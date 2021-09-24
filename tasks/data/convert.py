import luigi
import gokart

class ConvertCategoryToLabel(gokart.TaskOnKart):
    data_task = gokart.TaskInstanceParameter(description='A task outputs pd.DataFrame.')
    target_column = luigi.Parameter()  # type: str
    rename_to = luigi.Parameter(default='labels')  # type: str
    output_file_path = luigi.Parameter(default='data/convert_category_to_label.pkl')  # type: str

    def output(self):
        return self.make_target(self.output_file_path)

    def run(self):
        df = self.load_data_frame()
        df[self.rename_to] = df[self.target_column].astype('category').cat.codes
        self.dump(df)
        

class NumOfCategories(gokart.TaskOnKart):
    data_task = gokart.TaskInstanceParameter(description='A task outputs pd.DataFrame.')
    column_name = luigi.Parameter(default='category')
    def run(self):
        df = self.load()
        self.dump(len(df[self.column_name].unique()))