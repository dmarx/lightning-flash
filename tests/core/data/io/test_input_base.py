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
import pytest

from flash.core.data.io.input_base import Input, IterableInput
from flash.core.utilities.stages import RunningStage


def test_input_validation():
    with pytest.raises(RuntimeError, match="Use `IterableInput` instead."):

        class InvalidInput(Input):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.data = iter([1, 2, 3])

        InvalidInput(RunningStage.TRAINING)

    class ValidInput(Input):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.data = [1, 2, 3]

    ValidInput(RunningStage.TRAINING)


def test_iterable_input_validation():
    with pytest.raises(RuntimeError, match="Use `Input` instead."):

        class InvalidIterableInput(IterableInput):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.data = [1, 2, 3]

        InvalidIterableInput(RunningStage.TRAINING)

    class ValidIterableInput(IterableInput):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.data = iter([1, 2, 3])

    ValidIterableInput(RunningStage.TRAINING)
