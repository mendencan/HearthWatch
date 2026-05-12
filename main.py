# FILENAME: main.py
# This is the main code for the HearthWatch project, which is a safety monitoring system designed to detect potential stovetop fires by monitoring temperature changes and user presence. 
# The system uses a thermistor to measure the temperature of the stovetop, a DHT11 sensor to measure ambient temperature, and a PIR sensor to detect human presence. 
# If the system detects a significant temperature increase while the user is absent for a certain period, it will sound a buzzer to alert the user. 
# The code also includes error handling to ensure that any sensor failures will trigger an alert rather than leaving the system silent.
# Author: Menden Cannistra
# menden.cannistra@gmail.com

#These are the required imported libraries. 
import machine
import utime
import math
import dht

# This is the configuration section of the code, where we define all the constants and setup for our sensors and buzzer.
THERMISTOR_PIN = 26 
DHT_PIN = 14
PIR_PIN = 15 
BUZZER_PIN = 13      
# This is the value of the resistor used in the voltage divider with the thermistor. Adjust if you use a different value.
R_FIXED = 10000     
# The Beta parameter for the thermistor, which is a characteristic of the specific thermistor you are using. Adjust if you have a different thermistor. 
BETA = 3950   
# The reference temperature (in Kelvin) for the thermistor, typically 25°C. Adjust if your thermistor has a different reference temperature.       
T0 = 298.15          
# The offset to calibrate the thermistor readings. This value was determined experimentally to align the thermistor readings with the DHT11 temperature. Adjust if you find a different offset works better for your setup.
THERMISTOR_OFFSET = -8.87

# These are the thresholds for the safety logic. Adjust these values based on your specific requirements and testing.
HEAT_THRESHOLD = 4.0      # ΔT required to trigger a watch state
INACTIVITY_TIMEOUT = 30   # Seconds before warning (Set to 30 seconds by default)

# This links the physical pins to the variables in our code, allowing us to read from the sensors and control the buzzer.
thermistor = machine.ADC(THERMISTOR_PIN)
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))
pir_sensor = machine.Pin(PIR_PIN, machine.Pin.IN)
buzzer = machine.Pin(BUZZER_PIN, machine.Pin.OUT)

# This global variable tracks the last moment the system detected human activity via the PIR sensor. It is initialized to the current time when the program starts.
last_activity_time = utime.time()

# This function handles the physica calculation required to convert an electrical reading (ADC) into a precise temperature in Celcius. It uses Steinhart-Hart principles. 
def get_thermistor_temp():
    # This is the raw ADC reading from the thermistor. We need to convert this to a resistance value, and then to a temperature using the Steinhart-Hart equation.
    raw = thermistor.read_u16()
    # This is an error check. Since the system uses a 16-bit integer, raw should be between 0 and 65535.
    if raw == 0 or raw >= 65535: return None # This sends a placeholder value for failure. 
    # This is the calculation to determine the current resistance of the thermistor. It takes the ADC count and translates it back to Ohms. 
    resistance = R_FIXED * (65535 / raw - 1)
    # This is a simplified version of the steinhart-hart equation, which calculates the temperature based on the resistance. It first calculates the natural logarithm of the resistance ratio, then applies the Beta parameter and reference temperature to find the actual temperature in Celsius. 
    steinhart = math.log(resistance / 10000) / BETA
    # This adds the next term required by the Steinhart equation, incorporating the reference temp T0. 
    steinhart += 1.0 / T0
    # This calculates the recprocal of the prev result and converts it to Kelvin. 
    temp_c = (1.0 / steinhart) - 273.15
    # This returns the temperature plus my offset that I determined experimentally. This is because the sensor setup is not perfect and must be accounted for. 
    return temp_c + THERMISTOR_OFFSET

# This is the main loop of the program. 
def main():
    # This tells the program that we will be modifying the global variable when we modify last activity time from the PIR sensor. 
    global last_activity_time
    # This prints the format of the status of the system for debugging purposes to the terminal. 
    print("HearthWatch Terminal Output for Monitoring Purposes:")
    print(f"Buzzer: ACTIVE if ΔT > {HEAT_THRESHOLD}C AND Absent > {INACTIVITY_TIMEOUT}s")
    
    # Initial silence for buzzer. 
    buzzer.value(0)

    # This is the main loop. It is an infinite loop that runs until shutdown. 
    while True:
        try:
            # This updates the occupancy status if the PIR sensor detects motion. 
            if pir_sensor.value() == 1:
                last_activity_time = utime.time()
                is_occupied = True
                occ_label = "PRESENT"
            # If motion is not detected, we calculate how long it has been since the last activity and update the label accordingly. 
            else:
                is_occupied = False
                seconds_unattended = utime.time() - last_activity_time
                occ_label = f"ABSENT ({seconds_unattended}s)"
            
            # This reads the temperature data from the DHT11 sensor and the thermistor. The DHT11 provides the ambient temperature, while the thermistor is used to detect the hotspot temperature.
            dht_sensor.measure()
            ambient_t = dht_sensor.temperature()
            hotspot_t = get_thermistor_temp()
            
            # This checks if both the thermistor reading and the DHT11 temperature reading are valid numbers before proceeding. 
            if hotspot_t is not None and ambient_t > 0:
                delta_t = hotspot_t - ambient_t
                current_unattended = utime.time() - last_activity_time
                
                # Only alarm if heat is high AND user has been gone too long. 
                if delta_t >= HEAT_THRESHOLD and not is_occupied and current_unattended >= INACTIVITY_TIMEOUT:
                    # Sounds buzzer
                    buzzer.value(1)
                    # Sets value of safety tag for print statements. 
                    safety_tag = "[WARNING: UNATTENDED]"
                else:
                    # Doesn't sound buzzer if alright and updates safety tag accordingly. 
                    buzzer.value(0)
                    safety_tag = "[OK]"

                # This is the final output to the terminal for monitoring purposes. 
                print(f"User: {occ_label:15} | ΔT: {delta_t:5.2f}°C | Status: {safety_tag}")
        # This runs if any part of the try block fails. This could be a sensor read failure. 
        except Exception as e:
            # This prints that there is an error with the system. 
            print(f"System Error (Possible sensor fault): {e}")
            # Contiunously sounds buzzer until user unplugs device. This is for safety purposes. User will likely first be summoned to inspect stovetop or other surface. A false alarm is better than no alarm. 
            buzzer.value(1)  # Alert on error
        # This pauses the entire program execution for one second before starting the loop over again. This gives the hardware time to process and prevents flooding of the terminal. 
        utime.sleep(1)
# This means the script is run if it is run directly by the user. Save the file as main.py on the pico and it will run automatically on startup. 
if __name__ == "__main__":
    main()
