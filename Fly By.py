import math
import time
import krpc
import Direction


# Telemetry:
conn = krpc.connect(name='Vessel deorbit')
vessel = conn.space_center.active_vessel
obt_frame = vessel.orbit.body.non_rotating_reference_frame
srf_frame = vessel.orbit.body.reference_frame
orb_speed = conn.add_stream(getattr, vessel.flight(obt_frame), 'speed')
altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
long = conn.add_stream(getattr, vessel.flight(obt_frame), 'longitude')
lat = conn.add_stream(getattr, vessel.flight(obt_frame), 'latitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
ap = vessel.auto_pilot

# pre-launch setup
vessel.control.brakes = True
vessel.control.sas = True
#vessel.auto_pilot.engage()
#vessel.auto_pilot.target_heading = 90
vessel.control.throttle = 1

print('ready to start')
time.sleep(2)

# full throttle
print('engage engines - full throttle')
vessel.control.activate_next_stage()
time.sleep(3)
vessel.control.brakes = False

# Rotate
while srf_speed() < 60:
    time.sleep(1)

vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(10, 90)
ap.target_roll = 0
vessel.control.sas = False
print('rotate')

# retracting wheels
while altitude() < 10:
    time.sleep(1)
print('retracting wheels')
vessel.control.toggle_action_group(0)
time.sleep(1)
vessel.control.toggle_action_group(0)

#lat, long, alt
pos = [[-0.050190213676223706, -74.0, 1500.0, 250, 1000],
       [-1.150190213676223706, -74.0, 2000.0, 250, 1000],
       [-1.150190213676223706, -77.5, 6000.0, 300, 1000],
       [-0.04860097852994589, -77.5, 6000.0, 200, 2000],
       [-0.04860097852994589, -76.5, 4000.0, 200, 1000],
       [-0.04860097852994589, -75.5, 1500.0, 150, 1000],
       [-0.04860097852994589, -75.0, 800.0, 120, 1000],
       [-0.04860097852994589, -74.85, 300.0, 110, 150, True],
       [-0.04860097852994589, -74.70438019083467, 100.0, 80, 120],
       [-0.04860097852994589, -74.49466027017348, 100.0, 50, 120]]

Direction.auto_pilot(pos)
vessel.control.throttle = 0.0
while srf_speed() >= 1.0\
        :
    if altitude() >= 14.0:
        vessel.auto_pilot.target_pitch_and_heading(-5, 90)
        print('up')
    elif altitude() <= 10.0:
        vessel.auto_pilot.target_pitch_and_heading(5, 90)
        print('down')
    else:
        vessel.auto_pilot.target_pitch_and_heading(0, 90)

print('done')