# Changelog for Affaldshåndtering DK Home Assistant Integration

  ## Version 2.1.1

  **Date**: `2024-04-03`

  ## What's Changed

- Found the real error for the sensors not being updated when containers have been collected. So you would see the -1 days for Next Pickup container. Closing [#61](https://github.com/briis/affalddk/issues/61)
- Added `Miljøboks` for Gentofte kommune. Closing [#64](https://github.com/briis/affalddk/issues/64)
- Bump dependency `pyaffalddk` to version 2.0.20

---------------------------

<details>
  <summary><b>PREVIOUS CHANGES</b></summary>

  ## Version 2.1.0

  **Date**: `2024-03-30`

  ## What's Changed

- The biggest change in this version is that you no longer need to download the images for the `entity_picture`. Thanks to @LordMike these images are now embedded as base64 data images. @LordMike did a lot of work to ensure the images are small enough to be able stay under the character limit, and he also made a great little script I can use if and when future changes to images are needed. Thanks again @LordMike. With this implemented, you do not need the images in `/config/www/affalddk` and this directory can be deleted.
- Updates are sometimes not executed according to time interval. This release should now fix this. Closing [#61](https://github.com/briis/affalddk/issues/61)
- Adjusted the update Interval, so that you can now set it to between 1 and 24 hours.
- Migrated dependency `pyrenoweb` to `pyaffalddk` as the plan is to support more than RenoWeb in the future, and then the name should embrace that.

  ## Version 2.0.7

  **Date**: `2024-03-26`

  ## What's Changed

**NOTE**: A new category 'plast' has been added, so you will have to redownload the images files.

- Removed Furesø kommune as they are no longer using Renoweb. Closing [#51](https://github.com/briis/affalddk/issues/51)
- Added Lejre kommune, that was left out in the initial release. Closing [#52](https://github.com/briis/affalddk/issues/52)
- Fixing wrong date count on sensors. Closing [#54](https://github.com/briis/affalddk/issues/54)
- Fixed categories for Solrød kommune. Closing [#53](https://github.com/briis/affalddk/issues/53)
- Fixing the `calendar.get_events` service call so that it now supports a start and end date. Thank you to @chamook for the initial Pull Request.
- Partly fix of #59. Catagorize container `Pap og papir/metal, glas og hård plast` correctly for Sorø Kommune
- Bumped minimum required HA version to 2024.2.0, to ensure that HA is using Python 3.12. Previous versions of Python might not work.
- Bump dependency `pyrenoweb` to 2.0.17

  ## Version 2.0.6

  **Date**: `2024-03-23`

  ## What's Changed

- Compressed newly added SVG images, so they are faster to load.
- Placing Textil correctly for Roskilde and Aalborg (and possible other Municipalities). Cloisng #49
- Adding new category `papirglasmetalplast`. **Note** You need to download the image files again.
- Fixing missing containers for Lyngby-Taarbæk. Closing #50
- Fixing occasionally wrong address id being returned.
- Bump dependency `pyrenoweb` to 2.0.15


  ## Version 2.0.5

  **Date**: `2024-03-22`

  ## What's Changed

- Fixing missing containers for Lyngby-Taarbæk. Closing issue [#40](https://github.com/briis/affalddk/issues/40)
- Fixing missing containers for Aalborg. Closing issue [#35](https://github.com/briis/affalddk/issues/35)
- Fixing missing containers for Rødovre
- Fixing missing containers for Solrød. Closing issue [#32](https://github.com/briis/affalddk/issues/32)
- Removed Rebild Kommune from the supported Municipalities list, as they have switched to another provider. Working on adding support for that provider, that also seems to service other Municipalities in Nordjylland.
- Added support for Billund Kommune. They were accidentially left out.
- Added new Categories `batterier`, `papirglasdaaser` and `elektronik`. **NOTE:** This also means you will have to redownload the images and update the directory with new files.
- Converted Calendar Events from time based events to full day events. Giving better support for some Lovelace cards. Closing [#34](https://github.com/briis/affalddk/issues/34)
- The sensor `Næste Afhentning`, now has a list of all entities that are picked up on that date. Use the attribute `name` to get the categories, and the attribute `description` to get a more detailed list of content. The icon and entity_picture will now always be the recycle symbol. Closing issue [#41](https://github.com/briis/affalddk/issues/41) and [#42](https://github.com/briis/affalddk/issues/42)
- Bump dependency `pyrenoweb` to 2.0.14

  ## Version 2.0.4

  **Date**: `2024-03-12`

  ## What's Changed

- Adding new Attribute `date_short`. Closing [#22](https://github.com/briis/affalddk/issues/22)
- Fixing missing update of Calendard state. Closing [#27](https://github.com/briis/affalddk/issues/27)
- Fixing missing Containers for Kerteminde. Closing [#19](https://github.com/briis/affalddk/issues/19)
- Bump dependency `pyrenoweb` to 2.0.11

  ## Version 2.0.3

  **Date**: `2024-03-10`

  This is a Hotfix release, only adding missing containers for some municipalities.

  I am sorry for these frequent releases, but this will most likely go on for a little while, until we mapped all the containers to the right Category. If you are missing a container, please add this to your configuration file:
```yaml
logger:
  default: warning
  logs:
    custom_components.affalddk: error
    pyrenoweb: error
```
And create an issue with the data from the logfile, and the Municipality that has the issue.

  ## What's Changed

- Fixing the Genbrug category for Hvidovre kommune
- Fixing the Genbrug category for Greve kommune
- Fixing the Genbrug category for Egedal kommune
- Bump dependency `pyrenoweb` to 2.0.10


  ## Version 2.0.2

  **Date**: `2024-03-09`

  ## What's Changed

  This is a Hotfix release, only adding missing containers for some municipalities

- Add missing containers for Rudersdal and Høje Taastrup. Closing [#15](https://github.com/briis/affalddk/issues/15) and [#16](https://github.com/briis/affalddk/issues/16)
- Optimied a few SVG files.
- Bump dependency `pyrenoweb` to 2.0.9


  ## Version 2.0.1

  **Date**: `2024-03-07`

  ## What's Changed

- Fixing wrong Issue Link address. Closing [#10](https://github.com/briis/affalddk/issues/10)
- Bump pyrenoweb to 2.0.5 Closing wrong types of garbage types in Egedal and Allerød [#6](https://github.com/briis/affalddk/issues/6)
- Handling the case where the same Road exists more than once in a Municipality. There is now a requirement to enter the Zipcode of the Address when setting up a new entity in Home Assistant. Closing Issue [#5](https://github.com/briis/affalddk/issues/5)
- Fixing missing containers in Aalborg. Closing [#11](https://github.com/briis/affalddk/issues/11)
- Added Rudersdal back to the list as they do work with this Integration. Closing [#8](https://github.com/briis/affalddk/issues/8)
- Bump dependency `pyrenoweb` to 2.0.6


  ## Version 2.0.0

  **Date**: `2024-03-04`

  ## What's Changed
  * Even though it says V2.0.0, this is the first release of this Integration. Please see the [README.md](https://github.com/briis/affalddk/blob/main/README.md) for a descriptin and installation instructions.
</details>

---------------------------
<details>
  <summary><b>VERSION 2.0.0-Beta-3</b></summary>

  ## Version 2.0.0-Beta-3

  **Date**: `2024-03-04`

  ## What's Changed
  * Bump ruff from 0.2.2 to 0.3.0 by @dependabot in https://github.com/briis/affalddk/pull/1
  * Version 2 beta3 by @briis in https://github.com/briis/affalddk/pull/2

  ## New Contributors
  * @dependabot made their first contribution in https://github.com/briis/affalddk/pull/1
  * @briis made their first contribution in https://github.com/briis/affalddk/pull/2

  **Full Changelog**: https://github.com/briis/affalddk/compare/2.0.0-beta2...v2.0.0-beta3

</details>

---------------------------
<details>
  <summary><b>VERSION 2.0.0-Beta-2</b></summary>

  ## Version 2.0.0-Beta-2

  **Date**: `2024-03-03`

  ### Changes

  Please see the [README.md](https://github.com/briis/affalddk/blob/main/README.md) before installation.

  This integration replaces the [RenoWeb integration](https://github.com/briis/renoweb), which will no longer be maintained.

  This is a complete rewrite of the RenowWeb V1.x Integration as the API this uses is slowly being phased out, and we needed to find a new way of collecting the data.

  If you were a previous user of Renoweb, you would have had to de-install the Integration before upgrading, as Unique ID's of all sensors would have been new, thus having to change your Automations, Scripts and Dashboard entries.
  With that in mind I decided to also use the opportunity to change the domain name of the Integration to `affalddk` So why change the name and not just give it a new version number?

  For a long time I wanted to have this Integration part of the Default HACS store, but in order to do that, you need to have Logo and icon images in the Home Assistant Brand Database. As Renoweb does not really have a logo by itself, I could not create one, as this could violate their rights to the name. But calling it something that is not related directly to Renoweb, gives me the possibility to invent my own logo and thus getting this added to the Default HACS store.

  If you were a previous user of Renoweb the Major changes to this integration are:

  - I now use a new API. The V1 API was based on a Renoweb API that is being phased ot, and over the last few months I have seen more and more municipalities disappearing from the supported municipalities. The new API is the same most Municipalities use, when you go to their official web page and search for your address and then get Pickup Schedules.
  - The `Sensors` are new, and not named the same way as the V1 sensors. Thus there is no upgrade path. With each sensor I now also iclude the official Pictograms as Entity Pictures, which you can use in your dashboard. **Note**: This image files must be installed manually - please see the README file).
  - There is a new local `Calendar` entity created, which has a full-day event every time there is a Pick-up. The event will contain a Description and what content is being picked up.
  - The `Binary Sensors` have not been created. If anyone uses these, raise an issue on Github.

  I have now been through all Municipalities and checked if they work with this Integration. There are 47 Munipalities that will work , and if you don't see your municipality in the Dropdown List, then it will not work.

</details>

