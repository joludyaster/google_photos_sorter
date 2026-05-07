<div align="center" dir="auto">
<pre>
 ██████╗ ██████╗ ████████╗████████╗
██╔════╝ ██╔══██╗╚══██╔══╝╚══██╔══╝
██║  ███╗██████╔╝   ██║      ██║   
██║   ██║██╔═══╝    ██║      ██║   
╚██████╔╝██║        ██║      ██║   
 ╚═════╝ ╚═╝        ╚═╝      ╚═╝   
----------------------------
                  google photos takeout toolkit                  
</pre>
</div>

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/gphotos-takeout-toolkit?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/gphotos-takeout-toolkit)

## Table of Contents

- [Why did I create this?](#why-did-i-create-this)
- [What does gphotos_takeout_toolkit do?](#what-does-gphotos_takeout_toolkit-do)
- [How to run?](#how-to-run)
  - [Prerequisites](#prerequisites)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
    - [From PyPi](#from-pypi)
    - [From source](#from-source)
- [CLI](#cli)
  - [Main](#main)
  - [Organize](#organize)
- [Edge cases](#edge-cases)
- [Metrics](#metrics)
- [Roadmap](#roadmap)

## Why did I create this?

Well, my parents asked me to move all of their google photos to an external SSD drive. I saw how many photos they had and didn't want to do it manually so I decided to create a library that will do it for me.

## What does gphotos_takeout_toolkit do?

This library sorts photos from Google Takeout and merges their missing metadata. 
Metadata is exported along with the file and has almost the same name. 
Files are moved according to this convention: 

```
├── Your destination folder
    ├── videos
        ├── user (you could name it however you want, it sets to `user` folder by default)
            ├── photos_from_2024_11_05_by_user
                ├── photo.jpg
```

## How to run?

### Prerequisites

To be able to use this library, you need to have [ExifTool](https://exiftool.org/) installed on your machine as that is the required tool to restore metadata. Library checks whether you have it installed or not.

> Windows/Mac
```python
https://exiftool.org
```

> Ubuntu
```bash
sudo apt install libimage-exiftool-perl
```

> CentOS/RHEL
```bash
yum install perl-Image-ExifTool
```

> Arch
```bash
sudo pacman -S perl-image-exiftool
```

### Dependencies

- [PyExifTool](https://pypi.org/project/PyExifTool/)
- [Typer](https://pypi.org/project/typer-cli/)
- [Rich](https://rich.readthedocs.io/en/latest/introduction.html#installation)

### Installation

To use gphotos_takeout_toolkit, you will need python 3.11+ (earlier versions will not work due to the lack of support).

Create a virtual environment:
```commandline
python -m venv .venv
source ./.venv/bin/activate
```

#### From PyPi

> Pip installation:
```commandline
pip install gphotos_takeout_toolkit
```

> Uv installation:
```commandline
uv add gphotos_takeout_toolkit
```

#### From source
> Clone the project on your local machine:
```git
https://github.com/joludyaster/gphotos_takeout_toolkit.git
```

> Run:
```commandline
pip install .
```

And to make sure that everything is fine, run these commands to check
whether the library has all needed dependencies:

```commandline
gphotos_takeout_toolkit --help
python -m gphotos_takeout_toolkit
```

## CLI

### Main

```commandline
Usage: gphotos_takeout_toolkit [OPTIONS] COMMAND [ARGS]...

Options:
    --version, -V                   Show version and exit.                                                                                                                                                                       │                                                                                                      │
    --help                          Show this message and exit.   

Commands:
    organize                        Command to sort, organize and 
                                    merge metadata of the files.
                                    
Examples:
    gphotos_takeout_toolkit --version                        
    gphotos_takeout_toolkit --V
```

### Organize

```commandline
Usage: gphotos_takeout_toolkit organize [OPTIONS] INPUT_PATH DESTINATION_PATH

Options:
    --owner-name, -o                TEXT  Owner of the folders. [default: user]                                                                                                                                                  │
    --additional-file-move, -a      Additionally move all files into one folder.                                                                                                                                           │
    --enable-verbosity, -v          Enable verbosity to see all the logs in the console.                                                                                                                                   │
    --help                          Show this message and exit. 

Examples:
    gphotos_takeout_toolkit organize input_path destination_path -o jack -a -v
    gphotos_takeout_toolkit organize input_path destination_path --owner-name jack --additional-file-move --enable-verbosity
    gphotos_takeout_toolkit organize input_path destination_path -a -v
```

## Metrics
Here I've performed some of the tests to see how long it takes to
organize the files:

| Source | Size   | Number of files | Time   |
|--------|--------|-----------------|--------|
| folder | 26.9GB | 1501            | ~33m   |
    

## Edge cases
While the library handles majority of the tricky situations, there are
moments where it's simply impossible to move or get a metadata for the file.

Here are some of the reasons:

- Not a valid JPG (looks more like a RIFF) - means that an actual type of the file is not supported by ExifTool, usually it's Webp.
- When a file name looks like this `Screenshot_2023-10-16-21-47-42-334_com.zhiliaoa.jpg` or `B5RjaEjPAEjbhnWhlB9JEJoo9M7dvFU-EmZgZseQH1kHdcC.jpg`, google either strips the names or replaces some of the characters in the file name. Since this library iterates through JSON files first, it won't find a corresponding filename, therefore it won't be moved.

## Roadmap
* [x] Merge metadata and a file that's being moved.
* [ ] Allow users to modify how the folders are made and what structure to follow.

