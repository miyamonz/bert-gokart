import luigi
import gokart
from transformers import BertConfig, BertForPreTraining, BertForSequenceClassification

class LoadBertConfig(gokart.TaskOnKart):
    num_labels = luigi.IntParameter()
    vocab_size = luigi.IntParameter(default=32000)
    
    def output(self):
        return self.make_target('bert/config.pkl')

    def run(self):
        # configの用意 (語彙数は30522 -> 32000に修正しておく)
        bertconfig = BertConfig.from_pretrained('bert-base-uncased',
                                                num_labels=self.num_labels,
                                                output_attentions = False,
                                                output_hidden_states = False,
                                               )
        bertconfig.vocab_size = self.vocab_size
        self.dump(bertconfig)

class LoadBertForSequenceClassification(gokart.TaskOnKart):
    model_dir = luigi.Parameter()
    base_ckpt = luigi.Parameter()
    config_task = gokart.TaskInstanceParameter()

    def output(self):
        return self.make_target('bert/model-for-sequence_classification.pkl')

    def run(self):
        bertconfig = self.load()
        # BERTモデルの"ガワ"の用意 (全パラメーターはランダムに初期化されている)
        pretrained = BertForPreTraining(bertconfig)
        # TensorFlowモデルの重み行列を読み込む (数分程度かかる場合がある)
        pretrained.load_tf_weights(bertconfig, self.model_dir + self.base_ckpt)
        
        tmp_dir = self.local_temporary_directory
        pretrained.save_pretrained(tmp_dir)
        model = BertForSequenceClassification.from_pretrained(tmp_dir)
        self.dump(model)