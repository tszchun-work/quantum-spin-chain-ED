import numpy as np
from numba import jit
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import os

"""
The first section below is for setting simulation parameters.
All numbers are in SI units. (We may normalize them later.)
One may adjust various parameters to try different settings.
Moon-earth distance: The moon was closer to earth at the beginning of solar system.
Recession rate: Its exact variation over the evolution of the moon-earth system is not clearly known.
Radius of dust: It affects how easy it is to collide with earth or moon.
Angular speed/ acceleration: They affect the centrifugal, coriolis forces, and the euler force, and depends on the recession rate.
(Though the dependence is not taken into account below)
"""

# Physical constants
gravi_constant = 6.67e-11
mass_of_earth = 5.97e24 # earth
radius_of_earth = 6.371e6
mass_of_moon = 7.35e22 # moon
radius_of_moon = 1.737e6
radius_of_dust = 1e5 # dust
moon_earth_distance = 21 * radius_of_earth # moon-earth
recession_rate = 1e-4

# Parameters for rotating frame
angular_speed = np.sqrt(gravi_constant * (mass_of_earth + mass_of_moon) / moon_earth_distance**3)
angular_acceleration = -1e-20

"""
Below are the simulation parameters.
All numbers are in SI units.
Note the difference between time step and the number of steps skipped per frame.
During animation, frames are updated.
In between each frame, the simulation runs for several time steps.
The number of times the simulation runs between frames is defined as the number of steps skipped per frame.
This is to reduce the computational costs for rendering the animation.
"""

# Simulation parameters
time_step = 100
number_of_dust = 1000
number_of_iter_skipped_per_step = 3000
number_of_year_per_frame = number_of_iter_skipped_per_step * time_step / (365 * 24 * 3600)
number_of_dust_fallen_on_earth = 0
number_of_dust_fallen_on_moon = 0
screenshot_interval_year = 1 # in years
image_folder = f"simulation_screenshots_dt={str(time_step)}_n={str(number_of_dust)}_rec={str(recession_rate)}"
print(f"Parameters of this simulation: time step={time_step}, number of dust={number_of_dust}, recession rate={recession_rate}")

"""
We initialize the positions and velocities of earth, moon and dust particles below.
The earth and moon are initialized such that their centre of mass is exactly the origin.
The dust are initialized at randomly around L4, L5, as well as everywhere else.
"""

# Initial positions
position_of_earth = np.array([-mass_of_moon * moon_earth_distance / (mass_of_earth + mass_of_moon), 
                              0.0])
position_of_moon = np.array([mass_of_earth * moon_earth_distance / (mass_of_earth + mass_of_moon), 
                             0.0])
position_of_L4 = np.array([(position_of_moon[0] - position_of_earth[0]) * np.cos(np.pi/3) + position_of_earth[0],
                           (position_of_moon[0] - position_of_earth[0]) * np.sin(np.pi/3)])
position_of_L5 = np.array([(position_of_moon[0] - position_of_earth[0]) * np.cos(-np.pi/3) + position_of_earth[0],
                           (position_of_moon[0] - position_of_earth[0]) * np.sin(-np.pi/3)])

# Create dust particles at both L4 and L5 points
particles_per_group = number_of_dust // 3
remaining_particles = number_of_dust - (2 * particles_per_group)

position_of_dust_at_L4 = position_of_L4 + 0.08 * moon_earth_distance * np.random.normal(loc=0, scale=0.1, size=(particles_per_group, 2))
position_of_dust_at_L5 = position_of_L5 + 0.08 * moon_earth_distance * np.random.normal(loc=0, scale=0.1, size=(particles_per_group, 2))
position_of_random_dust = moon_earth_distance * np.random.normal(loc=0, scale=1.5, size=(remaining_particles, 2))
position_of_dust = np.concatenate([position_of_dust_at_L4, position_of_dust_at_L5, position_of_random_dust], axis=0).astype(np.float64)
assert position_of_dust.shape[0] == number_of_dust, f"Expected {number_of_dust} particles, got {position_of_dust.shape[0]}" # Ensure we have exactly the right number of particles

