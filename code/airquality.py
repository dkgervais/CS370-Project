#imports for air quality code
import bme680
import time
from datetime import datetime

def get_air_quality():
    try:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    except (RuntimeError, IOError):
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

    # Default oversampling settings

    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

    # start_time and curr_time ensure that the
    # heat_up_time (in seconds) is kept track of.

    start_time = time.time()
    curr_time = time.time()
    heat_up_time = 1
    
    try:
        # Heating up the sensor
        while curr_time - start_time < heat_up_time:
            curr_time = time.time()
            if sensor.get_sensor_data():
                gas = sensor.data.gas_resistance
                temp = sensor.data.temperature
                time.sleep(1)

        # Set the gas baseline to an averaged, precomputed value
        gas_baseline = 10000.0

        # Set the humidity baseline to 40%, an optimal outdoor humidity.
        hum_baseline = 40.0

        # This sets the balance between humidity and gas reading in the
        # calculation of air_quality_score (25:75, humidity:gas)
        hum_weighting = 0.25

        if sensor.get_sensor_data():

            temp = sensor.data.temperature
            gas = sensor.data.gas_resistance
            gas_offset = gas_baseline - gas

            hum = sensor.data.humidity
            hum_offset = hum - hum_baseline

            # Calculate hum_score as the distance from the hum_baseline.
            if hum_offset > 0:
                hum_score = (100 - hum_baseline - hum_offset)
                hum_score /= (100 - hum_baseline)
                hum_score *= (hum_weighting * 100)

            else:
                hum_score = (hum_baseline + hum_offset)
                hum_score /= hum_baseline
                hum_score *= (hum_weighting * 100)

            # Calculate gas_score as the distance from the gas_baseline.
            if gas_offset > 0:
                gas_score = (gas / gas_baseline)
                gas_score *= (100 - (hum_weighting * 100))

            else:
                gas_score = 100 - (hum_weighting * 100)

            # Calculate air_quality_score.
            air_quality_score = hum_score + gas_score
            aqs_rounded = round(air_quality_score, 2)

            print('Gas: {0:.2f} Ohms\tTemperature: {1:.2f} \nHumidity: {2:.2f} %RH\tAir quality: {3:.2f}'.format(gas,temp,hum,air_quality_score)) 

            air_quality_text = str(aqs_rounded) + " percent, which is " + get_aq_text(air_quality_score)

            return air_quality_text

    except KeyboardInterrupt:
        pass
    
def get_aq_text(air_quality_score):
    # Calculate air quality score on a 0-5 scale
    score = (100 - air_quality_score) * .05
    
    if(score >= 3.01):
        return "Hazardous."
    if(score >= 2.01 and score <= 3.01):
        return "Very Unhealthy."
    if(score >= 1.76 and score <= 2):
        return "Unhealthy."
    if(score >= 1.51 and score <= 1.75):
        return "Unhealthy for Sensitive Groups"
    if(score >= .51 and score <= 1.50):
        return "Moderate"
    return "Good"

def main():
    get_air_quality()

if __name__ == "__main__":
    main()

