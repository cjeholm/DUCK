# DUCK
Aircraft proximity alerts for DUMP1090

This alert script reads the JSON data created by DUMP1090 and alerts the user for low altitude aircraft in the area. Some aircraft do not transmit location in their ADS-B data and sometimes this data is missing due to poor signal quality. When the alert script detects an aircraft with a low altitude and its location is unknown, the warning will be triggered as a safety precaution. DUCK and DUMP1090 can run on different computers but is intended to function without any network or internet connection. All you need is the software, a RTL-SDR and a vertically polarized antenna tuned to 1090 MHz.

The purpose of DUCK is to be an early warning system for drone pilots. Where I live, close to the coast in the middle of Sweden, low flying helicopters can pop up out of nowhere. Ambulance-, Coast Guard and Sea Rescue choppers are quite busy some days and they can come in very low. Of course you should keep your drone way away from their airspace but a warning tool for incoming aircraft can still be good practice.

Be advised that not all aircraft carries an ADS-B transmitter and will therefore not be detected. Do not blindly trust this script, it's just one tool in the toolbox.


KNOWN LIMITATIONS

Reported altitude from the aircraft is uncorrected for local changes in pressure and temperature. This may cause an incorrect or even negative altitude being reported, a limitation of the ADS-B system itself. Negative altitudes will trigger the warning.

Airport ground vehicles transmitting ADS-B data may trigger the altitude warning, this is not yet tested. Add them to ignored_aircraft to suspend warning.

Aircraft reporting a non-numerical altitude may cause the script to crash. Not yet tested.

Warning sounds play well on Windows but is not yet fully implemented on OSX and Linux.
