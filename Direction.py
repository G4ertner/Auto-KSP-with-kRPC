# import krpc
import time
import math
# conn = krpc.connect()
# vessel = conn.space_center.active_vessel

pos = [
    [1, 2, 3],
    [4, 5, 6, 777],
    [7, 8, 9, 888, True],
]

def auto_pilot(pos):
#set up telemetry
    import krpc
    import time
    import math
    conn = krpc.connect(name='auto pilot')
    vessel = conn.space_center.active_vessel
    ap = vessel.auto_pilot
    obt_frame = vessel.orbit.body.non_rotating_reference_frame
    srf_frame = vessel.orbit.body.reference_frame
    srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
    long0 = conn.add_stream(getattr, vessel.flight(obt_frame), 'longitude')
    lat0 = conn.add_stream(getattr, vessel.flight(obt_frame), 'latitude')
    alt0 = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    list1 = [1, 1, 1, 1, 1, 1] #list for stabilizer
    counter1 = 0 #counting for acceleration timer
    print('auto pilot start')

#set up directional coordinates
    for i in range(len(pos)):
        lat1 = pos[i][0]
        long1 = pos[i][1]
        alt1 = pos[i][2]
        if len(pos[i]) == 4:
            speed = pos[i][3]
            dist = 500
            landing = False
        elif len(pos[i]) == 5:
            speed = pos[i][3]
            dist = pos[i][4]
            landing = False
        elif len(pos[i]) == 6:
            speed = pos[i][3]
            dist = pos[i][4]
            landing = pos[i][5]
        else:
            speed = 999
            dist = 500
            landing = False

        print('approaching position %.1f' % int(i+1))

        #ensuring that curve protocol only triggers once per coordinate
        curve = True

    #start the while loop based on distance to target
        while True:

    #do the calculation
        # calculating the altitude
            alt = alt0() - alt1
            if alt >= 0:
                r = 600000 + alt
            elif alt <= 0:
                r = 600000 + alt0()
        # calculating the latitude length
            lat = math.sqrt(2 * (r ** 2) - 2 * (r ** 2) * math.cos(abs(lat1 - lat0()) * math.pi / 180))
        # calculating the longitude at equator (long0) and longitude at respected latitude (long1)
            long_dis0 = math.sqrt(2 * (r ** 2) - 2 * (r ** 2) * math.cos(abs(long1 - long0()) * math.pi / 180))
            long_dis1 = ((100 - (abs(lat1) * 1.1111111111111111)) * 0.01) * long_dis0
        # calculating distance on the ground
            dis = math.sqrt(lat ** 2 + long_dis1 ** 2)
        # distance to the target through the air
            distance = math.sqrt(dis ** 2 + abs(alt) ** 2)
            print('distance: %.11f m' % distance)
            if distance < dist:
                print('point approached')
                break


    #result section for heading
        # dealing with lat = 0
            if (long1 - long0()) > 0 and lat == 0.000000000000000000:
                heading = 90
                print('east-lat 0; heading: %.11f' % heading)

        # if lat is on the left side
            elif (long1 - long0()) > 0.0000000 and (lat1 - lat0()) > 0:
                heading = (math.atan(long_dis1 / lat) * 180 / math.pi)
                print('east-left; heading: %.11f' % heading)

        # if lat is on the right side
            elif (long1 - long0()) > 0.0000000 and (lat1 - lat0()) < 0:
                heading = 90 - (math.atan(long_dis1 / lat) * 180 / math.pi) + 90
                print('east-right; heading: %.11f' % heading)

        # if long is negative; with lat = 0
            elif (long1 - long0()) < 0 and lat == 0.000000000000000000:
                heading = 270
                print('west-lat 0; heading: %.11f' % heading)

        # if long is negative; lat on the right, goes down
            elif (long1 - long0()) < 0.000000 and (lat1 - lat0()) > 0:
                heading = 360 - (math.atan(long_dis1 / lat) * 180 / math.pi)
                print('west-right; heading: %.11f' % heading)

        # if long is negative; lat on the left: goes up
            elif (long1 - long0()) < 0.000000 and (lat1 - lat0()) < 0:
                heading = (math.atan(long_dis1 / lat) * 180 / math.pi) + 180
                print('west-left; heading: %.11f' % heading)

    #result section for pitch
        # if  starting pos is higher than ending pos
            if alt < 0:
                pitch = 90 - math.atan(dis / abs(alt)) * 180 / math.pi
                print('altitude up: %.11f' % pitch)

            # if starting pos is lower than ending pos
            if alt > 0:
                pitch = 360 - (90 - math.atan(dis / abs(alt)) * 180 / math.pi)
                print('altitude down: %.11f' % pitch)

            # if starting pos is equal with ending pos
            if alt == 0.00:
                print('altitude hold')
                pitch = 0

    #enter values into the auto pilot
            current_heading = vessel.flight().heading
            current_pitch = vessel.flight().pitch
            ap.target_pitch = pitch

        # Stabilize plane if wobbling occurs
            list1.insert(0, (ap.error)-ap.attenuation_angle[1])
            list1.pop()
            list1_medium = (sum(list1) / len(list1)+1)
            if ap.attenuation_angle[1] > 1 and list1_medium <= 2:
                list = [ap.attenuation_angle[0] - 1, ap.attenuation_angle[1] - 1, ap.attenuation_angle[2] - 1]
                ap.attenuation_angle = (list[0], list[1], list[2])
                list1 = [1, 1, 1, 1, 1, 1]
            elif ap.error >= 5 and ap.attenuation_angle[1] <= 9:
                list = [ap.attenuation_angle[0] + 1, ap.attenuation_angle[1] + 1, ap.attenuation_angle[2] + 1]
                ap.attenuation_angle = (list[0], list[1], list[2])

    # ensure standart roll as 0
            if abs(vessel.flight().roll) > 10:
                ap.target_heading = heading
                time.sleep(2)
                ap.target_roll = 0
                print('adjusting roll: %.11f' % vessel.flight().roll)

        #roll in the right direction for target heading
            #when plane goes right (target heading bigger than current heading)
            if (heading > current_heading or ((360 - current_heading) + heading) < 180) and (heading - current_heading) >= 10 and curve:
                time.sleep(3)
                ap.target_roll = 50
                roll_error_right = 0
                while vessel.flight().roll <45:
                    print('roll error %.11f' % (50 - vessel.flight().roll))
                    time.sleep(1)
                    ap.target_roll = 50
                    roll_error_right += 1
                    if roll_error_right >= 10:
                        ap.disengage()
                        time.sleep(3)
                        ap.engage()
                        roll_error_right = 0
                curve = False
                while vessel.flight().heading > heading + 1 or vessel.flight().heading < heading - 1:
                    #ap.target_roll = 60
                    ap.target_heading = vessel.flight().heading +5
                    print('heading right: %.11f' % vessel.flight().heading)
                    if ap.target_heading == 360:
                        ap.target_heading = 0
                    time.sleep(0.1)

        # when plane goes left (target heading smaller than current heading)
            if (heading < current_heading or ((360 - current_heading) + heading) < 180) and (current_heading - heading) >= 10 and curve:
                time.sleep(3)
                ap.target_roll = -50
                roll_error_left = 0
                while vessel.flight().roll <-45:
                    #print('roll error %.11f' % (50 - vessel.flight().roll))
                    time.sleep(1)
                    ap.target_roll = -50
                    roll_error_left += 1

                    if roll_error_left >= 10:
                        ap.disengage()
                        time.sleep(3)
                        ap.engage()
                        roll_error_left = 0
                curve = False
                while vessel.flight().heading < heading - 2 or vessel.flight().heading > heading + 2:
                    #ap.target_roll = -60
                    ap.target_heading = vessel.flight().heading -5
                    print('heading left: %.11f' % ap.target_heading)
                    if vessel.flight().heading+5 == 0:
                        vessel.flight().heading = 360
                    time.sleep(0.1)

        #TODO Speedometer to control speed
            accel0 = srf_speed()
            time.sleep(0.25)
            accel1 = srf_speed()
            acceleration = (accel1 - accel0) * 4

        #counter to adjust acceleration only every third click
            counter1 += 1
            if counter1 == 4:
                counter1 = 0

            # calculate wanted acceleration
            if counter1 == 3 and srf_speed() - speed >= 0:
                wanted_acceleration = -(3 / 24) * (srf_speed() - speed) ** (11 / 12)
            elif counter1 == 3 and srf_speed() - speed < 0:
                wanted_acceleration = ((3 / 24) * abs(srf_speed() - speed) ** (11 / 12))

            # calculate wanted throttle

            #if ship needs to deccellerate
            if counter1 == 3 and acceleration - wanted_acceleration >= 0:
                print('deccellerate')
                wanted_throttle = -(2 / 3) * (acceleration - wanted_acceleration) ** (1 / 3)
                if vessel.control.throttle >=0.05:
                    vessel.control.throttle += wanted_throttle * 0.1
            #if ship needs to acellerate
            elif counter1 == 3 and acceleration - wanted_acceleration < 0:
                print('accellerate')
                wanted_throttle = ((2 / 3) * abs(acceleration - wanted_acceleration) ** (1 / 3))
                vessel.control.throttle += wanted_throttle * 0.1






        #Extending the wheels if approaching landing
            if landing:
                print('extending wheels')
                vessel.control.toggle_action_group(0)
                time.sleep(1)
                vessel.control.toggle_action_group(9)
                time.sleep(1)
                vessel.control.brakes = True
                landing = False
                
            if alt0() <= 73 :
                vessel.control.throttle =0
                if srf_speed() < 10:
                    break
            ap.target_pitch_and_heading(pitch, heading)

            time.sleep(0.2)






