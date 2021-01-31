class Atmospheric_Flight:
    """everything for flying and airplane"""
    def __init__(self):
            # frame of reference
        self.srf_frame = vessel.orbit.body.reference_frame
        self.speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')

    def show_speed(speed):
        print(speed)

import krpc
conn = krpc.connect(name='Automated Orbit')
vessel = conn.space_center.active_vessel
Atmospheric_Flight.show_speed()
