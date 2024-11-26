# Affaldshåndtering DK

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

<a href="https://www.buymeacoffee.com/briis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>

<p align="center">
  <img width="384" height="128" src="https://github.com/briis/affalddk/blob/main/images/brand/logo@2x.png?raw=true">
</p>
The Affaldshåndtering DK integration adds support for retreiving Garbage Collection data from Municipalities around Denmark.

### INTRODUCTION

This integration replaces the [RenoWeb integration](https://github.com/briis/renoweb), which will no longer be maintained.

This is a complete rewrite of the RenowWeb V1.x Integration as the API this uses is slowly being phased out, and we needed to find a new way of collecting the data.

If I had updated Renoweb to V2.0 and you were a previous user of Renoweb, you would anyway have had to redo all your dashboards and automations, as Unique ID's of all sensors would have been new, thus having to change your Automations, Scripts and Dashboard entries.
With that in mind I decided to also use the opportunity to change the domain name of the Integration to `affalddk`

So why change the name and not just give it a new version number?

For a long time I wanted to have this Integration part of the Default HACS store, but in order to do that, you need to have Logo and icon images in the Home Assistant Brand Database. As Renoweb does not really have a logo by itself, I could not create one, as this could violate their rights to the name. But calling it something that is not related directly to Renoweb, gives me the possibility to invent my own logo and thus getting this added to the Default HACS store.

### DESCRIPTION
Municipalities in Denmark, do not have one standard for how to expose the Pickup Calendars for their citizens, and different Municipalities have different solutions. This integration currently supports the Municipalities that uses the solution from **Renoweb** and that accounts for more than 50% of all Municipalities. Go to the [Municipality List](#MUNICIPALITIES) to see if your Municipality will work with this integration.

The biggest issue is, that there is NO standard for the way municipalities mix the content of containers. Some have glas & metal in one container, others have glas and paper in one container, etc and also even though they do mix the same content in a container, they do not name it the same. In order to have some structure I need them grouped together and this is a bit of a challenge with all these different types. If a new pickup-type is found, the system will log a warning, which you can put in an issue and I will add it to the list. Please enable logging for the wrapper module in Home assistant to get this warning in Home Assistant, by adding this code to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.affalddk: debug
    pyaffalddk: debug
```

#### This integration will set up the following platforms.

Platform | Description
-- | --
`sensor` | A Home Assistant `sensor` entity, with all available sensor from the API. State value will be the days until next pick-up
`calendar` | An entry will be made in to a local Home Assistant `calendar`. There will be a full-day event every time there is a pick-up, describing what is collected.

## CREDITS

A big thank you to @thomaspalmdk for finding the new API, and to the people who helped Beta test it. Also thank you to @LordMike for making the embedded image functionality.

### UPGRADING FROM RENOWEB V1.x
As of V2.1.x of this Integration it can co-exist with the previous RenoWeb integration, as the dependecy API module has changed its name. So all you have to do is to install this integration, and then migrate your Dashboard, Automations and Scripts to use the new Entity names.

I still recommend that you de-install the previous integration, to not overload the servers. To deinstall *RenoWeb* do the following:
1. first remove Renoweb from the *Devices & Services* section.
2. Then go to HACS, and de-install Renoweb
3. Finally restart Home Assistant


## INSTALLATION

### HACS Installation

This Integration is not yet part of the default HACS store, (Work in progress, but that can take some time) but you can add it as a Custom repository in HACS by doing the following:

1. Go to HACS in your HA installation, and click on *Integrations*
2. Click the three vertical dots in the upper right corner, and select *Custom repositories*
3. Add `https://github.com/briis/affalddk` and select *Integration* as Category, and then click *Add*

You should now be able to find this Integration in HACS. After the installation of the files, you must restart Home Assistant, or else you will not be able to add Affald-DK from the *Devices & Services* Page.

If you are not familiar with HACS, or haven't installed it, I would recommend to [look through the HACS documentation](https://hacs.xyz/), before continuing. Even though you can install the Integration manually, I would recommend using HACS, as you would always be reminded when a new release is published.

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `affalddk`.
4. Download _all_ the files from the `custom_components/affalddk/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Affald*"

## CONFIGURATION

To add Affald-DK to your installation, do the following:

- Go to *Settings* and *Devices & Services*
- Click the **+ ADD INTEGRATION** button in the lower right corner.
- Search for *Affald** and click the integration.
- When loaded, there will be a configuration box, where you must select and enter:

  | Parameter | Required | Default Value | Description |
  | --------- | -------- | ------------- | ----------- |
  | `Municipality` | Yes | None | Select your Municipality from the Dropdown list. You can press the first letter of your municipality to quickly scroll down. |
  | `Zipcode` | Yes | None | Enter the Zipcode of the address. This is required as some municipalities use the same road name in several cities, so we need to make sure we pick the right street. |
  | `Road name` | Yes | None | Type the name of the road you want to get collection data for. Without house number. |
  | `House Number` | Yes | None | The house number of the address. Also accepts letters. If you have a house number like 2A or similar, and it does not work, try putting a space between the number and the letter, like 2 A |

- Click on SUBMIT to save your data. If all goes well you should now have entities under the *Affaldshåndtering DK* integration

You can configure more than 1 instance of the Integration by using a different Address.

### MORE INFORMATION

Around every New Year a bunch of Pickup Types will have no dates for the next pickup, as the calendar for the following year has not yet been created. That will result in some Sensors with `Undefined` or `Unavailable` in their value, and they will be unavailable, until they have a date again. As of version 2.1.20, they will now get an artificial date which is always December 31. the following year. As soon as a valid date is found for these sensors, this date will be used instead.


## MUNICIPALITIES

Here is the list of currently supported Municipalities

    - Aabenraa
    - Aalborg
    - Aarhus (Version 2.2.0-beta2)
    - Albertslund
    - Allerød
    - Billund
    - Bornholm
    - Brøndby
    - Brønderslev
    - Dragør
    - Egedal
    - Esbjerg
    - Faxe
    - Fredensborg
    - Frederiksberg
    - Frederikssund
    - Gentofte
    - Gladsaxe
    - Glostrup
    - Greve
    - Gribskov
    - Halsnæs
    - Hedensted
    - Helsingør
    - Herlev
    - Hillerød
    - Hjørring
    - Horsens
    - Hvidovre
    - Høje-Taastrup
    - Hørsholm
    - Jammerbugt
    - Kerteminde
    - Køge
    - Lejre
    - Lyngby-Taarbæk
    - Mariagerfjord
    - Næstved
    - Odense (Version 2.2.0-beta1)
    - Odsherred
    - Randers
    - Ringkøbing-Skjern
    - Ringsted
    - Roskilde
    - Rudersdal
    - Rødovre
    - Samsø
    - Slagelse
    - Solrød
    - Sorø
    - Stevns
    - Svendborg
    - Sønderborg
    - Tårnby
    - Varde
    - Vejen
    - Vordingborg

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/briis/affalddk.svg?style=flat-square
[commits]: https://github.com/briis/affalddk/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=flat-square
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/briis/affalddk.svg?style=flat-square
[maintenance-shield]: https://img.shields.io/badge/maintainer-Bjarne%20Riis%20%40briis-blue.svg?style=flat-square
[releases-shield]: https://img.shields.io/github/release/briis/affalddk.svg?include_prereleases&style=flat-square&style=flat-square
[releases]: https://github.com/briis/affalddk/releases
