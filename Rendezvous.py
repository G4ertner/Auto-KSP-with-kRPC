######################################################################
### Automated Rendez-Vous for Space Planes
######################################################################
###
###  This script will take your space plane from the start of the
###  runway all the way up to the set target on orbit and dock
###  with the set docking port.
###
###  Steps to follow:
###  1. Launch space plane on the runway.
###  2. Activate brakes to prevent it from rolling.
###  3. Set the the vessel to rendez-vous with as target.
###  4. Start the kRPC server.
###  5. Start the script.
###
###  Notes:
###  Please don't forget to have fun.
###
###  Author: Nikolas Guttler				December, 2020
###  Template: artwhaley
######################################################################

def rendez_vous():
    import krpc
    import math
    import time
    import win32com.client as comclt

###############################################################################
## 			Setting up Telemetry
##  In here are all neccessary telemetry connections needed to be pulled
##  directly from the game.
##
##############################################################################

    global math, wsh, time, sc, vessel, target, obt_frame, ap, orb_speed, ut, mu, altitude, time_to_apoapsis, vessel_velocity, target_velocity

    wsh = comclt.Dispatch("WScript.Shell")
    conn = krpc.connect(name='Rendez-vous')
    sc = conn.space_center
    vessel = sc.active_vessel
    target = sc.target_vessel
    obt_frame = vessel.orbit.body.non_rotating_reference_frame
    vessel_velocity = conn.add_stream(getattr, vessel.flight(obt_frame), 'velocity')
    target_velocity = conn.add_stream(getattr, target.flight(obt_frame), 'velocity')
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    orb_speed = conn.add_stream(getattr, vessel.flight(obt_frame), 'speed')
    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
    mu = vessel.orbit.body.gravitational_parameter
    ap = vessel.auto_pilot

###############################################################################
##                      Rendezvous Function
##
##  This is the rendezvous function that describes the different steps in the
##  procedure to execute the rendezvous from start to docking.
##
##  please call the rendez_vous function to start the script.
##
##
###############################################################################

    #Check if ship is already in orbit
    if altitude() > 70000:
        in_orbit = True
        print('Ship is already in orbit, continuing with step 3.')


    if not in_orbit:
        print('Step 1:\nWait for the target to cross the vessel on ground overhead.')
        wait_for_target_is_overhead()


    if not in_orbit:
        print('Step 2:\nFly to transfer orbit using Auto_orbit script.')
        import Auto_orbit
        Auto_orbit.auto_orbit(90000, 90, 60)

    print('Step 3:\nWaiting for right angle to execute burn 1 of Hohman transfer.')
    Wait_for_hohman1()

    print('Step 4:\nExecute burn 1 of Hohman transfer.')
    hohman_transfer_1()

    print('Step 5:\nWait for burn 2 of Hohman transfer.')
    wait_for_hohman2()

    print('Step 5:\nExecute burn 2 of Hohman transfer.')
    hohman_transfer_2()

    print('Step 6:\nMatch speed with target vessel.')
    match_speed()

    print('Step 7:\nApproach target vessel to save distance of 1000 meters.')
    approach_target()

    print('Step 8:\nSeparate payload from space plane.')
    Payload_separation()


    print('Step 9:\nFind and align docking ports.')
    docking_alignment(conn, vessel, target)

    print('Step 11:\nExecute docking.')
    docking_maneuver(conn, vessel, target)

    print('Rendezvous Complete.')

###############################################################################
##                      Automated Functions
##    High Level Functions that perform each phase of the maneuver
###############################################################################

def wait_for_target_is_overhead():
    vessel.control.brakes = True
    phase_angle = 3
    time_warp = False
    while abs(phase_angle) >= 0.01:
        phase_angle = angle_between_two_vectors(vessel.position(obt_frame), target.position(obt_frame))
        print('Angle between Vessel and Target:', phase_angle)
        if phase_angle >= 1.0 or phase_angle < 0.0:
            if sc.warp_factor != 4:
                time_warp_up(4)
        elif phase_angle > 0.1 and phase_angle > 0.1:
            if sc.warp_factor != 2:
                time_warp_up(2)
        elif phase_angle < 0.1:
            if sc.warp_factor != 0:
                time_warp_stop()
        time.sleep(1)


def Wait_for_hohman1():

    #calculate the estimated time to burn
    time_to_burn = time_to_coincidence((vector_length(target.position(obt_frame)) - 600000), altitude())
    print('time to burn:', time_to_burn)

    #set up burn node
    global node
    node = vessel.control.add_node(ut() + time_to_burn, prograde=delta_v1())

    sc.warp_to(ut()+time_to_burn-10)

    ap.sas = True
    vessel.control.speed_mode = vessel.control.speed_mode.orbit
    time.sleep(1)
    ap.sas_mode = ap.sas_mode.prograde
    print("Angle Difference:", math.degrees(towards_angle()))
    while towards_angle() < 0:
        print("Angle Difference:", math.degrees(towards_angle()))
        time.sleep(0.5)


