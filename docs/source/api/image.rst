###########
flash.image
###########

.. contents::
    :depth: 1
    :local:
    :backlinks: top

.. currentmodule:: flash.image

Classification
______________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~classification.model.ImageClassifier
    ~classification.data.ImageClassificationData
    ~classification.data.ImageClassificationInputTransform

    classification.data.MatplotlibVisualization

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template:

    classification.transforms.default_transforms
    classification.transforms.train_default_transforms

Object Detection
________________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~detection.model.ObjectDetector
    ~detection.data.ObjectDetectionData

    detection.data.FiftyOneParser
    detection.data.ObjectDetectionFiftyOneInput
    detection.output.FiftyOneDetectionLabels
    detection.data.ObjectDetectionInputTransform

Keypoint Detection
__________________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~keypoint_detection.model.KeypointDetector
    ~keypoint_detection.data.KeypointDetectionData

    keypoint_detection.data.KeypointDetectionInputTransform

Instance Segmentation
_____________________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~instance_segmentation.model.InstanceSegmentation
    ~instance_segmentation.data.InstanceSegmentationData

    instance_segmentation.data.InstanceSegmentationInputTransform

Embedding
_________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~embedding.model.ImageEmbedder

Segmentation
____________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~segmentation.model.SemanticSegmentation
    ~segmentation.data.SemanticSegmentationData
    ~segmentation.data.SemanticSegmentationInputTransform

    segmentation.data.SegmentationMatplotlibVisualization
    segmentation.data.SemanticSegmentationNumpyInput
    segmentation.data.SemanticSegmentationTensorInput
    segmentation.data.SemanticSegmentationPathsInput
    segmentation.data.SemanticSegmentationFiftyOneInput
    segmentation.data.SemanticSegmentationDeserializer
    segmentation.model.SemanticSegmentationOutputTransform
    segmentation.output.FiftyOneSegmentationLabels
    segmentation.output.SegmentationLabels

.. autosummary::
    :toctree: generated/
    :nosignatures:

    segmentation.transforms.default_transforms
    segmentation.transforms.prepare_target
    segmentation.transforms.train_default_transforms

Style Transfer
______________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~style_transfer.model.StyleTransfer
    ~style_transfer.data.StyleTransferData
    ~style_transfer.data.StyleTransferInputTransform

.. autosummary::
    :toctree: generated/
    :nosignatures:

    ~style_transfer.utils.raise_not_supported

flash.image.data
________________

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: classtemplate.rst

    ~data.ImageDeserializer
    ~data.ImageFiftyOneInput
    ~data.ImageNumpyInput
    ~data.ImagePathsInput
    ~data.ImageTensorInput