# Initial velocities
velocity_of_earth = np.array([0.0, 0.0], dtype=np.float64)
velocity_of_moon = np.array([0.0, 0.0], dtype=np.float64)
velocity_of_dust = np.zeros((number_of_dust, 2), dtype=np.float64)

"""
Below are functions used for creating subplots and saving screenshots.
ax1 is the plot for the simulation of earth, moon and dust particles.
ax2 is the plot for the collision history of dust particles with earth and moon.
The save_screenshot function saves the current state of the simulation to a PNG file.
The create_subplots function initializes the two subplots for each screenshot.
"""

def create_subplots(current_time):
    # Set up motion plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    ax1.set_xlim([-2 * moon_earth_distance, 2 * moon_earth_distance])
    ax1.set_ylim([-2 * moon_earth_distance, 2 * moon_earth_distance])
    ax1.set_title(f"Simulation Time: {current_time:.2f}")
    ax1.set_aspect('equal')
    ax1.set_facecolor('white')

    # Setup collision history plot
    ax2.set_xlim([0, max(100, current_time)])
    ax2.set_ylim([0, number_of_dust / 10])
    ax2.set_xlabel('Time (years)')
    ax2.set_ylabel('Number of Fallen Dust')
    ax2.set_title('Collision History')
    ax2.grid(True)
    
    return fig, ax1, ax2

# Screenshot function
def save_screenshot(position_of_earth, position_of_moon, position_of_dust,
                    active_mask, time_data, earth_collision_data,
                    moon_collision_data, folder):
    
    # Check if folder exists, if not create it
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Create a new figure for each screenshot
    fig, ax1, ax2 = create_subplots(time_data[-1])
    
    # Plot the objects of ax1
    active_rD = position_of_dust[active_mask] # select active dust
    ax1.scatter(position_of_earth[0], position_of_earth[1], color='blue', s=100, label='Earth') # earth
    ax1.scatter(position_of_moon[0], position_of_moon[1], color='gray', s=50, label='Moon') # moon
    ax1.scatter(active_rD[:, 0], active_rD[:, 1], color='red', s=1, alpha=0.5, label='Dust') # dust

    ax1.text(0.75*moon_earth_distance, 1.85*moon_earth_distance, f"Time: {time_data[-1]:.3f} years") # timer
    ax1.text(0.75*moon_earth_distance, 1.75*moon_earth_distance, f"Earth: {earth_collision_data[-1]} Dust") # earth counter
    ax1.text(0.75*moon_earth_distance, 1.65*moon_earth_distance, f"Moon: {moon_collision_data[-1]} Dust") # moon counter
    ax1.text(0.75*moon_earth_distance, 1.55*moon_earth_distance, f"Number of Dust: {np.sum(active_mask)} Dust") # dust counter

    # Plot the collision history
    ax2.plot(time_data, earth_collision_data, 'o', color='blue', markersize=4, label='Earth') # earth
    ax2.plot(time_data, moon_collision_data, 'o', color='red', markersize=4, label='Moon') # moon
    ax2.legend()

    # Save to file
    filename = os.path.join(folder, f"step_{int(time_data[-1]):06d}.png")
    fig.savefig(filename)
    plt.close() # Important: close the figure to free up memory
    print(f"Saved: {filename}")

# Initialize simulation time
current_time = 0.0
last_screenshot_time = -screenshot_interval_year # To trigger one at t=0

# Initialize active mask (all dust particles are initially active)
active_mask = np.ones(number_of_dust, dtype=bool)  # True means the particle is active

# Data for plotting collision history
time_data = []
earth_collision_data = []
moon_collision_data = []

"""
Below are functions used in the JIT-accelerated RK4 simulation.
norm is defined instead of using np.linalg.norm because the latter is not supported in Numba JIT.
compute_acceleration computes the total acceleration on each dust particle due to gravitational and fictitious forces.
do_step performs several RK4 steps in between each frame.
"""

@jit(nopython=True)
def norm(arr):
    return np.sqrt(np.sum(arr**2, axis=1))

