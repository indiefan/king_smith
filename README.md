# King Smith Walking Pad

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![Community Forum][forum-shield]][forum]

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]


Custom integration to connect Home Assistant with [King Smith Walking Pads][king_smith].

Currently this integration adds a switch for main belt and a number entity to control/monitor the belt speed (in mph).

This integration discovers/connects to the device using bluetooth (you may need to configure a bluetooth proxy like an ESP32).

It has been tested with a C2 (the model I personally own), but is likely to work with other models supported by the underlying library.

In order for the device to be connected to HA, it must not be connected to another device (e.g. the mobile app). If it is already configured via the mobile app, you will have to disconnect it before using it in HA.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `king_smith`.
1. Download _all_ the files from the `custom_components/king_smith/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. Click on `Settings` and then `Devices & services`
1. If the treadmill is on and not currently connected to another device, it should show up in the `Discovered` list. Click `configure` and give it a name.

## Configuration is done in the UI

## Verified Supported Models

* C2
* A1 Pro

(if you have a King Smith treadmill and would like to verify support, please reach out)

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[king_smith]: https://github.com/gwyntel/king_smith
[buymecoffee]: https://www.buymeacoffee.com/indiefan
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/gwyntel/king_smith.svg?style=for-the-badge
[commits]: https://github.com/gwyntel/king_smith/commits/main
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/gwyntel/king_smith.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/gwyntel/king_smith.svg?style=for-the-badge
[releases]: https://github.com/gwyntel/king_smith/releases
