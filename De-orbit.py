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

# deactivating auto.pilot
ap.disengage()
time.sleep(2)

# wait for de-orbit burn
conn.space_center.rails_warp_factor = 3
time.sleep(1)
while conn.space_center.rails_warp_factor != 3:
    conn.space_center.rails_warp_factor = 1
    print('time accelleration error\nengage manually to continue')
    time.sleep(3)
    conn.space_center.rails_warp_factor = 2
    time.sleep(3)

time.sleep(1)
# calculating the angle for return burn


while long() < 140 or long() > 145:
    time.sleep(0.1)

conn.space_center.rails_warp_factor = 0
print('waiting done')

# setting sas to retrograde
print('setting retrograde')
ap.sas = True
vessel.control.rcs = True
time.sleep(2)
ap.sas_mode = ap.sas_mode.retrograde
while ap.error >= 2:
    time.sleep(1)

# executing de-orbit burn
print('de-orbit burn')
time.sleep(1)
while periapsis() > 0:
    vessel.control.throttle = 1.0
vessel.control.throttle = 0.0
time.sleep(1)

# wait until descending into atmosphere
print('wait until entering the atmosphere')
time.sleep(1)
conn.space_center.rails_warp_factor = 2
while (altitude() // 73000) > 0:
    pass
conn.space_center.rails_warp_factor = 0
time.sleep(1)
print('entering atmosphere')

print('aerobraking')
ap.engage()
ap.stopping_time = (10, 10, 10)

ap.target_roll = 0
vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.control.rcs = True
while vessel.flight().roll > abs(5):
     ap.target_roll = 0
     print('roll error %.11f' % (vessel.flight().roll))
     time.sleep(0.85)
vessel.control.rcs = False
#calculating when aerobrake starts to work

while True:
    accel1 = srf_speed()
    time.sleep(0.25)
    accel0 = srf_speed()
    acceleration = (accel0 - accel1) * 4
    if acceleration < 0:
        break

ap.stopping_time = (0.5, 0.5, 0.5)

# aerobraking turn

print('aerobraking turn starts')
start_altitude = altitude()
end_altitude = 22500
turn_angle = 0
error = [9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999]
while altitude() > end_altitude:
    frac = ((start_altitude - altitude()) /
            (start_altitude - end_altitude))
    print('frac: %.11f' % frac)
    new_turn_angle = frac * 90
    vessel.auto_pilot.target_pitch_and_heading(90 - new_turn_angle, 90)
    if abs(ap.error) > 3 and vessel.control.rcs == False:
        vessel.control.rcs = True
    if vessel.control.rcs == True:

        error.insert(0, abs(ap.error))
        error.pop()
        time.sleep(0.25)
        error_median = sum(error) / len(error)
        print(error_median)
        if error_median <= 1:
            vessel.control.rcs = False

print('aerobraking turn ends')
while srf_speed() > 800:
    time.sleep(1)

# switching engines back on

print('switching jet engines on')
vessel.control.toggle_action_group(8)
for engine in vessel.parts.engines:
    engine.toggle_mode()
vessel.control.throttle = 0.3

if long() <= -79.0:
    print('approaching from East')
    pos = [[-0.04860097852994589, -78.5, 10000.0, 300, 2000],
           [-0.04860097852994589, -77.5, 8000.0, 300, 2000],
           [-0.04860097852994589, -76.5, 5000.0, 200, 1000],
           [-0.04860097852994589, -75.5, 2000.0, 150, 1000],
           [-0.04860097852994589, -75.0, 800.0, 120, 1000],
           [-0.04860097852994589, -74.85, 300.0, 110, 150, True],
           [-0.04860097852994589, -74.70438019083467, 100.0, 80, 120],
           [-0.04860097852994589, -74.49466027017348, 100.0, 0, 120]]

if long() >= -79.0:
    print('approaching from West')
    pos = [[-0.04860097852994589, -71.5, 6000.0, 200, 2000],
           [-0.04860097852994589, -72.5, 4000.0, 200, 1000],
           [-0.04860097852994589, -73.5, 1500.0, 150, 1000],
           [-0.04860097852994589, -74.0, 800.0, 120, 1000],
           [-0.04860097852994589, -74.35, 300.0, 110, 150, True],
           [-0.04860097852994589, -74.49466027017348, 100.0, 80, 120],
           [-0.04860097852994589, -74.72438019083467, 100.0, 0, 120]]

Direction.auto_pilot(pos)




