#!/usr/bin/env python3
"""
视频处理器的单元测试
"""
import os, sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from data_engine.processors.video.video_mapper_split_by_scene import videoSplitByScene
from data_engine.utils.transform import sort_and_compare
from data_engine.utils.test import test_case_list

root_dir = os.path.dirname(os.path.dirname(__file__))
case_list = [
    {
        "class": videoSplitByScene,
        "params": {},
        "input": [{"path": "data/video1.mp4"}],
        "output": [
            {
                "resolution": [360, 640, 3],
                "scene": 1,
                "start": "00:00:00.000",
                "start_frame": 0,
                "end": "00:00:06.000",
                "end_frame": 144,
                "path": "data/video1.mp4",
            },
            {
                "resolution": [360, 640, 3],
                "scene": 2,
                "start": "00:00:06.000",
                "start_frame": 144,
                "end": "00:00:09.875",
                "end_frame": 237,
                "path": "data/video1.mp4",
            },
            {
                "resolution": [360, 640, 3],
                "scene": 3,
                "start": "00:00:09.875",
                "start_frame": 237,
                "end": "00:00:11.750",
                "end_frame": 282,
                "path": "data/video1.mp4",
            },
        ],
        "compare": sort_and_compare,
    }
]


if __name__ == "__main__":
    test_case_list(case_list)