@jit(nopython=True)
def compute_acceleration(rD, vD, rDE, rDM, norm_rDE, norm_rDM, w, dwdt, 
                         gravi_constant, mass_of_earth, mass_of_moon):
    
    # Gravitational accelerations (avoid division by zero)
    norm_rDE_safe = np.maximum(norm_rDE, 1e-10)
    norm_rDM_safe = np.maximum(norm_rDM, 1e-10)
    
    # Calculate accelerations
    aD = np.zeros_like(rD)
    
    for i in range(rDE.shape[0]):

        # Denominators
        denom_E = norm_rDE_safe[i]**3
        denom_M = norm_rDM_safe[i]**3
        
        # Gravitational acceleration components
        aD[i, 0] += (-gravi_constant * mass_of_earth * rDE[i, 0] / denom_E # earth
                     -gravi_constant * mass_of_moon * rDM[i, 0] / denom_M # moon
                     -2 * (-w * vD[i, 1]) # coriolis
                     +w**2 * rD[i, 0] # centrifugal
                     -(-dwdt * rD[i, 1])) # euler
        aD[i, 1] += (-gravi_constant * mass_of_earth * rDE[i, 1] / denom_E 
                     -gravi_constant * mass_of_moon * rDM[i, 1] / denom_M
                     -2 * (w * vD[i, 0])
                     +w**2 * rD[i, 1]
                     -(dwdt * rD[i, 0]))
    return aD

@jit(nopython=True)
def rk4(rD, vD, dt, rE, rM, w, dwdt, 
        gravi_constant, mass_of_earth, mass_of_moon):
    
    # We must re-calculate relative positions for the intermediate RK4 steps
    # Note: Strictly speaking, rE and rM move slightly during dt, but usually 
    # in RK4 for N-body, we use the t=0 positions or drift them. 
    # For simplicity here, we assume rE/rM are constant during the tiny dt step 
    # OR you need to pass drift logic. Assuming static for the sub-step:
    
    # Pre-calc for k1
    rDE = rD - rE
    rDM = rD - rM
    n_rDE = norm(rDE)
    n_rDM = norm(rDM)
    
    k1_v = compute_acceleration(rD, vD, rDE, rDM, n_rDE, n_rDM, w, dwdt, gravi_constant, mass_of_earth, mass_of_moon)
    k1_r = vD

    # Step 2
    rD_k2 = rD + 0.5 * k1_r * dt
    vD_k2 = vD + 0.5 * k1_v * dt
    rDE_k2 = rD_k2 - rE
    rDM_k2 = rD_k2 - rM
    n_rDE_k2 = norm(rDE_k2)
    n_rDM_k2 = norm(rDM_k2)
    
    k2_v = compute_acceleration(rD_k2, vD_k2, rDE_k2, rDM_k2, n_rDE_k2, n_rDM_k2, w, dwdt, gravi_constant, mass_of_earth, mass_of_moon)
    k2_r = vD + 0.5 * k1_v * dt

    # Step 3
    rD_k3 = rD + 0.5 * k2_r * dt
    vD_k3 = vD + 0.5 * k2_v * dt
    rDE_k3 = rD_k3 - rE
    rDM_k3 = rD_k3 - rM
    n_rDE_k3 = norm(rDE_k3)
    n_rDM_k3 = norm(rDM_k3)

    k3_v = compute_acceleration(rD_k3, vD_k3, rDE_k3, rDM_k3, n_rDE_k3, n_rDM_k3, w, dwdt, gravi_constant, mass_of_earth, mass_of_moon)
    k3_r = vD + 0.5 * k2_v * dt

    # Step 4
    rD_k4 = rD + k3_r * dt
    vD_k4 = vD + k3_v * dt
    rDE_k4 = rD_k4 - rE
    rDM_k4 = rD_k4 - rM
    n_rDE_k4 = norm(rDE_k4)
    n_rDM_k4 = norm(rDM_k4)

    k4_v = compute_acceleration(rD_k4, vD_k4, rDE_k4, rDM_k4, n_rDE_k4, n_rDM_k4, w, dwdt, gravi_constant, mass_of_earth, mass_of_moon)
    k4_r = vD + k3_v * dt

    rD_new = rD + (k1_r + 2*k2_r + 2*k3_r + k4_r) * (dt / 6)
    vD_new = vD + (k1_v + 2*k2_v + 2*k3_v + k4_v) * (dt / 6)

    return rD_new, vD_new

