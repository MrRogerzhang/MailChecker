"""
@Author: peviroy
@Date: 2020-09-08
@Last Modified by: peviroy
@Last Modified time: 2020-09-08 23:56
"""
import os
import numpy as np
import torch
import torch.nn.utils.rnn as rnn_utils

from dataset import get_sms_dataset


class SMSTransform():
    '''
    Transform text data into correct form:
        tensor([[55, 11, 51, 35, 17,  9, 38, 32,  4, 12, 43, 39, 25, 45, 10, 47,  0,  0,
          0,  0,  0,  0,  0,  0,  0],....])
        Integer means idx of words_dict, zero means none
        In the type of torch.Tensor
    '''

    def __init__(self, word_dict_dir='./checkpoints'):
        super(SMSTransform, self).__init__()
        WORD_DICT_NAME = 'word_dict.npy'
        self.word_dict_path = os.path.join(word_dict_dir, WORD_DICT_NAME)
        if word_dict_dir != '':
            try:
                self.word_dict = np.load(
                    self.word_dict_path, allow_pickle=True).item()
            except FileNotFoundError:
                self.word_dict = None

    def __call__(self, texts, targets=None):
        out_texts, word_dict = self.vectorize(texts)
        out_texts = self.pad_sequence(out_texts)
        out_targets = self.to_tensor(targets)
        if self.word_dict is None:
            np.save(self.word_dict_path, word_dict)
        return out_texts, out_targets, word_dict

    def vectorize(self, texts):
        if self.word_dict is not None:
            word_dict = self.word_dict
        else:
            word_list = " ".join(texts).split()
            word_list = list(set(word_list))
            # i+1 to avoid encode zero
            word_dict = {w: i + 1 for i, w in enumerate(word_list)}

        vec_texts = []
        for text in texts:
            vec_texts.append(torch.LongTensor(np.asarray(
                [word_dict[n] for n in text.split()])))

        return vec_texts, word_dict

    @staticmethod
    def pad_sequence(vec_texts):
        data = rnn_utils.pad_sequence(
            vec_texts, batch_first=True, padding_value=0)
        return data

    @staticmethod
    def to_tensor(ls: list):
        if ls is None:
            return None
        return torch.LongTensor([out for out in ls])


class SMSDataset(torch.utils.data.Dataset):
    def __init__(self, transform=SMSTransform(), file_path='data/spam.csv'):
        data_df = get_sms_dataset(SMS_DATASET=file_path)
        texts, targets = data_df.message.to_list(), data_df.target.to_list()
        self.texts, self.targets, self.word_dict = transform(texts, targets)

    def __getitem__(self, idx):
        return self.texts[idx], self.targets[idx]

    def __len__(self):
        return len(self.texts)
