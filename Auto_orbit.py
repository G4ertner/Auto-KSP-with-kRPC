import krpc
import math
import time
import Rendezvous


conn = krpc.connect(name='testing space plane')
vessel = conn.space_center.active_vessel

# frame of reference
srf_frame = vessel.orbit.body.reference_frame

# Streams for telemetry
srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
thrust = conn.add_stream(getattr, vessel, 'thrust')
ut = conn.add_stream(getattr, conn.space_center, 'ut')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
mu = conn.space_center.active_vessel.orbit.body.gravitational_parameter


# Functions
def steering_heading(current_heading, target_heading, roll=60):
    if target_heading <= 90 or target_heading >= 270:
        print('heading left')
        vessel.auto_pilot.target_roll = roll * (-1)
        time.sleep(1)
        while vessel.auto_pilot.target_heading > target_heading + 1 or vessel.auto_pilot.target_heading < target_heading - 1:
            vessel.auto_pilot.target_heading -= 0.5
            if vessel.auto_pilot.target_heading == 0:
                vessel.auto_pilot.target_heading = 360
            time.sleep(0.08333)
            print(vessel.auto_pilot.target_heading)
    elif target_heading >= 90 or target_heading < 270:
        print('heading right')
        vessel.auto_pilot.target_roll = roll
        time.sleep(1)
        while vessel.auto_pilot.target_heading > target_heading + 1 or vessel.auto_pilot.target_heading < target_heading - 1:
            vessel.auto_pilot.target_heading += 0.5
            if vessel.auto_pilot.target_heading == 360:
                vessel.auto_pilot.target_heading = 0
            time.sleep(0.08333)
    vessel.auto_pilot.target_heading = target_heading
    vessel.auto_pilot.target_roll = 0
    counter = 8
    while counter > 1:
        counter -= 1
        time.sleep(2)
        vessel.auto_pilot.attenuation_angle = (counter, counter, counter)
        print(vessel.auto_pilot.attenuation_angle)


def direction(angle_D, des_orbit=80000):
    # angle_A calculates the angle between delta_va (orbital velocity on ground + vis-visa) and delta_vr;
    angle_A = [90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65,
               64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39,
               38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13,
               12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
               19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
               45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
               71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96,
               97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
               118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138,
               139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
               160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180,
               179, 178, 177, 176, 175, 174, 173, 172, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160, 159,
               158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138,
               137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121, 120, 119, 118, 117,
               116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95,
               94, 93, 92, 91]
    # print(angle_A[angle_D])
    # vis_visa_1 is ground level, vis_visa_2 is desired orbit; des_orbit is the desired orbit put in by the user; orbital_vel_ground is the calculated orbital velosity on ground level
    vis_visa_1 = math.sqrt((3.5316000 * 10 ** 12) / 600000) * (
                math.sqrt((2 * (des_orbit + 600000)) / (600000 + des_orbit + 600000)) - 1)
    vis_visa_2 = math.sqrt((3.5316000 * 10 ** 12) / (600000 + des_orbit)) * (
                1 - math.sqrt((2 * (600000)) / (600000 + des_orbit + 600000)))
    orbital_vel_ground = 2426
    # adding v1 + v2 + orbital_vel_ground to length_c of the to calculate triangle
    length_c = vis_visa_1 + vis_visa_2 + orbital_vel_ground
    # length_b is the standard rotation of Kerbin in delta V
    length_b = 174.94
    # calculating length_a which is also the total delta V needed for getting into orbit if 1000 m/s drag is added
    # adding if sentence for angle_A is 90
    length_a = math.sqrt(
        length_c ** 2 + length_b ** 2 - (2 * length_c * length_b * math.cos(angle_A[angle_D] * (math.pi / 180))))
    delta_v = length_a + 1000
    print('calculated delta_v for ascent plan: %.1f' % delta_v)
    # calculating angle_B
    angle_B = math.asin(math.sin(angle_A[angle_D] * (math.pi / 180)) * (length_b / length_a))
    # return angle_B*(180/math.pi)
    # calculating aim_angle as the rotational corrected turn angle
    if (angle_D < 90 or angle_D > 270):
        aim_angle = angle_D - (angle_B * (180 / math.pi))
        if aim_angle >= 0:
            return aim_angle
        elif aim_angle < 0:
            return 360 + aim_angle
    elif angle_D > 90 or angle_D < 270:
        return angle_D + (angle_B * (180 / math.pi))
    elif (angle_D - (angle_B * (180 / math.pi))) < 0:
        return 360 - (angle_B * (180 / math.pi))