def hohman_transfer_1():
    while ap.error >= 2:
        time.sleep(1)

    start_speed = orb_speed()
    speed_wanted = orb_speed() + delta_v1()
    while speed_wanted >= orb_speed():
        frac = int(((start_speed - orb_speed()) / (start_speed - speed_wanted))*100)
        print('burn done:', frac)
        vessel.control.throttle = 1 - (frac*0.01)
        pass
    vessel.control.throttle = 0.0
    node.remove()


def wait_for_hohman2():
    burn_t = burn_time(delta_v2())
    global node
    node = vessel.control.add_node(ut() + time_to_apoapsis() - burn_t, prograde=delta_v2())
    sc.warp_to(ut() + time_to_apoapsis() - burn_t - 10)


def hohman_transfer_2():
    burn_t = burn_time(delta_v2())
    while time_to_apoapsis() >= (burn_t * 0.5):
        time.sleep(0.1)

    while ap.error >= 2:
        time.sleep(1)

    start_speed = orb_speed()
    speed_wanted = orbital_velocity(altitude())
    print('accelerating to speed: ', speed_wanted)
    while speed_wanted >= orb_speed():
        frac = int(((start_speed - orb_speed()) / (start_speed - speed_wanted)) * 100)
        vessel.control.throttle = 1 - (frac * 0.01)
        pass
    vessel.control.throttle = 0.0
    node.remove()


def match_speed():
    vessel.control.speed_mode = vessel.control.speed_mode.target
    ap.sas = True
    time.sleep(1)
    ap.sas_mode = ap.sas_mode.retrograde
    while ap.error >= 2:
        time.sleep(1)

    speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
    start_speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
    speed_wanted = 0.1
    frac1 = 2
    while speed_wanted <= speed:
        speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
        print('Speed between Vessel and Target:', speed)
        frac = speed / start_speed
        vessel.control.throttle = 1 * frac
        # if (frac1 - frac) < 0:
        #     break
        # time.sleep(0.05)
        # frac1 = frac

        pass
    vessel.control.throttle = 0.0

def approach_target():
    # this function approaches the target to 1000 meters

    # turning the SAS on and aiming at the target
    ap.sas = True
    time.sleep(1)
    ap.sas_mode = ap.sas_mode.target

    #  Depending on the distance to target a different speed for the approach is used
    target_distance = vector_length(vector_between_vectors(vessel.position(obt_frame), target.position(obt_frame)))
    if target_distance > 5000:
        #accelerate speed towards target to 50 m/s
        speed_wanted = 50
    elif target_distance <= 3000:
        #accelerate speed towards target to 20 m/s
        speed_wanted = 20
    elif target_distance <= 2000:
        speed_wanted = 10
    else:
        return

    while ap.error >= 2:
        time.sleep(1)

    speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
    start_speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
    print('accelerating to speed: ', speed_wanted)
    while speed_wanted >= speed:
        speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
        frac = int(((start_speed - speed) / (start_speed - speed_wanted)) * 100)
        vessel.control.throttle = 1 - (frac * 0.01)
        pass
    vessel.control.throttle = 0.0

    # aiming towards retrograde in preparation of deceleration maneuver
    ap.sas_mode = ap.sas_mode.retrograde

    while ap.error >= 2:
        time.sleep(1)

    #waiting until the distance to the target is 1000 m:
    while target_distance >= 1000:
        target_distance = vector_length(vector_between_vectors(vessel.position(obt_frame), target.position(obt_frame)))
        print('distance to target: ', target_distance, ' m')
        time.sleep(0.5)

    #decelerating the ship down to match the target's speed
    speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
    start_speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
    speed_wanted = 0.5
    print('decelerating to speed: ', speed_wanted)
    while speed_wanted <= speed:
        speed = abs(vector_length(vector_between_vectors(vessel_velocity(), target_velocity())))
        frac = speed / start_speed
        vessel.control.throttle = 1 * frac
        pass
    vessel.control.throttle = 0.0


def Payload_separation():
    # getting the index number of the active_vessel
    transporter = sc.vessels.index(sc.active_vessel)


    # Orient vessel 90 degree to target

    # open up cargo bay & switch on lights
    print('opening Cargo Bay')
    vessel.control.toggle_action_group(7)
    for part in vessel.parts.lights:
        part.active = True
    time.sleep(10)

    # separate payload
    print('Decoupling Payload')
    for part in vessel.parts.decouplers:
        part.decouple()

    #switch to payload
    print('Jump to Payload')
    wsh.AppActivate("Kerbal Space Program")
    wsh.SendKeys("]")  # send the keys you want

    #get index number of payload
    payload = sc.vessels.index(sc.active_vessel)

    time.sleep(4)

    # jump back to active_vessel
    print('Jump back to Space Plane')
    sc.active_vessel = sc.vessels[transporter]


    # pushback from payload
    print('Pushback from Payload')
    vessel.control.rcs = True
    vessel.control.up = -1
    time.sleep(1)
    vessel.control.up = 0
    vessel.control.rcs = False

    time.sleep(3)

    # jump to payload
    print('Jump to Payload')
    sc.active_vessel = sc.vessels[payload]

    # wait unitl distance between both vessels is 20 m
    print('Wait for distance between Payload and Ship')
    distance = vector_length(vector_between_vectors(sc.vessels[transporter].position(obt_frame), sc.vessels[payload].position(obt_frame)))
    while distance < 20:
        distance = vector_length(vector_between_vectors(sc.vessels[transporter].position(obt_frame),
                                                        sc.vessels[payload].position(obt_frame)))
        time.sleep(1)

    time.sleep(3)

    # switch off lights
    print('Payload separation complete')
    for part in vessel.parts.lights:
        part.active = False

