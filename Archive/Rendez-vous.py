import math
import time
import krpc
import Direction


# Telemetry:
conn = krpc.connect(name='Try out')
vessel = conn.space_center.active_vessel
obt_frame = vessel.orbit.body.non_rotating_reference_frame
srf_frame = vessel.orbit.body.reference_frame
orb_speed = conn.add_stream(getattr, vessel.flight(obt_frame), 'speed')
altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
long = conn.add_stream(getattr, vessel.flight(obt_frame), 'longitude')
lat = conn.add_stream(getattr, vessel.flight(obt_frame), 'latitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
mu = vessel.orbit.body.gravitational_parameter
ut = conn.add_stream(getattr, conn.space_center, 'ut')
ap = vessel.auto_pilot
time_accel = True

#throttleing engines
vessel.control.toggle_action_group(8)
for engine in vessel.parts.engines:
    engine.thrust_limit = 0.2


angle = 10
angular_diff = 15

conn.space_center.rails_warp_factor = 1
time.sleep(1)
conn.space_center.rails_warp_factor = 2

while abs(angle+angular_diff) >= 0.00001:
    #calculating Holman transfer
    vessel_orbit = vessel.position(obt_frame)
    target_orbit = conn.space_center.target_vessel.position(obt_frame)
    r1 = vessel.orbit.semi_major_axis
    r2= ((target_orbit[0]**2 + target_orbit[2]**2)**0.5)

    delta_v1 = math.sqrt(mu/r1)*((math.sqrt(2*r2/(r1+r2)))-1)
    delta_v2 = math.sqrt(mu/r2)*(1-(math.sqrt(2*r1/(r1+r2))))

    angular_diff = (math.pi * ((1 - (1 / (2 * math.sqrt(2))) * math.sqrt((r1 / r2 + 1) ** 3))))

    # phase angle
    dot = target_orbit[0] * vessel_orbit[0] + target_orbit[2] * vessel_orbit[2]
    det = target_orbit[0] * vessel_orbit[2] - vessel_orbit[0] * target_orbit[2]
    angle = math.atan2(det, dot)

    print("Angle Difference:", abs(angle+angular_diff))

    if abs(angle+angular_diff) <= 0.01 and time_accel:
        conn.space_center.rails_warp_factor = 0
        ap.sas = True
        #vessel.control.rcs = True
        time.sleep(1)
        ap.sas_mode = ap.sas_mode.prograde
        time.sleep(1)
        time_accel = False

    time.sleep(0.01)

#setting node v1
#
# vessel.control.add_node(ut = ut(), prograde=delta_v1 )
# vessel.control.rcs = False

#executing node v1
speed_wanted = orb_speed() +delta_v1

vessel.control.throttle = 1
while speed_wanted >= orb_speed():
    pass
vessel.control.throttle = 0.0

#setting node v2
#vessel.control.add_node(ut = ut()+vessel.orbit.time_to_apoapsis, prograde=delta_v2 )
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v2 / Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate
print(burn_time)
time.sleep(1)
# wait for burn time comming up
burn_ut = ut() + time_to_apoapsis() - (burn_time)
lead_time = 18
conn.space_center.warp_to(burn_ut - lead_time)

while time_to_apoapsis() > burn_time:
    #print('waiting')
    time.sleep(0.001)


# executing burn v2
print('starting circularization burn')
throttle = 1
checker3 = False
while periapsis() < apoapsis() - 1:
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

#reducing speed to target to 0
vessel.control.speed_mode = vessel.control.speed_mode.target
ap.sas = True
vessel.control.rcs = True
ap.sas_mode = ap.sas_mode.retrograte
time.sleep(12)
vessel.control.throttle = 1
while speed_wanted >= orb_speed():
    pass
vessel.control.throttle = 0.0










print(r1)
print(r2)
print(delta_v1)
print(delta_v2)
print(angular_diff)
print(angle)

    #time.sleep(1)
