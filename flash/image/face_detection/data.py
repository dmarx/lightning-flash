# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

import torch
import torch.nn as nn
from torch.utils.data import Dataset

from flash.core.data.io.input import DataKeys, DatasetInput, InputFormat
from flash.core.data.io.input_transform import InputTransform
from flash.core.data.io.output_transform import OutputTransform
from flash.core.data.transforms import ApplyToKeys
from flash.core.data.utils import image_default_loader
from flash.core.utilities.imports import _FASTFACE_AVAILABLE, _TORCHVISION_AVAILABLE
from flash.image.data import ImagePathsInput
from flash.image.detection import ObjectDetectionData

if _TORCHVISION_AVAILABLE:
    import torchvision

if _FASTFACE_AVAILABLE:
    import fastface as ff


def fastface_collate_fn(samples: Sequence[Dict[str, Any]]) -> Dict[str, Sequence[Any]]:
    """Collate function from fastface.

    Organizes individual elements in a batch, calls prepare_batch from fastface and prepares the targets.
    """
    samples = {key: [sample[key] for sample in samples] for key in samples[0]}

    images, scales, paddings = ff.utils.preprocess.prepare_batch(samples[DataKeys.INPUT], None, adaptive_batch=True)

    samples["scales"] = scales
    samples["paddings"] = paddings

    if DataKeys.TARGET in samples.keys():
        targets = samples[DataKeys.TARGET]
        targets = [{"target_boxes": target["boxes"]} for target in targets]

        for i, (target, scale, padding) in enumerate(zip(targets, scales, paddings)):
            target["target_boxes"] *= scale
            target["target_boxes"][:, [0, 2]] += padding[0]
            target["target_boxes"][:, [1, 3]] += padding[1]
            targets[i]["target_boxes"] = target["target_boxes"]

        samples[DataKeys.TARGET] = targets
    samples[DataKeys.INPUT] = images

    return samples


class FastFaceInput(DatasetInput):
    """Logic for loading from FDDBDataset."""

    def load_data(self, data: Dataset, dataset: Any = None) -> Dataset:
        new_data = []
        for img_file_path, targets in zip(data.ids, data.targets):
            new_data.append(
                super().load_sample(
                    (
                        img_file_path,
                        dict(
                            boxes=targets["target_boxes"],
                            # label `1` indicates positive sample
                            labels=[1 for _ in range(targets["target_boxes"].shape[0])],
                        ),
                    )
                )
            )

        return new_data

    def load_sample(self, sample: Any, dataset: Optional[Any] = None) -> Mapping[str, Any]:
        filepath = sample[DataKeys.INPUT]
        img = image_default_loader(filepath)
        sample[DataKeys.INPUT] = img

        w, h = img.size  # WxH
        sample[DataKeys.METADATA] = {
            "filepath": filepath,
            "size": (h, w),
        }

        return sample


class FaceDetectionInputTransform(InputTransform):
    """Applies default transform and collate_fn for fastface on FastFaceDataSource."""

    def __init__(
        self,
        train_transform: Optional[Dict[str, Callable]] = None,
        val_transform: Optional[Dict[str, Callable]] = None,
        test_transform: Optional[Dict[str, Callable]] = None,
        predict_transform: Optional[Dict[str, Callable]] = None,
        image_size: Tuple[int, int] = (128, 128),
    ):
        self.image_size = image_size

        super().__init__(
            train_transform=train_transform,
            val_transform=val_transform,
            test_transform=test_transform,
            predict_transform=predict_transform,
            inputs={
                InputFormat.FILES: ImagePathsInput(),
                InputFormat.FOLDERS: ImagePathsInput(),
                InputFormat.DATASETS: FastFaceInput(),
            },
            default_input=InputFormat.FILES,
        )

    def get_state_dict(self) -> Dict[str, Any]:
        return {**self.transforms}

    @classmethod
    def load_state_dict(cls, state_dict: Dict[str, Any], strict: bool = False):
        return cls(**state_dict)

    def default_transforms(self) -> Dict[str, Callable]:
        return {
            "to_tensor_transform": nn.Sequential(
                ApplyToKeys(DataKeys.INPUT, torchvision.transforms.ToTensor()),
                ApplyToKeys(
                    DataKeys.TARGET,
                    nn.Sequential(
                        ApplyToKeys("boxes", torch.as_tensor),
                        ApplyToKeys("labels", torch.as_tensor),
                    ),
                ),
            ),
            "collate": fastface_collate_fn,
        }


class FaceDetectionOutputTransform(OutputTransform):
    """Generates preds from model output."""

    @staticmethod
    def per_batch_transform(batch: Any) -> Any:
        scales = batch["scales"]
        paddings = batch["paddings"]

        batch.pop("scales", None)
        batch.pop("paddings", None)

        preds = batch[DataKeys.PREDS]

        # preds: list of torch.Tensor(N, 5) as x1, y1, x2, y2, score
        preds = [preds[preds[:, 5] == batch_idx, :5] for batch_idx in range(len(preds))]
        preds = ff.utils.preprocess.adjust_results(preds, scales, paddings)
        batch[DataKeys.PREDS] = preds

        return batch


class FaceDetectionData(ObjectDetectionData):
    input_transform_cls = FaceDetectionInputTransform
    output_transform_cls = FaceDetectionOutputTransform
