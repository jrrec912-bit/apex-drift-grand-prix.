[app]
title = Apex Drift Grand Prix
package.name = apexdriftgrandprix
package.domain = com.jrrec.games
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,txt
version = 1.0.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1

# Pygame uses SDL; use the Pygame bootstrap supplied by python-for-android.
p4a.bootstrap = pygame

# Build a modern 64-bit Android APK.
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = True

# Keep the game offline and avoid requesting unnecessary permissions.
android.permissions =

[buildozer]
log_level = 2
warn_on_root = 1
