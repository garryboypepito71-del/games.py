
"""
Cyber Racer PRO: Infinite Overdrive
- 10 Playable Characters/Cars (Press TAB to switch)
- Unlimited Money System ($9,999,999)
- Real-time Upgrades (Press U to upgrade speed)
- Bug Fixes: Steering and projectile logic improved.
"""

import subprocess, sys, json
from pathlib import Path
import streamlit as st

GAME_CODE = r"""
from ursina import *
import random

app = Ursina()
window.title = 'Cyber Racer PRO: Infinite Overdrive'
window.borderless = False
window.color = color.black

# Global Stats
money = 9999999
health = 100
energy = 100
kills = 0
current_car_index = 0

# Car Library (10 unique vehicles)
CAR_DATA = [
    {'name': 'Neon Scout', 'color': color.cyan, 'speed': 25, 'armor': 100, 'scale': (1.5, 0.8, 3.5)},
    {'name': 'Shadow Blade', 'color': color.black, 'speed': 35, 'armor': 80, 'scale': (1.2, 0.6, 4)},
    {'name': 'Titan Tank', 'color': color.gray, 'speed': 15, 'armor': 300, 'scale': (2.5, 1.2, 4.5)},
    {'name': 'Plasma Flyer', 'color': color.violet, 'speed': 45, 'armor': 60, 'scale': (1.4, 0.5, 3.8)},
    {'name': 'Infernus', 'color': color.red, 'speed': 40, 'armor': 120, 'scale': (1.6, 0.9, 3.6)},
    {'name': 'Acid Driver', 'color': color.lime, 'speed': 30, 'armor': 150, 'scale': (1.8, 1, 3.5)},
    {'name': 'Ghost', 'color': color.white, 'speed': 50, 'armor': 40, 'scale': (1.1, 0.5, 3.2)},
    {'name': 'Gold Rush', 'color': color.gold, 'speed': 28, 'armor': 200, 'scale': (2, 1.1, 4)},
    {'name': 'Vanguard', 'color': color.blue, 'speed': 32, 'armor': 180, 'scale': (1.7, 0.9, 3.7)},
    {'name': 'Zenith', 'color': color.orange, 'speed': 38, 'armor': 110, 'scale': (1.5, 0.7, 3.4)},
]

# Arena
ground = Entity(model='plane', scale=(200, 1, 200), texture='white_cube', color=color.black, collider='box')
for i in range(-100, 101, 10):
    Entity(model='cube', scale=(200, 0.05, 0.1), position=(0, 0.01, i), color=color.rgba(0, 255, 255, 50))
    Entity(model='cube', scale=(0.1, 0.05, 200), position=(i, 0.01, 0), color=color.rgba(0, 255, 255, 50))

# Player Setup
player = Entity(model='cube', collider='box', position=(0, 0.5, 0))
thruster_l = Entity(parent=player, model='cube', color=color.magenta, scale=(0.3, 0.3, 0.5), position=(0.4, 0, -1.8))
thruster_r = Entity(parent=player, model='cube', color=color.magenta, scale=(0.3, 0.3, 0.5), position=(-0.4, 0, -1.8))

def update_car_stats():
    car = CAR_DATA[current_car_index]
    player.model = 'cube'
    player.color = car['color']
    player.scale = car['scale']
    global speed, health
    speed = car['speed']
    health = car['armor']

update_car_stats()

# Enemy System
enemies = []
def spawn_enemy():
    e = Entity(model='cube', color=color.red, scale=(2, 1, 3), position=(random.uniform(-80, 80), 0.5, random.uniform(-80, 80)), collider='box')
    e.health = 3
    enemies.append(e)

for _ in range(12): spawn_enemy()

# HUD
ui_parent = Entity(parent=camera.ui)
health_bar = Entity(parent=ui_parent, model='quad', color=color.green, origin=(-.5,0), scale=(.5, .03), position=(-0.85, 0.45))
energy_bar = Entity(parent=ui_parent, model='quad', color=color.yellow, origin=(-.5,0), scale=(.5, .02), position=(-0.85, 0.41))
info_text = Text(text='', position=(-0.85, 0.37), scale=1.2, color=color.gold)

# Camera
camera.parent = player
camera.position = (0, 10, -20)
camera.rotation_x = 25

projectiles = []

def shoot():
    b = Entity(model='sphere', scale=0.5, color=player.color, position=player.position + player.forward * 4 + Vec3(0, 0.5, 0), collider='sphere')
    b.direction = player.forward
    b.life = 2.0
    projectiles.append(b)

def input(key):
    global current_car_index, money
    if key == 'space': shoot()
    if key == 'tab': # Cycle Cars
        current_car_index = (current_car_index + 1) % len(CAR_DATA)
        update_car_stats()
    if key == 'u' and money >= 1000: # Instant Upgrade Simulation
        money -= 1000
        global speed
        speed += 5

def update():
    global health, energy, kills, money
    info_text.text = f'CASH: ${money} | KILLS: {kills} | UNIT: {CAR_DATA[current_car_index]["name"]}'
    
    energy = min(100, energy + 10 * time.dt)
    energy_bar.scale_x = (energy / 100) * 0.5

    # Movement Fix
    move_dir = player.forward * (held_keys['w'] - held_keys['s'])
    player.position += move_dir * speed * time.dt
    player.rotation_y += (held_keys['d'] - held_keys['a']) * 120 * time.dt

    for e in list(enemies):
        e.look_at(player)
        e.position += e.forward * 10 * time.dt
        if distance(e, player) < 3:
            health -= 30 * time.dt
            health_bar.scale_x = max(0, (health / CAR_DATA[current_car_index]['armor']) * 0.5)

    for b in list(projectiles):
        b.position += b.direction * 100 * time.dt
        b.life -= time.dt
        if b.life <= 0:
            destroy(b)
            projectiles.remove(b)
            continue
        for e in list(enemies):
            if distance(b, e) < 2.5:
                e.health -= 1
                destroy(b)
                if b in projectiles: projectiles.remove(b)
                if e.health <= 0:
                    destroy(e)
                    enemies.remove(e)
                    kills += 1
                    money += 500
                    spawn_enemy()
                break

    if health <= 0:
        Text(text='CRITICAL FAILURE: SYSTEM RESET', origin=(0,0), scale=3, color=color.red, background=True)
        application.pause()

Sky(color=color.black)
app.run()
"""

def launch():
    p = Path(__file__).with_name("_pro_runtime.py")
    p.write_text(GAME_CODE, encoding="utf-8")
    subprocess.Popen([sys.executable, str(p)])

def main():
    st.set_page_config(page_title="Cyber Racer PRO", layout="wide")
    st.title("🛡️ Cyber Racer PRO: Infinite Overdrive")
    st.write("Professional Edition with Unlimited Resources & 10-Car Garage.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Pro Features Active")
        st.success("✅ Unlimited Cash: $9,999,999")
        st.success("✅ 10 Vehicles Unlocked")
        st.success("✅ High-Resolution Physics Fix")
        if st.button("LAUNCH PRO ENGINE"):
            launch()
            st.info("Game window active.")

    with col2:
        st.subheader("🕹️ Keybinds")
        st.code("W/A/S/D: Drive\nSPACE: Pulse Cannon\nTAB: Cycle 10 Characters\nU: Instant Engine Upgrade")

if __name__ == "__main__":
    main()
