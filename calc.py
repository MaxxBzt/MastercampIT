def carbon_saved(time_in_seconds):

    time_in_hours = time_in_seconds / 3600

    car_speed = 20
    metro_speed = 27

    car_distance = car_speed * time_in_hours
    metro_distance = metro_speed * time_in_hours

    car_co2_rate = 134
    metro_co2_rate = 3.8

    car_co2 = car_co2_rate * car_distance
    metro_co2 = metro_co2_rate * metro_distance

    co2_difference = abs(car_co2 - metro_co2)

    return co2_difference

if __name__ == '__main__':
    time_in_seconds = 3600 # 1 hour
    print(carbon_saved(time_in_seconds))