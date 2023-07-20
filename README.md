# POPSICL
POPSICL - Proactive Optimization of Physics Space Integrated Climate Logging

## How to Make a POPSICL
Acquire the following items:  
Raspberry Pi Pico W  
DHT20 Temperature and Humidity Sensor  
Wires  
Popsicle  Sticks  
Solder  
Soldering Iron  

## Part 1: Programming the Raspberry Pi Pico
### Part 1.A: Setting Up the Pico

You’re going to want to have Thonny installed on your computer. It is like an IDE/Code Editor specifically for raspberry pi computers and microcontrollers.  Once you have that, take your Pico, push and hold the BOOTSEL button and plug your Pico into your computer. Release the BOOTSEL button after your Pico is connected. It will mount as a Mass Storage Device called RPI-RP2. Go to [this](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) website to download the UF2 file that will allow the Pico to read Micropython (make sure to install the latest version!), the language this project was done in. Drag and drop the MicroPython UF2 file onto the RPI-RP2 volume. Your Pico will reboot. You are now running MicroPython. 

### Part 1.B: Importing the code to the device:

Plug in the pico to your computer (without pressing any buttons). In a terminal, navigate to the `pico_files` folder of this repo. Then run:

```
rshell --buffer-size=30 -a -p /dev/tty.usbmodemXXXXX "cp *py /pyboard/"
```

where the `tty...` will be the address of the specific USB device on your system. This will vary with each pico and different operating systems. You should be able to install `rshell` with just a `pip install rshell`.

Then you can unplug/replug the device to reboot it and you're done!

If you want to monitor the serial output, you can use screen:

```
screen  /dev/tty.usbmodemXXXXX
```

and watch whatever print statements are in `main.py`

## Part 2: Register the device in POPSICL spreadsheet

Use the serial output to find the MAC address and password. Plug the device in and quickly run a screen command described above. Note these values in the central spreadsheet.

## Part 2: Register the device on the UT network

Goto netreg.utk.edu to register that mac address, giving the host the unique name of the device (e.g. `Popsicl-01`). This will allow the device to connect to the UT wifi.

## Part 3: Adding a device to the database

In the inFluxDB web interface, go to the InFluxDB Admin menu > Users. Add a user having the name of the MAC of the device, and put in the password. This will allow the device to write new data to the DB.


## Notes for how the database was set up and how to restart it if needed

Follow the instructions on [this website](https://hub.docker.com/r/philhawthorne/docker-influxdb-grafana) in order to set the docker image. This will run Chronograf, Influxdb and Grafana in a docker image on your machine. To stop the image, run
```bash
docker stop docker-influxdb-grafana
```
and to start it run
```
docker start docker-influxdb-grafana
```
To create a database in influxdb, you'll need to communicate through the port you chose for it to run on through the use of the curl command. Here's how to make a new database with the name 'mydb':
```
curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE mydb"
```
Now data from your popsicl can be posted to mydb through that port.

If you want to enable security, you'll need to create an admin user of the database. Then you'll need to ssh into the docker image using 
```
docker exec -it docker-influxdb-grafana bash
```
and follow the instructions [here](https://docs.influxdata.com/influxdb/v1.8/administration/authentication_and_authorization/) to enable authentication.
