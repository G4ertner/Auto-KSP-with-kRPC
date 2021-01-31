import math
import time
import krpc
import Rendezvous
import Direction


# Telemetry:

conn = krpc.connect(name='Try out')
vessel = conn.space_center.active_vessel
target = conn.space_center.target_vessel
obt_frame = vessel.orbit.body.non_rotating_reference_frame
srf_frame = vessel.orbit.body.reference_frame
orb_speed = conn.add_stream(getattr, vessel.flight(obt_frame), 'speed')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
long = conn.add_stream(getattr, vessel.flight(obt_frame), 'longitude')
lat = conn.add_stream(getattr, vessel.flight(obt_frame), 'latitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
mu = vessel.orbit.body.gravitational_parameter
ut = conn.add_stream(getattr, conn.space_center, 'ut')
ap = vessel.auto_pilot

# vessel_vector = conn.space_center.active_vessel.position(obt_frame)
# target_vector = conn.space_center.target_vessel.position(obt_frame)

# vessel_velocity = conn.add_stream(getattr, vessel.flight(obt_frame), 'velocity')
# target_velocity = conn.add_stream(getattr, target.flight(obt_frame), 'velocity')

def angle_between_two_vectors_xz(v1, v2):
    # this function calculates the angle between two vectors on x and z axis
    dot = v2[0] * v1[0] + v2[2] * v1[2]
    det = v2[0] * v1[2] - v1[0] * v2[2]

    return math.atan2(det, dot)

def angle_between_two_vectors_xy(v1, v2):
    # this function calculates the angle between two vectors on x and z axis
    dot = v2[0] * v1[0] + v2[1] * v1[1]
    det = v2[0] * v1[1] - v1[0] * v2[1]

    return math.atan2(det, dot)

def angle_between_two_vectors_yz(v1, v2):
    # this function calculates the angle between two vectors on y and z axis
    dot = v2[1] * v1[1] + v2[2] * v1[2]
    det = v2[1] * v1[2] - v1[1] * v2[2]

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



def orbital_period(altitude):
    return 2*math.pi*math.sqrt(((600000+altitude)**3)/mu)

def coincidence(orbital_period1, orbital_period2):
    #calculates the time between two orbital objects conicide ("meet" at the same point in orbit)
    return (orbital_period1 * orbital_period2) / (orbital_period1 - orbital_period2)

def angle_between_two_vectors(v1, v2):
    # this function calculates the angle between two vectors
    dot = v2[0] * v1[0] + v2[2] * v1[2]
    det = v2[0] * v1[2] - v1[0] * v2[2]

    return math.atan2(det, dot)

def angular_diff():
    # calculates the difference between two angles
    vessel_orbit = vessel.position(obt_frame)
    target_orbit = target.position(obt_frame)
    r1 = vessel.orbit.semi_major_axis
    r2= ((target_orbit[0]**2 + target_orbit[2]**2)**0.5)

    return (math.pi * ((1 - (1 / (2 * math.sqrt(2))) * math.sqrt((r1 / r2 + 1) ** 3))))

def towards_angle():
    phase_angle = angle_between_two_vectors(vessel.position(obt_frame), target.position(obt_frame))
    angular_difference = angular_diff()

    return phase_angle + angular_difference

def approach_target():
    return




# #ap.engage()
# ap.target_roll = 0
# ap.sas = True
#
# time.sleep(2)
# ap.sas_mode = ap.sas_mode.target
# time.sleep(3)
# #ap.engage()
# ap.target_roll = 0
#
# ref_frame = obt_frame
#
# while True:
#     conn.drawing.clear()
#
#     vessel_position = vessel.position(obt_frame)
#     target_position = target.position(obt_frame)
#
#     vessel_target_vector = vector_between_vectors(vessel_position, target_position)
#
#     vessel_direction = conn.add_stream(getattr, vessel.flight(obt_frame), 'direction')
#     vessel_target_angle_xz = angle_between_two_vectors_xz(vessel_direction(), vessel_target_vector)
#     vessel_target_angle_yz = angle_between_two_vectors_yz(vessel_direction(), vessel_target_vector)
#
#     conn.drawing.add_direction((vessel_target_vector), ref_frame)
#     conn.drawing.add_direction((vessel_direction()), ref_frame)
#
#     print('angle xz: ', math.degrees(vessel_target_angle_xz))
#     print('angle yz: ', math.degrees(vessel_target_angle_yz))
#
#     if math.degrees(vessel_target_angle_xz) > 3:
#
#
#
#     time.sleep(1)



payload = conn.space_center.vessels.index(conn.space_center.active_vessel)

print(payload)
conn.space_center.active_vessel = conn.space_center.vessels[13]


