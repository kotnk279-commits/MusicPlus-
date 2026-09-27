
[app]
title = Music+
package.name = musicplus
package.domain = org.musicplus
source.dir = .
source.include_exts = py,jpg,gif,mp3,wav,ogg,m4a,aac
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 1
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.permissions = FOREGROUND_SERVICE
android.allow_backup = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
