# Datagenerator Creating Random Travel Requests

The datagenerator/emitter of group 9 is a tool to create public transport requests in the greater Gothenburg area.  
By running the main script these requests are continuously published to a MQTT broker at a customizable rate.

This module has been developed using Python 3.  

The following sections will go deeper into the process for installation and usage.

## Installation

### Python 3.6+
First of all you need to make sure to Python 3 is installed on your system.   

**Check your Python Version:**

In order to check whether Python 3 is installed already, go to your command line and run the following command:
```bash
python --version
```

If the result is Python 2.x.x, Python 2 is your system standard. In this case you should check whether Python 3 is installed additionally:
```bash
python3 --version
```
If the result is Python 3.x.x you can either always use the command `python3` to replace the simple `python`. Alternatively you could switch Python 3 to be your system default.  


If neither of these two commands returns Python 3.x.x, you probably need to install Python 3 before continuing with the next steps of the installation. If the release number is lower than 3.7, you should also consider updating your Python to a newer version.  

**Install Python:**  
* To install Python please download a recent version from the  
[Official Python Download Page](https://www.python.org/downloads/)
* Or consult these [Python Installation Instructions](https://realpython.com/installing-python/)  

**Install Python Dependencies:**  

All non-standard Python dependencies for this project are listed in the file [requirements.txt](requirements.txt).
The easiest way to install these dependencies is using pip or pip3 (depending on your systems default Python).
Simply run the corresponding command from your commandline:
```bash
pip install -r requirements.txt
pip3 install -r requirements.txt
```
If this command completes successfully, the correct versions of all necessary dependencies should be installed on your system.  

Otherwise you can check [the requirements](requirements.txt) and try to manually install any missing dependencies.

**Install Tkinter:**  

Tkinter is a Python framework for user interfaces. 
If it is not installed with your standard python distribution, you might need to take some additional steps to install it.
You can find install instructions for your OS in the [tkdocs](https://tkdocs.com/tutorial/install.html).  
 
For instance it can be installed on Linux using your distribution's package manager:  

```bash
sudo apt-get install python3-tk
```

Now you should be able to execute the datagenerator without any problems.

## Usage

There are a few things you can do with the datagenerator. 
To run the script you ideally open a commandline in the top-level directory of this project. 
From there you can simply run the project and pass parameters in the commands.  

To get an idea of the available parameters, ask for help using the flag -h or --help:
```bash
python3 -m datagenerator --help
```
The result should look like this:  

![command line help](readme/datagenerator_help.png)  

Now the parameters listed in this list might seem a bit cryptic if you are not familiar of 
how it creates and emits travel requests. 

So let's quickly explain all these options and shed some light on what they do:
* The first optional argument just prints the help statement you see in the screenshot
* The next parameter is used to select a file with coordinates. This is option can be used 
to seed the coordinate generator used for the requests. It randomly picks from the provided locations.
* BROKER specifies the address of the broker
* TOPIC sets the topic the emitter will publish to
* CLIENT sets the MQTT client's name
* The print option can be used to print the emitted messages in the commandline
* SLEEP sets how long the emitter will wait between emitting two requests. 
This can be used to set the load on the system.
* OFFSET is used to adjust another dimension of randomness in the generated coordinates.
Each coordinate is created at a random location in a circle with radius OFFSET 
around the currently selected seed. 
* LIMIT defines how many coordinates from the list of seed coordinates are used. 
This can be used to create random clusters by setting a low value.
* FILENAME is the output file for logs produced while running the generator
* DAYS_OFFSET sets the number of days the randomly produced timestamp can be 
before or after the current daytime.
* The **resend** option can be used to replay messages from a logfile instead of creating new ones.
* The final option can be used to create requests at any arbitrary point in time by shifting
all request DAYS into the past (give negative days for the future) 

### Example

You could for example run the emitter with the following command:
```bash
python3 -m datagenerator -p -t example -s 1 -D 50
```
This will run an emitter using mostly the default values. 
It will print the emitted messages to the command line, 
publish on the topic "example", wait 1 second between messages, 
and date back the requests by 50 days.  

The output of this command should look something like this:  

![emitter example](readme/datagenerator_example.png)

## Support

If you have any questions regarding this specific module,
please contact the lead developer of this module, [Konrad Otto](mailto:gusottko@student.gu.se), 
or the co-developer and maintainer, [Armin Ghoroghi](arre2118@gmail.com).

## Authors and Acknowledgment

This module is part of the distributed system for Visual Transportation Support 
developed by Clusterrot (Group 9) during the course 
DIT355 Miniproject: Distributed Systems at the University of Gothenburg.  
The system was implemented from November 2019 through January 2020.  

Clusterrot consists of the following members:
- Tobias Bank
- Armin Ghoroghi
- Simon Johansson
- Kardo Marof
- Jean Paul Massoud
- Konrad Otto

### Documentation

* To access Diagrams and Documentaion please visit [Documentaion](https://git.chalmers.se/courses/dit355/2019/group-9/dit355-project-documentation)
 

[//]: # (The structure of this file has been inspired by the suggestions on https://www.makeareadme.com/) 
