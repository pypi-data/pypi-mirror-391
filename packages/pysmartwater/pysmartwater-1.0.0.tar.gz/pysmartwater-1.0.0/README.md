[![license](https://img.shields.io/github/license/toreamun/amshan-homeassistant?style=for-the-badge)](LICENSE)
[![buy_me_a_coffee](https://img.shields.io/badge/If%20you%20like%20it-Buy%20me%20a%20coffee-yellow.svg?style=for-the-badge)](https://www.buymeacoffee.com/ankohanse)


# pysmartwater

Python library for retrieving sensor information from Smart Water branded devices.
This component connects to the remote Smart Water Technology servers and automatically determines which gateways, tanks and pumps are available there.

The custom component is compatible with SW900 devices (Desk Mount Wifi LCD, Wall Mount WiFi LCD, Tank Level Sender and Wireless Pump Controllers).
Legacy SW800 devices are not supported as these do not have WiFi/internet connectivity.

Disclaimer: this library is NOT created by [Smart Water Technologies](https://www.smart-water-online.com)


# Prerequisites
This library depends on the backend servers for the Smart Water app to retrieve the device information from. Before using this library, the Smart Water app must have been setup on your phone and linked to the desktop or wall-mount WiFi LCD.

When using the free app, usage is limited to 1 tank and 1 pump controller. For the paid app version multiple tanks and pumps are supported.


# Usage

The library is available from PyPi using:
`pip install pysmartwater`

See example_api_use.py for an example of usage.
