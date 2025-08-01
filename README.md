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

As of May 2025, there is no longer support for municipalities that just use RenoWeb, as they have all implemented MitID validation, for you to see your own Garbage Pickup Data. I am sure there a good reasons for that, but unfortunately that broke most of this integration.
As of release 2.6.0, this integration now supports the following API's:
- Municipalities that use **AffaldOnline**
- Municipalities that use **AffaldsPortal**
- Municipalities that use **Open Experience**
- Municipalities that use **Perfect Waste**
- Municipalities that use **Provas**
- Municipalities that use **Renodjurs**
- Municipalities that use **RenoSyd**
- Municipalities that use **Vest Forbrænding**
- Municipalities that have an **iCal** implementation. (Like København)
- The municipality of **Herning**
- The municipality of **Ikast-Brande**

That also means that a few Municipalities that were previously supported through **RenoWeb** and are not using any of the above API's, are no longer supported. There is no workaround for that at the moment.

### DESCRIPTION
Municipalities in Denmark, do not have one standard for how to expose the Pickup Calendars for their citizens, and different Municipalities have different solutions. This integration currently supports the Municipalities that uses the solution from Garbage Pickup API's listed above and that accounts for around 86% of all Municipalities.

Go to the [Municipality List](#MUNICIPALITIES) to see if your Municipality will work with this integration.

The biggest issue is, that there is NO standard for the way municipalities mix the content of containers. Some have glas & metal in one container, others have glas and paper in one container, etc and also, even though they do mix the same content in a container, they do not name it the same. In order to have some structure we need them grouped together and this is a bit of a challenge with all these different types. If a new pickup-type is found, the system will log a warning, which you can put in an issue and we will add it to the list. Please enable logging for the wrapper module in Home assistant to get this warning in Home Assistant, by adding this code to your `configuration.yaml`:

```yaml
logger:
  default: warning # Or whatever level you want
  logs:
    custom_components.affalddk: debug
    pyaffalddk: debug
```

#### This integration will set up the following platforms.

Platform | Description
-- | --
`sensor` | A Home Assistant `sensor` entity, with all available sensor from the API. State value will be the days until next pick-up
`calendar` | An entry will be made in to a local Home Assistant `calendar`. There will be a time based event every time there is a pick-up, describing what is collected. The default time is from 07:00 to 15:00. This value can be change in the Configuration section.

## CREDITS

@TermeHansen is now a new Co-Developer on this Integration, and has done a fantastic job to get support for Municipalities that use other API's than Renoweb and he has rewritten the underlying ``pyaffalddk`library, to make it easier to maintain going forward.

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
  | `House Number` | No | None | The house number of the address. Also accepts letters. If you have a house number like 2A or similar, and it does not work, try putting a space between the number and the letter, like 2 A. If more than 1 address is returned a second selection box will pop-up from where you can select the correct address. If the correct address is not found, don't put anything in the House Number field and all addresses for the road will be displayed. |

- Click on SUBMIT to save your data. If all goes well you should now have entities under the *Affaldshåndtering DK* integration

You can configure more than 1 instance of the Integration by using a different Address.

### MUNICIPALITY SPECIFIC Q&A

Based on user feedback, we are in this section collecting answers that often arise for a specific Municipality.

#### Odense

Odense has introduced reCAPTCHA, which is a technology to ensure that a real person and not a computer is retrieving data. So before the integration works you need to follow the instructions [found here](https://github.com/briis/affalddk/issues/257#issuecomment-2848522391)


## MUNICIPALITIES

Here is the list of currently supported Municipalities (85)

- Aabenraa (Affaldsportal)
- Aalborg (Affaldsportal)
- Aarhus (iCal)
- Albertslund (Vestforbrænding)
- Allerød (Affaldsportal)
- Assens (AffaldOnline)
- Ballerup (Vestforbrænding)
- Billund (Affaldsportal)
- Bornholm (Affaldsportal)
- Brøndby (Affaldsportal)
- Brønderslev (Affaldsportal)
- Dragør (Affaldsportal)
- Egedal (Affaldsportal)
- Esbjerg (Affaldsportal)
- Favrskov (AffaldOnline)
- Faxe (Perfect Waste)
- Fredensborg (Affaldsportal)
- Fredericia (Open Experience)
- Frederiksberg (Open Experience)
- Frederikssund (Perfect Waste)
- Furesø (Vestforbrænding)
- Gentofte (Affaldsportal)
- Gladsaxe (Perfect Waste)
- Glostrup (Affaldsportal)
- Greve (Perfect Waste)
- Gribskov (Perfect Waste)
- Guldborgsund (Perfect Waste)
- Haderslev (Provas)
- Halsnæs (Perfect Waste)
- Helsingør (Affaldsportal)
- Herlev (Affaldsportal)
- Herning (Herning API)
- Hillerød (Perfect Waste)
- Hjørring (Affaldsportal)
- Holbæk (AffaldOnline)
- Holstebro (Open Experience)
- Horsens (Perfect Waste)
- Hvidovre (Perfect Waste)
- Høje-Taastrup (Perfect Waste)
- Hørsholm (Affaldsportal)
- Ikast-Brande (Ikast-Brande)
- Ishøj (Vestforbrænding)
- Jammerbugt (Affaldsportal)
- Kalundborg (Perfect Waste)
- Kerteminde (Affaldsportal)
- København (iCal)
- Køge (Perfect Waste)
- Langeland (AffaldOnline)
- Lejre (Affaldsportal)
- Lemvig (Open Experience)
- Lolland (Perfect Waste)
- Lyngby-Taarbæk (Affaldsportal)
- Mariagerfjord (Affaldsportal)
- Morsø (AffaldOnline)
- Norddjurs (Renodjurs)
- Nordfyns (Open Experience)
- Næstved (Perfect Waste)
- Odder (RenoSyd)
- Odense (iCal) - [read this](#Odense) before adding the integration
- Odsherred (Perfect Waste)
- Randers (Affaldsportal)
- Rebild (AffaldOnline)
- Ringkøbing-Skjern (Perfect Waste)
- Roskilde (Perfect Waste)
- Rudersdal (Affaldsportal)
- Rødovre (Affaldsportal)
- Samsø (Affaldsportal)
- Skanderborg (RenoSyd)
- Skive (Open Experience)
- Slagelse (Perfect Waste)
- Solrød (Affaldsportal)
- Stevns (Perfect Waste)
- Struer (Open Experience)
- Svendborg (Affaldsportal)
- Syddjurs (Renodjurs)
- Sønderborg (Affaldsportal)
- Thy (Open Experience)
- Tårnby (Perfect Waste)
- Vallensbæk (Vestforbrænding)
- Varde (Affaldsportal)
- Vejen (Perfect Waste)
- Vejle (AffaldOnline)
- Viborg (Revas)
- Vordingborg (Affaldsportal)
- Ærø (AffaldOnline)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/briis/affalddk.svg?style=flat-square
[commits]: https://github.com/briis/affalddk/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=flat-square
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/briis/affalddk.svg?style=flat-square
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40briis,%20%40TermeHansen-blue.svg?style=flat-square
[releases-shield]: https://img.shields.io/github/release/briis/affalddk.svg?include_prereleases&style=flat-square&style=flat-square
[releases]: https://github.com/briis/affalddk/releases
