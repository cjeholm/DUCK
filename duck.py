# DUCK
# Aircraft proximity alerts for DUMP1090
# https://github.com/cjeholm/DUCK


import json
import time
import os
import urllib.request
import math
if os.name == 'nt':
    import winsound


# User settings
alert_alt = 6000
play_sound = False
metric = True
refresh_timer = 2
timeout = 10
# json_source = "http://localhost:8080/data.json"
json_source = "http://localhost/sdrjson/data.json"
my_lat = 59.758202
my_long = 18.700124
alert_distance = 200
log = True


known_aircraft = {
    '4aaa72': 'heli ambul',
    '4aaa4e': 'heli sjörä',
    '86831e': 'test JAL45'
}

ignored_aircraft = {
    'aaaaaa': 'ignored',
    'bbbbbb': 'ground',
    'cccccc': 'drone'
}


# User settings ends

# Set units
if metric:
    altitude_unit = "m"
    distance_unit = "km"
else:
    altitude_unit = "ft"
    distance_unit = "miles"


# Logging
def write_log(log_file_name, log_entry):
    with open(log_file_name, "r") as log_file:
        log_data = log_file.read()
    if log_entry not in log_data:
        with open(log_file_name, "a+") as log_file:
            log_file.write(log_entry + "\n")


# Start a log
log_file_name = "alert_" + str(int(time.time())) + ".txt"
if log:
    with open(log_file_name, "a+") as log_file:
        log_file.write("Session started: " + str(time.ctime()) + "\n")


# Clearing the screen
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def warning_counters(active, recent, ignored):
    print("\nActive: \t" + str(active))
    print("Recent: \t" + str(recent))
    print("Ignored: \t" + str(ignored))


def warning_message():
    print(("\n"))
    print("* " * 20)
    print("*" + " " * 37 + "*")
    print("*       !!! PROXIMITY ALERT !!!       *")
    print("*" + " " * 37 + "*")
    print("* " * 20)


def warning_sound():
    if os.name == 'nt':
        winsound.Beep(1000, 500)
        winsound.Beep(2000, 500)
    else:
        print("\a")


# Function for estimating distance between coords.
def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) =
    # sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
    math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.

    if metric:
        distance = arc * 6373
    else:
        distance = arc * 3960
    return distance


# MAIN LOOP
def main_loop():

    # Read JSON and do some error handling
    # DUMP1090 JSON file keeps data for 300 seconds
    try:
        with urllib.request.urlopen(json_source) as f:
            data = json.load(f)
    except urllib.error.URLError:
        print("\nError: JSON data could not be fetched. Check source and parameters.")
        print("Retrying in 5 seconds.")
        # data = {'hex': 'error'}
        data = ""
        time.sleep(5)

    # Clear screen
    cls()

    # Reset warning counters
    active_warnings = 0
    recent_warnings = 0
    ignored_count = 0

    # Print the header
    print ("Hex\tFlight\t\tSeen\tAlt\tDist\tNotes")
    print ("-" * 60)

    # List parsing loop
    for line in data:

        # Clear print buffer
        print_buffer = ""

        # Clear recent warning
        new_warning = False

        # Fill null data
        if line["flight"] == "":
            line["flight"] = "\t"

        # Unit conversion
        if metric:
            line["altitude"] = int(line["altitude"] * 0.3048)

        # Calculate distance
        if line['lat'] == 0:
            line['lat'] = my_lat
        if line['lon'] == 0:
            line['lon'] = my_long
        distance = distance_on_unit_sphere(my_lat, my_long, line['lat'], line['lon'])

        # Construct string for output
        print_buffer += str(line['hex'])
        print_buffer += "\t"
        print_buffer += str(line['flight'])
        print_buffer += "\t"
        print_buffer += str(line['seen'])
        print_buffer += "\t"
        print_buffer += str(line['altitude'])
        print_buffer += "\t"
        print_buffer += str(round(distance,1))
        print_buffer += "\t"
        if known_aircraft.get(line['hex']) is not None:
            print_buffer += str(known_aircraft.get(line['hex']))
            print_buffer += "\t"
        else:
            print_buffer += "\t\t"


        #print(ignored_count.get(line['hex']))
        #print(str(line['hex']))

        # Check for ignored aircraft
        if ignored_aircraft.get(line['hex']) is not None:
            ignored = True
        else:
            ignored = False

        # Check altitude trigger
        if line["altitude"] <= alert_alt and line["altitude"] != 0 and line["seen"] <= timeout and distance <= alert_distance and not ignored:
            print_buffer += "<<<  WARNING"
            new_warning = True
            active_warnings += 1
            if log:
                write_log(log_file_name, str(line['hex']) + "\t" + str(known_aircraft.get(line['hex'])) + "\n")
        elif line["altitude"] <= alert_alt and line["altitude"] != 0 and line["seen"] > timeout and distance <= alert_distance and not ignored:
            new_warning = True
            recent_warnings += 1
        else:
            new_warning = False
            ignored_count += 1

        # Print the line, ignore non-warning aircraft
        if new_warning:
            print(print_buffer)

    # Placeholder when no warnings
    if active_warnings == 0 and recent_warnings == 0:
        print("No warnings")

    # Check for active warnings
    if active_warnings > 0:
        warning_message()
    else:
        print("\n\n\n\n\n")

    # Show alert altitude, distance and units
    print("\nAltitude warning at " + str(alert_alt) + " " + altitude_unit)
    print("Distance warning at " + str(alert_distance) + " " + distance_unit)
    print("Position set to " + str(my_lat) + " " + str(my_long))

    # Show the counters
    warning_counters(active_warnings, recent_warnings, ignored_count)

    # Play warning sound
    if active_warnings > 0 and play_sound:
        warning_sound()

    # Timer, wait for refresh
    time.sleep(refresh_timer)

# Loop da loop, forever and ever
while True:
    main_loop()