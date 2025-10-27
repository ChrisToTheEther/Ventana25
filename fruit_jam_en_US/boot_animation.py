# SPDX-FileCopyrightText: 2025 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import displayio
import supervisor
import adafruit_fruitjam
from displayio import OnDiskBitmap, TileGrid
from launcher_config import LauncherConfig

# Load configuration
launcher_config = LauncherConfig()

# Set up display
display = supervisor.runtime.display
display.auto_refresh = False

# Set up I2C and check for DAC presence (for audio)
i2c = board.I2C()
while not i2c.try_lock():
    time.sleep(0.01)

tlv320_present = 0x18 in i2c.scan()
i2c.unlock()

# Display static bitmap image
bitmap = OnDiskBitmap("boot_animation_assets\Ventana95.bmp") 
tilegrid = TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)

main_group = displayio.Group()
main_group.append(tilegrid)
display.root_group = main_group
display.refresh()

# Play boot jingle if DAC present
if tlv320_present:
    # Use volume from config or default
    volume_level = launcher_config.audio_volume if "audio" in launcher_config.data and "volume" in launcher_config.data["audio"] else 0.7

    fjPeriphs = adafruit_fruitjam.peripherals.Peripherals(
        audio_output=launcher_config.audio_output,
        safe_volume_limit=launcher_config.audio_volume_override_danger
    )
    fjPeriphs.volume = volume_level

    # Path to the .wav file to play
    wave_file = "/boot_animation_assets/95Startup.wav"  

    # Play and wait for it to finish
    fjPeriphs.play_file(wave_file, False)

# Done — keep image up until system reload or next code runs
while fjPeriphs.audio.playing:
        pass


supervisor.set_next_code_file("code.py")
supervisor.reload()