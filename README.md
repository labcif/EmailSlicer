# Email Slicer

Autopsy module to split individual email messages from large files (e.g. PST files) within the scope of final project from the Computer Science 
Degree fromn ESTG "Escola Superior de Tecnologia e Gestão do Instituto Politécnico de Leiria", Portugal.

The focous of this program is create an alternative to the module Email Parser, used by Autopsy, in an attemp to provide functionalities that this one lacks, im particulary, extracting individual email messages.

Is also provided the alternative to use it as a report module or as a standalone application.


## Getting Started

### Prerequisites

* [Python](https://www.python.org/) (version 3 is recomended)
* [Autopsy](https://www.autopsy.com/) (if intended to be run inside the program) 

### Installing

There are two options providend when running this program:

* As an Autopsy module (Windows):
    1. Download [EmailSlicerReportModule.zip](https://github.com/labcif/EmailSlicer/releases/download/v0.1/EmailSlicerReportModuleWindows.zip) 
    2. Extract its content to Tools - Python Plugins 
    3. Install dependencies, by oppening the terminal inside de extrated folder and running the command: 
        * py -m pip install -r required_packages.txt --user
    
* As an Autopsy module (Linux):
    1. Download [EmailSlicerReportModule.zip](https://github.com/labcif/EmailSlicer/releases/download/v0.1/EmailSlicerReportModuleLinux.zip) 
    2. Extract its content to Tools - Python Plugins 
    3. Install dependencies, by oppening the terminal inside de extrated folder and running the command: 
        * python3 -m pip install -r required_packages.txt --user
        * sudo apt install pst-utils, graphviz
    
* As a standalone application:
    1. Download [EmailSlicerStandalone.zip](https://github.com/labcif/EmailSlicer/releases/download/v0.1/EmailSlicerStandalone.zip)
    2. Extract its content to desired location
    3. Install dependencies, by oppening the terminal inside de extrated folder and running the command: 
        * Windows:
            1. py -m pip install -r required_packages.txt --user
        * Linux: 
            1. python3 -m pip install -r required_packages.txt --user
            2. sudo apt install pst-utils, graphviz

### Run

* As an Autopsy module:
    1. Add the desired files to be analised to the opened case 
    2. Select "Generate Report"
    3. Select "Email Slicer report"
    5. Wait for the module to finish (the extracted content will be stored in the "TEMP" folder of the current case)
        
* As a standalone application:
    1. Open a temrinal window
    2. Navigate to the extrated location o the program
    3. Run the gram (run py EmailSlicer.py -h for options)
    4. Wait for the program to finish

## Authors

* **André Agostinho Nogueira (andre.nogueira@email.com)**
* Projet developed under the guidance and coordination of Professors Dr. **Miguel Monteiro de Sousa Frade** and **Patrício Rodrigues Domingue** 