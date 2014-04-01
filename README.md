PiThermostat
============

Raspberry Pi using a HY28 LCD touchscreen (Texy or Adafruit PiTFT) and a TMP102 to make a thermostat display. Integrates with Google calendar or Django Schedule to find required temperature. Works with 433MHz sender board to make a complete boiler control. Currently works with British Gas and Drayton gas boilers.

More details about the 433 sender board used can be found https://github.com/tommybobbins/Raspi_433

The file structure of this project is as follows:
     
    This directory - Python scripts to move to /usr/local/bin
    utilities - useful associated scripts, but may not be required in all cases.
    init - init scripts to be moved to /etc/init.d/
    icons - graphics used by thermostat_gui.py. Can be moved, but icon_dir in thermostat_gui.py will need updating.
    utilities/433PlanB - to be used in the event of redis/thermostat_gui.py dying.

Requires the Adafruit libraries to read from the TMP102:

    git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
    cp -rp Adafruit-Raspberry-Pi-Python-Code /usr/local/lib/python2.7/site-packages/

Install the Python Google API:

     sudo pip install google-api-python-client pytz evdev httplib2 pygame redis smbus
     mkdir /etc/google_calendar/

Create a new Google calendar called thermostat. You need to allow access through to this calendar here: https://developers.google.com/google-apps/calendar/get_started . Download the client-secrets.json file and put it into /etc/google_calendar/

     cp client-secrets.json /etc/google_calendar

Run the list_calendar.py

     python list_calendars.py --no_auth_local_webserver

This should create a sample.dat in the local directory. We need to copy this to /etc/google_calendar for neatness.
     
     cp sample.dat /etc/google_calendar

The summary of all events in the calendar should be of the form 

     Temp=20.0

Uses pygame to build an SDL interface to the thermometer
Uses weather-util to retrieve weather info:

    sudo apt-get install weather-util

Edit retreive_weather.sh (it is currently set to Leeds/Bradford airport):

    sudo cp utilities/retrieve_weather.sh /usr/local/bin/
    sudo cp utilities/parse_weather.py /usr/local/bin/
    sudo chmod a+x /usr/local/bin/retrieve_weather.sh

    crontab -e
Add a line similar to the following to retrieve the weather for your location

    13 0,6,12,18 * * * /usr/local/bin/retrieve_weather.sh

Copy the init script to /etc/init.d/temp.sh

    sudo cp utilities/temp.sh /etc/init.d/
    sudo insserv temp.sh

/etc/modules should look something like:

    # /etc/modules: kernel modules to load at boot time.
    #
    # This file contains the names of kernel modules that should be loaded
    # at boot time, one per line. Lines beginning with "#" are ignored.
    # Parameters can be specified after the module name.

    snd-bcm2835
    fbtft dma
    fbtft_device name=hy28a rotate=0 speed=48000000 fps=50
    ads7846_device pressure_max=255 y_min=190 y_max=3850 gpio_pendown=17 x_max=3850 x_min=230 x_plate_ohms=100 swap_xy=0 verbose=3

/boot/cmdline.txt should look something like:

    dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait fbcon=map:10 fbcon=font:VGA8x8

433PlanB contains the scripts to run on a 433 board in the event of a thermostat board failing or redis not being available.

/etc/hosts should contain the name/location of the redis server:
    
    echo "192.168.1.223       433board" >>/etc/hosts


The scripts to copy to /usr/local/bin are as follows:

    call_433.py  # Makes redis calls to / from the redis server which maintains temperature states/ runs boiler
    gettemperatures.py # Makes call to the TMP102 to grab the temperatures and calls call_433 to grab redis data.
    google_calendar.py # Grabs current temperature required from Google Calendar.
    processcalendar.py # Deprecated. Was used with django-schedule and is left her for future reference.
    thermostat_gui.py  # Pygame binary to display data on screen and call all other libraries.

