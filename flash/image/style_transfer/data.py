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
import functools
import pathlib
from typing import Any, Callable, Dict, Optional, Sequence, Union

from torch import nn

from flash.core.data.data_module import DataModule
from flash.core.data.io.input import DataKeys, InputFormat
from flash.core.data.io.input_transform import InputTransform
from flash.core.data.transforms import ApplyToKeys
from flash.core.utilities.imports import _TORCHVISION_AVAILABLE
from flash.image.classification import ImageClassificationData
from flash.image.data import ImageNumpyInput, ImagePathsInput, ImageTensorInput
from flash.image.style_transfer.utils import raise_not_supported

if _TORCHVISION_AVAILABLE:
    from torchvision import transforms as T

__all__ = ["StyleTransferInputTransform", "StyleTransferData"]


def _apply_to_input(
    default_transforms_fn, keys: Union[Sequence[DataKeys], DataKeys]
) -> Callable[..., Dict[str, ApplyToKeys]]:
    @functools.wraps(default_transforms_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Optional[Dict[str, ApplyToKeys]]:
        default_transforms = default_transforms_fn(*args, **kwargs)
        if not default_transforms:
            return default_transforms

        return {hook: ApplyToKeys(keys, transform) for hook, transform in default_transforms.items()}

    return wrapper


class StyleTransferInputTransform(InputTransform):
    def __init__(
        self,
        train_transform: Optional[Dict[str, Callable]] = None,
        val_transform: Optional[Dict[str, Callable]] = None,
        test_transform: Optional[Dict[str, Callable]] = None,
        predict_transform: Optional[Dict[str, Callable]] = None,
        image_size: int = 256,
    ):
        if val_transform:
            raise_not_supported("validation")
        if test_transform:
            raise_not_supported("test")

        if isinstance(image_size, int):
            image_size = (image_size, image_size)

        self.image_size = image_size

        super().__init__(
            train_transform=train_transform,
            val_transform=val_transform,
            test_transform=test_transform,
            predict_transform=predict_transform,
            inputs={
                InputFormat.FILES: ImagePathsInput(),
                InputFormat.FOLDERS: ImagePathsInput(),
                InputFormat.NUMPY: ImageNumpyInput(),
                InputFormat.TENSORS: ImageTensorInput(),
                InputFormat.TENSORS: ImageTensorInput(),
            },
            default_input=InputFormat.FILES,
        )

    def get_state_dict(self) -> Dict[str, Any]:
        return {**self.transforms, "image_size": self.image_size}

    @classmethod
    def load_state_dict(cls, state_dict: Dict[str, Any], strict: bool = False):
        return cls(**state_dict)

    @functools.partial(_apply_to_input, keys=DataKeys.INPUT)
    def default_transforms(self) -> Optional[Dict[str, Callable]]:
        if self.training:
            return dict(
                to_tensor_transform=T.ToTensor(),
                per_sample_transform_on_device=nn.Sequential(
                    T.Resize(self.image_size),
                    T.CenterCrop(self.image_size),
                ),
            )
        if self.predicting:
            return dict(
                pre_tensor_transform=T.Resize(self.image_size),
                to_tensor_transform=T.ToTensor(),
            )
        # Style transfer doesn't support a validation or test phase, so we return nothing here
        return None


class StyleTransferData(ImageClassificationData):
    input_transform_cls = StyleTransferInputTransform

    @classmethod
    def from_folders(
        cls,
        train_folder: Optional[Union[str, pathlib.Path]] = None,
        predict_folder: Optional[Union[str, pathlib.Path]] = None,
        train_transform: Optional[Union[str, Dict]] = None,
        predict_transform: Optional[Union[str, Dict]] = None,
        input_transform: Optional[InputTransform] = None,
        **kwargs: Any,
    ) -> "DataModule":

        if any(param in kwargs and kwargs[param] is not None for param in ("val_folder", "val_transform")):
            raise_not_supported("validation")

        if any(param in kwargs and kwargs[param] is not None for param in ("test_folder", "test_transform")):
            raise_not_supported("test")

        input_transform = input_transform or cls.input_transform_cls(
            train_transform=train_transform,
            predict_transform=predict_transform,
        )

        return cls.from_input(
            InputFormat.FOLDERS,
            train_data=train_folder,
            predict_data=predict_folder,
            input_transform=input_transform,
            **kwargs,
        )
