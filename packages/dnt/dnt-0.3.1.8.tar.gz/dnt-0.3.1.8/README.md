# Project Title

A Python package for video-based traffic analysis.

## Description

This tool can generate vehicel trajectories using real-time object detection and multiple object tracking technologies. Based on the trajectory data, the tool can prodcue various safety and operational analytics.

## Getting Started

### Dependencies

* OS: Ubuntu 20.04 or higher
* Python: 3.7 or higher
* Libarary: pytorch (>=1.12 with cuda), pandas, tqdm, numpy, scipy, matplotlib, ultralytics

### Installing
```
Setup enviroment:

    python3.x -m venv dnt (you may replace dnt with you specified name; python version >3.9)
    sudo apt-get install python3.x-dev  
    pip install python-dev-tools

pip install torch==1.12.0+cu116 torchvision==0.13.0+cu116 torchaudio==0.12.0 --extra-index-url https://download.pytorch.org/whl/cu116
pip install dnt
```

### Executing program

Call APIs from Python codes


## Authors

Zhenyu Wang [@wonstran@hotmail.com](mailto:wonstran@hotmail.com)

## Version History

* 0.2
    * Replace darknet with pytorch
    * Adopt YOLO v8 as backend for object detection
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE file for details