@jit(nopython=True)
def do_step(rE, vE, rM, vM, rD, vD, active_mask, w, dwdt, 
            time_step, recession_rate, 
            gravi_constant, mass_of_earth, mass_of_moon, 
            radius_of_earth, radius_of_moon, radius_of_dust,
            number_of_step_skipped_per_frame=10):

    # Recount for every frame
    collision_count_earth = 0
    collision_count_moon = 0

    for _ in range(number_of_step_skipped_per_frame):
        
        # 1. Update positions (Physics Integration)
        # Note: We pass rE/rM into RK4 so it can calculate rDE/rDM internally for the steps
        rD, vD = rk4(rD, vD, time_step, rE, rM, w, dwdt, gravi_constant, mass_of_earth, mass_of_moon)

        # 2. Check Collisions (Post-integration check)
        # Calculate current distances for collision check
        rDE = rD - rE
        rDM = rD - rM
        norm_rDE = norm(rDE)
        norm_rDM = norm(rDM)
        
        earth_collision_mask = norm_rDE < (radius_of_earth + radius_of_dust)
        moon_collision_mask = norm_rDM < (radius_of_moon + radius_of_dust)

        # Count collisions only for currently active particles
        collision_count_earth += np.sum(earth_collision_mask & active_mask)
        collision_count_moon += np.sum(moon_collision_mask & active_mask)

        # Deactivate
        active_mask &= ~(earth_collision_mask | moon_collision_mask)

        # 3. Move Celestial Bodies
        rM[0] += recession_rate * time_step
        rE[0] -= (mass_of_moon / mass_of_earth) * recession_rate * time_step

        # 4. Update Rotating Frame
        w += dwdt * time_step

    return collision_count_earth, collision_count_moon, w, rD, vD, active_mask

# Compilation
print("Compiling...")

# Make sure all inputs are the right type before calling the JIT function
earth_collisions, moon_collisions, w_updated, rD_updated, vD_updated, active_mask_updated = do_step(
    position_of_earth.copy(), velocity_of_earth.copy(), position_of_moon.copy(),
    velocity_of_moon.copy(), position_of_dust.copy(), velocity_of_dust.copy(),
    active_mask.copy(), angular_speed, angular_acceleration, time_step,
    recession_rate, gravi_constant, mass_of_earth, mass_of_moon, radius_of_earth,
    radius_of_moon, radius_of_dust, number_of_step_skipped_per_frame=1)

print("Finished compilation.")

"""
Below is the animatin part.
The update function is called for each frame.
Every frame, do_step is called and the plot is updated accordingly.
The animation is displayed and the elapsed time is printed.
"""

sim_start = time.time()
while current_time >= 0.0:
    
    # 1. Run a block of simulation using JIT
    earth_collisions, moon_collisions, angular_speed, position_of_dust, velocity_of_dust, active_mask = do_step(
        position_of_earth, velocity_of_earth, position_of_moon, velocity_of_moon,
        position_of_dust, velocity_of_dust, active_mask, angular_speed, angular_acceleration,
        time_step, recession_rate, gravi_constant, mass_of_earth, mass_of_moon, radius_of_earth,
        radius_of_moon, radius_of_dust, number_of_iter_skipped_per_step)
    
    # Update current time
    current_time +=  number_of_year_per_frame

    # Update collision counters
    number_of_dust_fallen_on_earth += earth_collisions
    number_of_dust_fallen_on_moon += moon_collisions
    
    # Store data for collision history plot
    time_data.append(current_time)
    earth_collision_data.append(earth_collisions)
    moon_collision_data.append(moon_collisions)
    
    # 2. Check if it's time for a screenshot
    if current_time - last_screenshot_time >= screenshot_interval_year:
        save_screenshot(position_of_earth, position_of_moon,
                        position_of_dust, active_mask, 
                        time_data, earth_collision_data, 
                        moon_collision_data, image_folder)
        last_screenshot_time = current_time

sim_end = time.time()
elapsed_time = sim_end - sim_start
print("Simulation completed in {:.2f} seconds.".format(elapsed_time))