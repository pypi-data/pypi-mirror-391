import numpy as np
from ml4cps import tools
from torch.utils.data import Dataset, DataLoader
import torch


class WindowedSequenceDataset(Dataset):
    def __init__(self, sequences, window_size=1, window_stride=1, pairs=False):
        """
        sequences: list of 2D tensors (seq_len, num_features)
        window_size: int
        stride: int
        random_sampling: bool → if True, samples randomly
        num_random_windows: int → number of random samples per epoch (only for random_sampling=True)
        """
        self.sequences = tools.window(sequences, window_size, window_stride)
        self.sequence_start = np.cumsum([0] + [s.shape[0] for s in self.sequences])[:-1]
        self.sequence_finish = np.cumsum([0] + [s.shape[0] for s in self.sequences])[1:]
        self.sequences = torch.cat(self.sequences, dim=0)
        self.window_size = window_size
        self.window_stride = window_stride
        self.pairs = pairs


    def __len__(self):
        if self.pairs:
            return self.sequences.shape[0] - self.window_size - 1
        else:
            return self.sequences.shape[0] - self.window_size

    def __getitem__(self, idx):
        # if self.random_sampling:
            # start = torch.randint(0, self.cum_sum_sequence_lengths[-1], 1).item()
            # seq_idx = np.cumsum((start > self.cum_sum_sequence_lengths))
            # start = start - self.cum_sum_sequence_lengths[seq_idx]
            # Random index
            # rand_idx = torch.randint(0, self.sequences.shape[0], (1,)).item()
            # Get the random row
            # return self.sequences[rand_idx]
        # else:
        if self.pairs:
            past_source = self.sequences[idx, :, :]
            past_destination = self.sequences[idx + self.window_size, :, :]
            source = self.sequences[idx+1, :, :]
            destination = self.sequences[idx+1 + self.window_size, :, :]
            return past_source, past_destination, source, destination
        else:
            source = self.sequences[idx, :, :]
            destination = self.sequences[idx + self.window_size, :, :]
        return source, destination


    def windowed_sequences(self):
        return [[self.sequences[start:finish - 2 * self.window_size + 1, :],
                 self.sequences[start+self.window_size:finish - self.window_size +1, :]]
                for start, finish in zip(self.sequence_start, self.sequence_finish)]

    def get_random_sample(self, num_examples=10000):
        return self[torch.randint(0, len(self), (num_examples,))]


    def normalize(self, variables=None, mean=None, std=None):
        if variables is None:
            variables = np.arange(0, self.sequences[0].shape[1])
        if mean is None:
            mean = self.sequences[:,:,variables].mean(dim=[0, 1], keepdim=True)
        if std is None:
            std = self.sequences[:,:,variables].std(dim=[0, 1], keepdim=True)

        self.sequences[:, :, variables] = (self.sequences[:, :, variables] - mean) / std
        return mean, std

def load_data_from_dataset(dataset, sample_size=1000, shufle=True):
    temp_loader = DataLoader(dataset, batch_size=min(sample_size, len(dataset)), shuffle=shufle)
    return next(iter(temp_loader))