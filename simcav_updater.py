#!/usr/bin/env python3

print('working')
import time, os, requests, misc


time.sleep(1)

# Web urls
simcav_api = misc.get_api()
simcav_url = misc.get_repo()

simcav_home = misc.gethomepath(misc.guestOS())

download_error = misc.download_file('Disclaimer.txt', simcav_home)