def docking_alignment(conn, v, t):
    return


def docking_maneuver(conn, v, t):
    return


###############################################################################
##                      Major Calculation Functions
##    Mid Level Functions that perform the calculations required for the maneuvers
###############################################################################

def time_to_coincidence(target_altitude, vessel_altitude):
    #calculates the time where the angle between two objects in different orbits is 0

    target_period = orbital_period(target_altitude)
    print('target period:', target_period)

    vessel_period = orbital_period(vessel_altitude)
    print('vessel period:', vessel_period)

    coincidence_time = coincidence(vessel_period, target_period)
    print('coincidence:', coincidence_time)
    print(towards_angle())

    coi_per_degree = coincidence_time/(2*math.pi)
    if towards_angle() < 0:
        return towards_angle()*coi_per_degree
    else:
        return abs((math.pi+towards_angle()) * coi_per_degree)


#calculates the current angle towards an angle in orbit
def towards_angle():
    phase_angle = angle_between_two_vectors(vessel.position(obt_frame), target.position(obt_frame))
    angular_difference = angular_diff()

    return phase_angle + angular_difference

def burn_time(delta_v):
    # Calculate burn time (using rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = ((m0 - m1) / flow_rate)
    print('burn time:', burn_time)
    return burn_time

###############################################################################
##                      Vector Functions
##    All functions dealing with calculating Vectors
###############################################################################

def angle_between_two_vectors(v1, v2):
    # this function calculates the angle between two vectors
    dot = v2[0] * v1[0] + v2[2] * v1[2]
    det = v2[0] * v1[2] - v1[0] * v2[2]

    return math.atan2(det, dot)


def vector_between_vectors(v1, v2):
    # this function calculates the vector between two vectors (or points) as |v1v2|
    vector = [
        v2[0] - v1[0],
        v2[1] - v1[1],
        v2[2] - v1[2]
    ]

    return vector

def vector_length(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)

def angular_diff():
    # calculates the difference between two angles
    vessel_orbit = vessel.position(obt_frame)
    target_orbit = target.position(obt_frame)
    r1 = vessel.orbit.semi_major_axis
    r2= ((target_orbit[0]**2 + target_orbit[2]**2)**0.5)

    return (math.pi * ((1 - (1 / (2 * math.sqrt(2))) * math.sqrt((r1 / r2 + 1) ** 3))))

###############################################################################
##                      Orbital Mechanics
##          All functions related to Orbital Mechanics
###############################################################################
def delta_v1():
    vessel_orbit = vessel.position(obt_frame)
    target_orbit = target.position(obt_frame)
    r1 = vessel.orbit.semi_major_axis
    r2= ((target_orbit[0]**2 + target_orbit[2]**2)**0.5)

    return math.sqrt(mu/r1)*((math.sqrt(2*r2/(r1+r2)))-1)

def delta_v2():
    vessel_orbit = vessel.position(obt_frame)
    target_orbit = target.position(obt_frame)
    r1 = vessel.orbit.semi_major_axis
    r2= ((target_orbit[0]**2 + target_orbit[2]**2)**0.5)

    return math.sqrt(mu/r2)*(1-(math.sqrt(2*r1/(r1+r2))))

def orbital_period(altitude):
    import math
    mu = sc.active_vessel.orbit.body.gravitational_parameter
    r = altitude + 600000
    return 2 * math.pi * math.sqrt((r ** 3) / mu)

def coincidence(orbital_period1, orbital_period2):
    #calculates the time between two orbital objects conicide ("meet" at the same point in orbit)
    return (orbital_period1 * orbital_period2) / (orbital_period1 - orbital_period2)

def orbital_velocity(altitude):
    #calculates the speed a vessel needs to have for a circular orbit
    return math.sqrt(mu/(altitude+600000))

###############################################################################
##                      Helper Functions
##    Low Level Functions - mostly designed for internal use
###############################################################################

def time_warp_up(warp):
    if warp >= 2:
        sc.rails_warp_factor = 1
        time.sleep(1)
        sc.rails_warp_factor = 2
        time.sleep(1)
    if warp >= 3:
        sc.rails_warp_factor = 3
        time.sleep(1)
    if warp >= 4:
        sc.rails_warp_factor = 4
        time.sleep(1)
    if warp >= 5:
        sc.rails_warp_factor = 5
        time.sleep(1)

def time_warp_stop():
    sc.rails_warp_factor = 0





