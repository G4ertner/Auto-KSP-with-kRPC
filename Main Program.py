from future.moves import tkinter
import Rendezvous
import Auto_orbit

top = tkinter.Tk()

#define

    # The Rendevous Scritp
label_rendezvous = tkinter.Label(top, text='Start a rendez-vous as follows:\n1. Launch Space Plane.\n2. Select Target.\n3. Press \'Rendez-vous\'', anchor= "e", justify='left')
button_rendezvous = tkinter.Button(top, text='Rendez-vous', command=lambda: Rendezvous.rendez_vous())

    # The Auto_Orbit Script
# Enter Target Apoapsis
label_target_ap = tkinter.Label(top, text='Start auto_orbit as follows:\n1. Define the target Apoapsis in meters:', anchor= "e", justify='left')
entry_target_ap = tkinter.Entry(top)
entry_target_ap.insert(0, '90000')

# Enter Orbital Inclination
label_orbit_inc = tkinter.Label(top, text='2. Define the Orbital Inclination in degrees:', anchor= "e", justify='left')
entry_orbit_inc = tkinter.Entry(top)
entry_orbit_inc.insert(0, '90')

# Enter Take-off speed
label_takeoff = tkinter.Label(top, text='3. Define takeoff speed in m/s:', anchor= "e", justify='left')
entry_takeoff = tkinter.Entry(top)
entry_takeoff.insert(0, '100')
button_auto_orbit = tkinter.Button(top, text='Auto Orbit', command=lambda: Auto_orbit.auto_orbit(int(entry_target_ap.get()),int(entry_orbit_inc.get()), int(entry_takeoff.get())))

#place
label_rendezvous.pack()
button_rendezvous.pack()
label_target_ap.pack()
entry_target_ap.pack()
label_orbit_inc.pack()
entry_orbit_inc.pack()
label_takeoff.pack()
entry_takeoff.pack()
button_auto_orbit.pack()



top.mainloop()