def auto_orbit(target_ap=90000, target_head=90, take_off_sp=100):
        # Input Variables
    take_off_speed = take_off_sp
    target_apoapsis = target_ap
    target_heading = target_head

    import krpc
    import math
    import time

    conn = krpc.connect(name='testing space plane')
    vessel = conn.space_center.active_vessel

    # frame of reference
    srf_frame = vessel.orbit.body.reference_frame

    # Streams for telemetry
    srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
    periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
    thrust = conn.add_stream(getattr, vessel, 'thrust')
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')


    # pre-launch setup
    vessel.control.brakes = True
    vessel.control.sas = True
    vessel.control.throttle = 1

    print('ready to start')
    time.sleep(2)

    # full throttle
    print('engage engines - full throttle')
    vessel.control.activate_next_stage()
    time.sleep(3)
    vessel.control.brakes = False

    # Rotate
    while srf_speed() < take_off_speed:
        time.sleep(1)

    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(10, 90)
    vessel.control.sas = False
    print('rotate')

    # retracting wheels
    while altitude() < 80:
       time.sleep(1)
    print('retracting wheels')
    vessel.control.toggle_action_group(0)
    time.sleep(1)
    vessel.control.toggle_action_group(0)


    # reaching 1000 m:
    while altitude() < 1000:
        time.sleep(1)

    # pitching to 3 degree
    checker1 = False
    if srf_speed() < 370:
        checker1 = True

    pitch = 10
    target_pitch = 3
    print('gaining speed to 450 m/s')
    while pitch > target_pitch and checker1:
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        pitch -= 0.25
        time.sleep(0.25)

    # heading in desired direction
    if target_heading != 90:
        print('heading for desired inclination')
        heading = 90
        heading_2 = direction(target_heading, target_apoapsis)
        steering_heading(heading, heading_2)
        print('heading for orbit complete')
    if target_heading == 90:
        heading_2 = target_heading

    # Raising altitude
    while srf_speed() < 450:
        time.sleep(1)

    # pitching to 10 degree
    pitch = 3
    target_pitch = 10
    print('rising to 10000 m')
    while pitch < target_pitch and checker1:
        vessel.auto_pilot.target_pitch_and_heading(pitch, heading_2)
        pitch += 0.25
        time.sleep(0.25)

    # gaining speed to 15000 m/s
    while altitude() < 10000:
        time.sleep(1)

    # pitching to 3 degree
    checker2 = False
    if srf_speed() < 1200:
        checker2 = True

    pitch = 10
    target_pitch = 4
    print('gaining speed to 15000 m/s')
    while pitch > target_pitch and checker2:
        vessel.auto_pilot.target_pitch_and_heading(pitch, heading_2)
        pitch -= 0.25
        time.sleep(0.25)

    while altitude() < 12000:
        time.sleep(1)

    # calculating acceleration: When acceleration falls under 0, engines will switch to closedcycle
    testnum = [1, 1]
    while True:
        for index in range(len(testnum)):
            testnum[1] = srf_speed()
            time.sleep(0.25)
            testnum[0] = srf_speed()
        acceleration = (testnum[0] - testnum[1]) * 4
        if acceleration < 0:
            break

    # switching to space mode
    print('switching to space mode')
    for engine in vessel.parts.engines:
        engine.toggle_mode()

    # pitching to 20 degree

    # while pitch < target_pitch:
    #     vessel.auto_pilot.target_pitch_and_heading(pitch, heading_2)
    #     pitch += 0.125
    #     time.sleep(0.25)


    acceleration = 20
    while apoapsis() <= target_apoapsis:
        if acceleration > 0:
            vessel.auto_pilot.target_pitch_and_heading(pitch, heading_2)
            pitch += 0.125
            time.sleep(0.25)
        vel1 = srf_speed()
        time.sleep(0.1)
        vel2 = srf_speed()
        acceleration = (vel2 - vel1)

    # shutting engines off at target apoapsis
    vessel.control.throttle = 0.0
    vessel.control.speed_mode = vessel.control.speed_mode.surface

    # turning sas prograde on
    vessel.auto_pilot.disengage()
    time.sleep(1)
    ap = vessel.auto_pilot
    ap.sas = True
    time.sleep(1)
    ap.sas_mode = ap.sas_mode.prograde

    print('target apoapsis reached')

    while altitude() < 65000:
        time.sleep(1)
    vessel.control.speed_mode = vessel.control.speed_mode.orbit

    # calculate burn time
    while altitude() < 70000:
        time.sleep(1)

    # Plan circularization burn (using vis-viva equation)
    print('Planning circularization burn')
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
    v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
    delta_v = v2 - v1
    node = vessel.control.add_node(
        ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

    # Calculate burn time (using rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = ((m0 - m1) / flow_rate)
    print(burn_time)

    # Wait until burn
    print('Waiting until circularization burn')
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time)
    lead_time = 12
    conn.space_center.warp_to(burn_ut - lead_time)

    # wait for burn time comming up
    while time_to_apoapsis() > burn_time:
        print('waiting')
        time.sleep(0.5)

    # The burn executer
    print('starting circularization burn')
    orbital_period = math.sqrt(mu/(apoapsis()+600000))
    throttle = 1
    checker3 = False
    while periapsis() < apoapsis() - 1 and time_to_apoapsis() < orbital_period * 0.25:
        if burn_time >= 5:
            testnum = time_to_apoapsis()
            time.sleep(0.25)
            burn_time = testnum
            print('check0')
            if (time_to_apoapsis() // burn_time) <= 0:
                vessel.control.throttle = throttle
                checker3 = True
                print('check1')
            elif (time_to_apoapsis() // burn_time) > 0 and checker3:
                throttle *= 0.9
                checker3 = False
                vessel.control.throttle = throttle * 0.2
                print('check2')

        else:
            if (time_to_apoapsis() // burn_time) <= 0:
                vessel.control.throttle = throttle
                checker3 = True
                print('check1')
            elif (time_to_apoapsis() // burn_time) > 0 and checker3:
                throttle *= 0.9
                checker3 = False
                vessel.control.throttle = throttle * 0.2
                print('check2')
    vessel.control.throttle = 0.00000000000000000

    node.remove()
    vessel.control.sas = False
    print('Orbit done!')
    vessel.auto_pilot.disengage()


