###########################################################################
### AUTOMATED ORBIT SCRIPT FOR SPACE PLANES				###
###########################################################################
###   									###
###  This script can fly a space plane with R.A.P.I.E.R engine(s) 	###
###  into a pre-set orbit					        ###
###   									###
###									###
###  									###
###  To do so, the following parameters need to be set:
###     1. All wheels need to have their deply function in
###     Action Group 0.
###									###
###  									###
###  Author: Nikolas Guttler				January, 2021	###
###  Template design: artwhaley						###
###########################################################################

###########################################################################
##                      Main Function					###
##  This is the main function that describes the different steps in the ###
##  procedure. The maneuver function needs to be called from the main 	###
##  script.                                                             ###
##                                                                      ###
##  The following variables can be defined:                             ###
##  target_apoapsis: How high shall the orbit be? (default 90 km)       ###
##  target_inclination: What inclination shall the orbit have?          ###
##  default 90 degree/equatorial orbit)                                 ###
##  take_off_speed: At what speed does the plane take off?              ###
##  (default 90m/s)                                                     ###
###########################################################################

def auto_orbit(target_apoapsis=90000, target_inclination=90, take_off_speed=90):

    Target_Apoapsis = target_apoapsis
    Target_Inclination = target_inclination
    Take_off_Speed = take_off_speed

###########################################################################
###			Modules & Game Connection			###
###	Importing all necessary modules as well as establishing		###						###
###		the connection to the ingame kRPC server		###						###
###########################################################################
    import krpc
    import time
    import math

    conn = krpc.connect(name='Automated Orbit')
    vessel = conn.space_center.active_vessel

###########################################################################
## 			Setting up Telemetry				###
##  In here are all neccessary telemetry connections needed to be 	###
##  		pulled directly from the game.				###
###########################################################################

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

###########################################################################
##                      Auto Orbit Function                             ###    
##                                                                      ###
## These are the procedural steps that make up the Auto Orbit function. ###
##                                                                      ###
##                                                                      ###
###########################################################################

# Take off sequence
    take_off

# Gaining supersonic speed


# Flying to high altitude and accellerate to max speed


# Switching to engines to space mode and burn to target apoapis


# Coasting out of atmosphere, calculating circularization burn,
# and waiting for circularization burn


# Executing circularization burn


# Ending script by removing nodes and deactivating auto pilot

  
###########################################################################
##                     Automated Functions				###
##    High Level Functions that perform each phase of the maneuver.	###
###########################################################################


def take_off():
# Setting pre-launch setup
    vessel.control.brakes = True
    vessel.control.sas = True
    vessel.control.throttle = 1


# Throttleing up
    print('engage engines - full throttle')
    vessel.control.activate_next_stage()
    time.sleep(3)
    vessel.control.brakes = False


# Rotate / Lift off
    while srf_speed() < take_off_speed:
        time.sleep(1)

    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(10, 90)
    vessel.control.sas = False
    print('rotate')


# Retracting wheels
    while altitude() < 80:
       time.sleep(1)
    print('retracting wheels')
    vessel.control.toggle_action_group(0)
    time.sleep(1)
    vessel.control.toggle_action_group(0)
        

# Rising to altitude of 1000 m & Pitching into level flight
    while altitude() < 1000:
        time.sleep(1)

    print('gaining speed to 450 m/s')

    # if engines are strong enough, skip level flight at 1000 m altitude
    if srf_speed() > 370:
        change_pitch(3)
        skip = False
    else:
        skip = True
    

# heading in chosen direction for orbital inclination
    if target_heading != 90:
        print('heading for desired inclination')
        heading = 90
        heading_2 = direction(target_heading, target_apoapsis)
        steering_heading(heading, heading_2)
        print('heading for orbit complete')
    if target_heading == 90:
        heading_2 = target_heading


# gaining speed to 450 m/s to unlock full power of supersonic engines
    print('gaining speed to 450 m/s')

    while srf_speed() < 450:
        time.sleep(1)

# Rising to altitude of 10 000 m
    if skip == False:
        print('Raising to 10 000 m altitude')
        change_pitch(10)
        
    while altitude() < 10000:
        time.sleep(1)
        
    print('gaining speed to 15000 m/s')

    # if engines are strong enough, skip level flight at altitude of 10 000 m
    
    if srf_speed() > 1200:
        change_pitch(4)

