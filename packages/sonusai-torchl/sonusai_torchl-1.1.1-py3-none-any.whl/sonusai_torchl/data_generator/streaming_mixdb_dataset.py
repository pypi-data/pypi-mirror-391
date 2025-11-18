from sonusai.datatypes import Feature
from sonusai.datatypes import GeneralizedIDs
from sonusai.datatypes import TruthsDict
from sonusai.mixture import MixtureDatabase
from torch.utils.data import DataLoader
from torch.utils.data import IterableDataset


class StreamingMixtureDatabaseDataset(IterableDataset):
    """Generates a PyTorch dataset from a SonusAI mixture database which streams one frame at a time"""

    def __init__(self, mixdb: MixtureDatabase, mixids: GeneralizedIDs):
        """Initialization"""
        self.mixdb = mixdb
        self.mixids = self.mixdb.mixids_to_list(mixids)
        self.current_mixid = 0
        self._get_next_mixture()

    def _get_next_mixture(self) -> None:
        """Get the next mixture"""
        if self.current_mixid >= len(self.mixids):
            raise StopIteration

        feature, truth = self.mixdb.mixture_ft(self.mixids[self.current_mixid])
        self.current_mixid += 1
        self.current_mixture = feature, truth
        self.current_mixture_len = feature.shape[0]
        self.frame_index = 0

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Feature, TruthsDict]:
        """Get next frame data from one mixture"""
        if self.current_mixture is None or self.frame_index >= self.current_mixture_len:
            self._get_next_mixture()

        feature_frame = self.current_mixture[0][self.frame_index, :]
        truth_frame = self.current_mixture[1]
        for category in truth_frame:
            for key in truth_frame[category]:
                if not key.startswith("nf_"):
                    truth_frame[category][key] = truth_frame[category][key][self.frame_index, :]

        self.frame_index += 1

        return feature_frame, truth_frame


def TorchFromStreamingMixtureDatabase(
    mixdb: MixtureDatabase,
    mixids: GeneralizedIDs,
    batch_size: int,
    num_workers: int = 0,
    drop_last: bool = False,
    shuffle: bool = False,
    pin_memory: bool = False,
) -> DataLoader:
    """Generates a PyTorch dataloader from a SonusAI mixture database"""
    dataset = StreamingMixtureDatabaseDataset(
        mixdb=mixdb,
        mixids=mixids,
    )

    result = DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        pin_memory=pin_memory,
        shuffle=shuffle,
        drop_last=drop_last,
        num_workers=num_workers,
    )

    return result
