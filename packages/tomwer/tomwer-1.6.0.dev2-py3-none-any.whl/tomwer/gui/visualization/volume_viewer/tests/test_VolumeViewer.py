from __future__ import annotations


import numpy

from tomoscan.volumebase import SliceTuple

from tomwer.tests.conftest import qtapp  # noqa F401
from tomwer.gui.visualization.volume_viewer.VolumeViewerWidget import (
    VolumeViewerWidget,
)


def test_volumeReconstructionSummary(qtapp):  # noqa F811

    widget = VolumeViewerWidget()
    widget.setSlices(
        {
            SliceTuple(axis=0, index=1): numpy.ones((10, 20)),
            SliceTuple(axis=0, index=12): numpy.ones((10, 20)),
            SliceTuple(axis=0, index=25): numpy.ones((10, 20)),
            SliceTuple(axis=1, index=0): numpy.arange(0, 100).reshape(10, 10),
            SliceTuple(axis=1, index=10): numpy.arange(1000, 1100).reshape(10, 10),
            SliceTuple(axis=1, index=20): numpy.arange(1000, 1100).reshape(10, 10),
            SliceTuple(axis=2, index=100): numpy.random.random(100).reshape(10, 10),
            SliceTuple(axis=2, index=101): numpy.random.random(100).reshape(10, 10),
            SliceTuple(axis=2, index=103): numpy.random.random(100).reshape(10, 10),
        }
    )
    widget.setVolumeMetadata(
        {
            "nabu_config": {
                "reconstruction": {
                    "method": "FBP",
                },
                "phase": {
                    "method": "paganin",
                    "delta_beta": 110.0,
                },
            },
            "processing_options": {
                "reconstruction": {
                    "voxel_size_cm": (0.2, 0.2, 0.2),
                    "rotation_axis_position": 104,
                    "enable_halftomo": True,
                    "fbp_filter_type": "Hilbert",
                    "sample_detector_dist": 0.4,
                },
                "take_log": {
                    "log_min_clip": 1.0,
                    "log_max_clip": 10.0,
                },
            },
        },
        volume_shape=(10, 10, 10),
    )