# Gaining speed until air breathing engines are maxed out
    testnum = [1, 1]
    while True:
        for index in range(len(testnum)):
            testnum[1] = srf_speed()
            time.sleep(0.25)
            testnum[0] = srf_speed()
        acceleration = (testnum[0] - testnum[1]) * 4
        if acceleration < 0:
            break
        ### TODO: Redo the acceleration calculation
    

# Switching Engines into closed cycle (space mode)
    print('switching to space mode')
    
    for engine in vessel.parts.engines:
        engine.toggle_mode()


# pitching to 20 degrees & Shuttin engines off when target apoapsis is reached
    while apoapsis() <= target_apoapsis:
        if pitch < target_pitch:
            change_pitch(20, 0.125)
        time.sleep(0.1)
    vessel.control.throttle = 0.0
    vessel.control.speed_mode = vessel.control.speed_mode.surface

    print('target apoapsis reached')
    

# Coasting out of atmosphere
    vessel.auto_pilot.disengage()
    time.sleep(1)
    ap = vessel.auto_pilot
    ap.sas = True
    time.sleep(1)
    ap.sas_mode = ap.sas_mode.prograde

    print('coasting out of atmosphere')

    while altitude() < 70000:
        time.sleep(1)
        ### TODO: ADD TIME ACCELLERATION
    vessel.control.speed_mode = vessel.control.speed_mode.orbit

# Calculate Delta V and duration for circularization burn


# Accelerate time until circularization burn is reached
    print('Waiting until circularization burn')
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time)
    lead_time = 12
    conn.space_center.warp_to(burn_ut - lead_time)


# Wait until burn starts
    while time_to_apoapsis() > burn_time:
    print('waiting')
    time.sleep(0.5)


# Execute burn until orbit is fully circularized
    perfect_circularization_burn()


# Remove burn node, deactivate vessel control, end script
    node.remove()
    vessel.control.sas = False
    print('Orbit done!')
    vessel.auto_pilot.disengage()


###########################################################################
##                      Atmospheric Flight Functions			###
##    Mid Level Functions that perform maneuvers required for   	###
##			    atmospheric flight.				###
###########################################################################

def fly_to_altitude(new_altitude):
    print('new target altitude: ', new_altitude, ' m')
    if altitude() < new_altitude:
        change_pitch(10)
        while altitude() < new_altitude:
            time.sleep(0.5)
        
    elif altitude() > new_altitude:
        change_pitch(-10)
        while altitude() > new_altitude:
            time.sleep(0.5)
    print('new target altitude ', new_altitude, 'm, reached')
    
def change_pitch(target_pitch=0, time_period=0.25):
# Changes the pitch over short period of time in seconds (time_period) to avoid too rapid pitch change
    Pitch = vessel.auto_pilot.target_pitch
    Target_Pitch = target_pitch
    # determines if pitch goes up (positive)or pitch goes down(negative)
    up_or_down = Target_Pitch - Start_Pitch
    if up_or_down > 0:
	while Pitch < Target_Pitch:
            vessel.auto_pilot.target_pitch = Pitch
            pitch += 0.25
	    time.sleep(time_period)

    
###########################################################################
##                      Orbital Mechanics				###
##          All functions related to Orbital Mechanics.			###
###########################################################################
    
def perfect_cirularization_burn():
    # This function circularizes an orbit down to 1 meter accuracy
    
    print('starting circularization burn')
    throttle = 1
    checker3 = False
    while periapsis() < apoapsis() - 1:
        if burn_time >= 5:
            testnum = time_to_apoapsis()
            time.sleep(0.25)
            burn_time = testnum
            
            if (time_to_apoapsis() // burn_time) <= 0:
                vessel.control.throttle = throttle
                checker3 = True
                
            elif (time_to_apoapsis() // burn_time) > 0 and checker3:
                throttle *= 0.9
                checker3 = False
                vessel.control.throttle = throttle * 0.2
                
        else:
            if (time_to_apoapsis() // burn_time) <= 0:
                vessel.control.throttle = throttle
                checker3 = True
                
            elif (time_to_apoapsis() // burn_time) > 0 and checker3:
                throttle *= 0.9
                checker3 = False
                vessel.control.throttle = throttle * 0.2
                
    vessel.control.throttle = 0
###########################################################################
##                      Helper Functions				###
##    Low Level Functions - mostly designed for internal use. 		###
###########################################################################


