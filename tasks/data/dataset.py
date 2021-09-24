import luigi
import gokart
from datasets import Dataset


class CreateDataset(gokart.TaskOnKart):
    data_task = gokart.TaskInstanceParameter()
    required_columns = luigi.Parameter(default={'text', 'labels'})
    def run(self):
        df = self.load_data_frame(required_columns=set(self.required_columns), drop_columns=True)
        ds = Dataset.from_pandas(df)
        dataset = ds.train_test_split()
        self.dump(dataset)