# WindTunnel

A data collection app.

The design is closely coupled to the wind tunnel hardware - it measures angle
of attack, lift and drag on the airfoil platform, plus airspeed.

Airspeed and angle of attack inputs are via Phidget voltage sensors, while lift
and drag are measured with strain gauges connected to Phidget voltage ratio 
sensors.

The sensors are periodically polled, the values conditioned, and the results
are presented on the application GUI. The GUI also provides some controls for
calibratation, and the ultimate goal of the app - when the user selects "save", the 
currently presented data is written in csv format to the specified file.

The app is composed of the following classes -

TunnelMain: responsible for getting everything started, spinning off threads, and
providing communication between the data collection thread and the GUI.

Tunnel_Model: generated from Tunnel_Model.ui (created in Qt Designer), it implements the
GUI display and controls. It is instantiated in TunnelMain, and TunnelMain provides the
hooks for delivering data to be displayed and responding to control inputs.

DialogCalibrate: generated from DialogCalibrate.ui, it provides the controls that allow
for calibrating the changeable tunnel sensor references.

PhidgetBoardWait: generated from PhidgetBoardWait.ui, it is simply a dialog that pops up
if it's taking an inordinate amount of time to locate the phidget boards. Usually it 
appears just before the Phidget library times-out on the device open.

SensorReader: runs in its own thread and is responsible for periodically polling the
sensors, collecting sensor data into an instance of SensorSample, and putting the sample
into a queue. It creates an AnalogInput object for each phidget sensor to be read.

AnalogInput: is a wrapper class around a phidget VoltageInput class. AnalogInput is
designed to provide an interface that more resembles the 2.1 Phidget library - this has to
do with some historical Visual Basic algorithms that were used in a earlier version of 
wind tunnel data collection and subsequently morphed into python and reused herein.

ForceBalanceBridge: similar to AnalogInput, is a wrapper class around a phidget
VoltageRatioInput class. Again, it provides an interface to make it easier to reuse
some older code.

SensorSample: simply a class to contain all the sensor values collected during a 
particular polling cycle.

SampleCollector: this is the workhorse of the app. It runs in its own thread and waits on 
the queue written by SensorReader until a SensorSample appears. Each time a SensorSample
arrives, SampleCollector processes the elements of the sample, converting raw data into
values of known units. It also processes inputs delivered from Tunnel_Model via TunnelMain,
which consists of updating tare values as requested, and saving an instance of 
ProcessedSample to the specified file whenever the "Save" button is clicked.

ProcessedSample: one of these is created each time the GUI "Save" button is clicked. It
is the collection of processed sensor values, and writes them to the specified file in
"csv" format. This is the ultimate data collected by the app.

TunnelConfig: a wrapper around ConfigParser, allows reading various configuration values
written in the file "config.ini". Configurable items include the Phidget serial number 
and port specifying various sensor inputs, scaling and y-intercept values for converting
a raw sensor input to a known measurement, default output file location, and other things
deemed useful for changing without having to change the code. It is, however, rather 
closely coupled to the code, in that adding additional key/values will require code changes
to make use of those new config items.

TunnelPersist: similar to TunnelConfig, this is a wrapper around ConfigParser to allow
reading and writing items that need to be persistent across stops and restarts of the app.
These values are kept in the file "persist.ini". Besides the file used, the big difference
between TunnelConfig and TunnelPersist is that the latter can write to it's file, while
the former is read-only.

LiveGraph: an experimental window that displays a moving graph of sensor values. Not 
being used at this time.

SensorSimulator: if selected in the config.ini file, this class replaces SensorReader and
generates artificial data to test the GUI parts of the app.

TestBridge: provides a simple cli for unit-testing ForceBalanceBridge.

TestFilename: experimental code for testing slugify and the creation of safe filenames.

