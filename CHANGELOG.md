# Changelog for Affaldshåndtering DK Home Assistant Integration

## Version 2.7.1

**Date**: `PRE-RELEASE ONLY`

### Added
* Added new API for Herning: ([#330](https://github.com/briis/affalddk/issues/330))

**Note**: We know that when we add new Municipalities, some of them will miss some fractions (Garbage or Material Types). Please make sure you create an issue, where you attach the Log entries from Home Assistant. This will make sure we can fix these issue before the final release.

### Changes

* Fixed missing or failing Fractions in:
  * Hjørring ([#329](https://github.com/briis/affalddk/issues/329))

* Bump `pyaffalddk` to 2.12.1

---------------------------

<details>
  <summary><b>PREVIOUS CHANGES</b></summary>

**Date**: `2025-06-13`

### Added
* Added new API for Provas: ([#216](https://github.com/briis/affalddk/issues/216))
  * Haderslev
* Added new API for Renodjurs: ([#246](https://github.com/briis/affalddk/issues/246))
  * Norddjurs
  * Syddjurs
* Added Assens to AffaldOnline ([#229](https://github.com/briis/affalddk/issues/229))
* Added new municipalities to *Open Experience*
  * Lemvig
  * Skive
  * Struer
* Added new API for RenoSyd, supporting new Municipalities:
  * Odder
  * Skanderborg

**Note**: We know that when we add new Municipalities, some of them will miss some fractions (Garbage or Material Types). Please make sure you create an issue, where you attach the Log entries from Home Assistant. This will make sure we can fix these issue before the final release.

### Changes

* With version 2.7.0 the Next Pickup should change after the End time of the Pickup had passed. Unfortunately the Update Interval was not changed during that release. As of 2.7.0 update interval is now every hour and cannot be changed. This means every hour we check if end time has passed and if yes the Next Pickup will change to one after today. Data from the Garbage API is only loaded once a day, so we do not spam the providers.
* fix bug in set_next_pickup when only one fraction type
* With version 2.7.0 searching for an address, will use only `roadname` and `zipcode` -  and `house_number` will be used as `house_number` + wildcard to return a list of results for a new seconds selction step (if more than one result). Fixing [#323](https://github.com/briis/affalddk/issues/323)

* Fixed missing or failing Fractions in:
  * Dragør ([#321](https://github.com/briis/affalddk/issues/321))
  * Aalborg ([#51](https://github.com/briis/pyaffalddk/issues/51))
  * Horsens ([#326](https://github.com/briis/affalddk/issues/326))
  * Jammerbugt ([#328](https://github.com/briis/affalddk/issues/328))

* Rewrite of `get_next_event` logic, to ensure getting true next event and not next pickup type

* Bump `pyaffalddk` to 2.12.0


## Version 2.6.0

**Date**: `2025-06-01`

### Added
* Added new API for Open Experience:
  * Fredericia
  * Frederiksberg
  * Holstebro
  * Nordfyns
  * Thy

**Note**: We know that when we add new Municipalities, some of them will miss some fractions (Garbage or Material Types). Please make sure you create an issue, where you attach the Log entries from Home Assistant. This will make sure we can fix these issue before the final release.

### Changes

* Always return basic attributes also when no event from API, to fix [#312](https://github.com/briis/affalddk/issues/312)
* Next_event will now move to next comming event after the end time [#93](https://github.com/briis/affalddk/issues/93)
* We will only fetch online data once a day no matter how often the sensor is updating.
* @TermeHansen made more optimizations on the API Module, hopefully it more robust to handle changes in the Fraction naming.
* Changed to use links for fraction images instead of base64 data strings, to fix [#230](https://github.com/briis/affalddk/issues/230)
* Bump `pyaffalddk` to V2.10.3
* Fixed missing Fractions in:
  * Holstebro ([#214](https://github.com/briis/affalddk/issues/214))
  * Viborg ([#297](https://github.com/briis/affalddk/issues/297))
  * Favrskov ([#302](https://github.com/briis/affalddk/issues/302))
  * Albertslund ([#304](https://github.com/briis/affalddk/issues/304))
  * Greve ([#305](https://github.com/briis/affalddk/issues/305))
  * Holbæk ([#306](https://github.com/briis/affalddk/issues/306))
  * Fredensborg ([#308](https://github.com/briis/affalddk/issues/308))
  * Billund ([#309](https://github.com/briis/affalddk/issues/309))
  * Ringøbing-Skjern ([#314](https://github.com/briis/affalddk/issues/314))
  * fix Allerød, rest/mad mangler ([#315](https://github.com/briis/affalddk/issues/315))

---------------------------

## Version 2.5.0

**Date**: `2025-05-23`

### Added
* Added new API for Vest Forbrænding, fixing Ballerup and adding new municipalities:
  * Furesø
  * Ishøj
  * Vallensbæk
* Added new API for AffaldOnline with new municipalities:
  * Favrskov
  * Holbæk
  * Langeland
  * Morsø
  * Rebild
  * Vejle
  * Ærø
* Added new API for Revas with new municipalities:
  * Viborg ([#297](https://github.com/briis/affalddk/issues/297))


**Note**: We know that when we add new Municipalities, some of them will miss some fractions (Garbage or Material Types). Please make sure you create an issue, where you attach the Log entries from Home Assistant. This will make sure we can fix these issue before the final release.

### Changes

* @TermeHansen made even more optimizations on the API Module, making it more robust to handle changes in the Fraction naming, and unifying Pickup Event Functions.
* Fixed missing Fractions in:
  * Esbjerg ([#298](https://github.com/briis/affalddk/issues/298))
  * Solrød ([#300](https://github.com/briis/affalddk/issues/300))
* Bump `pyaffalddk` to V2.9.0

### [Dependabot](https://github.com/apps/dependabot) updates


## Version 2.4.3

**Date**: `2025-05-18`

## What's Changed

* **Calendar Items are now no longer full day events**, but have a timespan for the day. Default is from 7:00 to 15:00, but both these can be changed in the configuration settings. First part of fixing [#93](https://github.com/briis/affalddk/issues/93)
  * Function still missing to move to *Next Pickup* when time of day has passed. This is a bit more complicated, as we only update data a few times a day.
  * You might see that existing calendar entries are not changed right away, but all future entries will be time based and not date based.
* Fixing several missing fractions:
  * Rudersdal - Material type [Farligt affald, distrikt A] is not defined in the system for Genbrug #289
  * Herlev - Herlev Kommune - #290
  * Bornholms Kommune #291
  * Helsingør Kommune - Mangler 5 entiteter #292
  * Sønderborg mangler en entitet #293
  * [Storskrald Distrikt 3] is not defined #294
* Big re-structure and cleanup of internal material string to defined fractions code
* Bump `pyaffalddk` to V2.6.0

## Version 2.4.2

**Date**: `2025-05-12`

## What's Changed

* Fixing issue with new installations not displaying any data. Closing [AffaldDK #281](https://github.com/briis/affalddk/issues/281)

  **For those people who made a new setup of an address, after 2.4.0, you have to remove that address, and set it up again, and then it should work**
* Fixing missing Fractions in Høe-Taastrup, Esbjerg, Gentofte and Hjørring. Cloising issues:
  * [#280](https://github.com/briis/affalddk/issues/280)
  * [#277](https://github.com/briis/affalddk/issues/277)
  * [#275](https://github.com/briis/affalddk/issues/275)
  * [#265](https://github.com/briis/affalddk/issues/265)
* Unfortunately we also had to remove the following Municipalities from the supported list, as they are still stuck behind the MitID wall, and we have found no alternative way to support those:
  * Frederiksberg
  * Hedensted
  * Ringsted
* Bump `pyaffalddk` to V2.5.1

## Version 2.4.1

**Date**: `2025-05-11`

## What's Changed
* Fixing issue with configure of new entities Closing [AffaldDK #276](https://github.com/briis/affalddk/issues/276)

## Version 2.4.0

**Date**: `2025-05-11`

We have now decided to release this as the new official release 2.4.0, which implements a whole new backend module that has gone through a tremendous rework, mostly thanks to @TermeHansen.
We do realize there will still be some naming of fractions or missing fractions that you will find, but please report this by opening an issue, and **remember to attach the log output from HA**.

Many Municipalities started to use MitID, for validation before you could retrieve data for your Garbage Collection. This meant in reality that this Component stopped working when that happened.
@TermeHansen with the support from @ttopholm have now made a new interface, that uses the **Perfect Waste** API to retrieve the data.
@TermeHansen has also implemented the first version that supports **Affaldsportalen**. So if you can see your Garbage Collection schedule using that App or Website, you should also be able to use this Integration.
This should solve the issue for all the Municipalities that use them. But not all do. We have gone through the list, and to our best knowledge, all previously supported Municpalities should still work, and on top of that there is now also support for 4 new Municpalities:
- Ballerup
- Guldborgsund
- Kalundborg
- Lolland

## What's Changed
* Timezone bug in ics data from Kbh by @TermeHansen in #26
* new interface for Perfect Waste by @TermeHansen in #28
* Adding interface for the affaldsportalen / renoweb.servicegh
* Changed address_id to the new naming uid, to avoid unique_id issues. Fixing partly [#273](https://github.com/briis/affalddk/issues/273)
* Adopted code to match changes in `pyaffalddk` 2.5.0
* Added and/or changed Fractions for the following Municipalities_
  * Mariagerfjord ([#261](https://github.com/briis/affalddk/issues/261))
  * Aalborg ([#261](https://github.com/briis/affalddk/issues/261))
  * Egedal ([#261](https://github.com/briis/affalddk/issues/261))
  * Svendborg ([#261](https://github.com/briis/affalddk/issues/261))
  * Glostrup ([#261](https://github.com/briis/affalddk/issues/261))
  * Lyngby-Taarbaek ([#261](https://github.com/briis/affalddk/issues/261))
  * Esbjerg ([#267](https://github.com/briis/affalddk/issues/267))
  * Randers ([#268](https://github.com/briis/affalddk/issues/268))
  * Sønderborg ([#269](https://github.com/briis/affalddk/issues/269))
  * Kerteminde ([#270](https://github.com/briis/affalddk/issues/270))
  * Næstved ([#271](https://github.com/briis/affalddk/issues/271))
  * Jammerbugt ([#273](https://github.com/briis/affalddk/issues/273))
  * Rudersdal
  * Rødovre
* Bump `pyaffalddk` to V2.5.0

## Version 2.3.1

**Date**: `2025-05-01`

## What's Changed

* Fixing wrong pickup date for KK, due to conversion to UTC. Thank you to @TermeHansen for implementing this
* Bump `pyaffalddk` to V2.2.1

## [Dependabot](https://github.com/apps/dependabot) updates

## Version 2.3.0

**Date**: `2025-04-24`

## What's Changed

* Support for **Københavns Kommune** added. Thank you to @TermeHansen for implementing this
* Rewritten `Config Flow`, to remove deprecation warning.
* Bump `pyaffalddk` to V2.2.0

## Version 2.2.3

**Date**: `2025-03-19`

## What's Changed

* Fixing Missing Material in Egedal Kommune. Closing [AffaldDK #221](https://github.com/briis/affalddk/issues/221)
* Fixing Missing Material in Gladsaxe Kommune. Closing [AffaldDK #238](https://github.com/briis/affalddk/issues/238)
* Fixing Missing Material in Gribskov Kommune. Closing [AffaldDK #242](https://github.com/briis/affalddk/issues/242)
* Fixed Blocking Call. Closing [AffaldDK #213](https://github.com/briis/affalddk/issues/213)
* Added function to find a date based on Weekday and Odd or Even week. Closing [AffaldDK #226](https://github.com/briis/affalddk/issues/226)
* **IMPORTANT** Removed Sorø Kommune as they no longer have en open API.
* Bump `pyaffalddk` to V2.1.7

## Version 2.2.2

**Date**: `2025-01-07`

## What's Changed

* Changed the Last Update field as this causes blocking IO issues with Home Assistant. Now this value is calculated based on homeassistant dt functions.
* Fixing missing DAYLIGHT information in iCal data. Closing [AffaldDK #205](https://github.com/briis/affalddk/issues/205)
* Fixing missing containers in Køge after renaming. Closing [AffaldDK #207](https://github.com/briis/affalddk/issues/207)
* Bump development environment to Python 3.1.3 and Home Assistant 2025.1
* Bump `pyaffalddk` to V2.1.6

## Version 2.2.1

**Date**: `2024-12-09`

## What's Changed

* Fixing renamed containers in Egedal kommune. Closing [AffaldDK #194](https://github.com/briis/affalddk/issues/194)
* Bump `pyaffalddk` to V2.1.2

## Version 2.2.0

**Date**: `2024-11-26`

## What's Changed

* Added Odense Kommune to list of supported municipalities.
* Added Aarhus Kommune to list of supported municipalities.
* Added base support for municipalities that can deliver data via an iCalendar file.
* Added new Material Type `Genbrugsspand, 240L (2-delt) (1 stk.)`. Closing [AffaldDK #186](https://github.com/briis/affalddk/issues/186)
* Bump `pyaffalddk` to V2.1.1

## Version 2.1.20

**Date**: `2024-11-19`

## What's Changed

* **IMPORTANT** Around every New Year a bunch of Pickup Types will have no dates for the next pickup, as the calendar for the following year has not yet been created. That will result in some Sensors with `Undefined` or `Unavailable` in their value, and they will be unavailable, until they have a date again. As of version 2.1.20, they will now get an artificial date which is always December 31. the following year. As soon as a valid date is found for these sensors, this date will be used instead.
* Fixing issue where there is a weekday present but next pick-up is undefined. Typically occurs around New Years time. Closing [AffaldDK #179](https://github.com/briis/affalddk/issues/179)
* Added Municipality and Address ID to 'Service Info', to be used when asking for support.
* Bump `pyaffalddk` to V2.0.44

## Version 2.1.19

**Date**: `2024-10-11`

## What's Changed

* Corrected wrong image for Pap, Pair, Glas & Metal. Closing [AffaldDK #159](https://github.com/briis/affalddk/issues/159)
* Added new Material Type `juletrae` and also added new image. Closing [AffaldDK #165](https://github.com/briis/affalddk/issues/165)
* Bump `pyaffalddk` to V2.0.41

## Version 2.1.18

**Date**: `2024-10-04`

## What's Changed

* Start Fixing issues, after Bornholm has changed naming of many un its. Contributing to [AffaldDK #159](https://github.com/briis/affalddk/issues/159)
* Bump `pyaffalddk` to V2.0.40

## Version 2.1.17

**Date**: `2024-09-26`

## What's Changed

* Fixing missing Types in Svendborg. Closing [AffaldDK #151](https://github.com/briis/affalddk/issues/151)
* Fixing missing Types in Horsens. Closing [pyaffalddk #14](https://github.com/briis/pyaffalddk/issues/14)
* Bump `pyaffalddk` to V2.0.39

## Version 2.1.16

**Date**: `2024-08-20`

## What's Changed

* Fixing missing Types in Solrød. Closing [AffaldDK #139](https://github.com/briis/affalddk/issues/139)
* Fixing missing Types in Egedal. Closing [AffaldDK #142](https://github.com/briis/affalddk/issues/142)
* Bump `pyaffalddk` to V2.0.38

## Version 2.1.15

**Date**: `2024-08-13`

This is a **minor update**, and if you don't live in Vordingborg Kommune, there is no need to install this.

## What's Changed

* Fixing missing Types in Vordingborg. Closing [AffaldDK #136](https://github.com/briis/affalddk/issues/136)
* Bump `pyaffalddk` to V2.0.37

## Version 2.1.14

**Date**: `2024-08-06`

## What's Changed

* Fixing missing Types in Ringsted. Closing [AffaldDK #133](https://github.com/briis/affalddk/issues/133)
* Bump `pyaffalddk` to V2.0.36

## Version 2.1.13

**Date**: `2024-07-29`

## What's Changed

* Fixing missing Types in Albertslund. Closing [AffaldDK #129](https://github.com/briis/affalddk/issues/129)
* Bump `pyaffalddk` to V2.0.35

## Version 2.1.12

**Date**: `2024-07-06`

## What's Changed

* Fixing missing containers in Esbjerg. Closing [AffaldDK #117](https://github.com/briis/affalddk/issues/117)
* Fixing missing containers in Gribskov. Closing [AffaldDK #118](https://github.com/briis/affalddk/issues/118)
* Bump dependency `pyaffalddk` to version 2.0.34

## Version 2.1.11

**Date**: `2024-06-30`

## What's Changed

* Adding Bornholm as new Municipality. I have limited test data to go on, but some data is being returned. If anything is missing, please report back. Closing [#114](https://github.com/briis/affalddk/issues/114)
* Bump dependency `pyaffalddk` to version 2.0.33

  ## Version 2.1.10

  **Date**: `2024-06-15`

  ## What's Changed

* Fixing missing details for Faxe. Closing [`pyaffalddk` #4](https://github.com/briis/pyaffalddk/issues/4)
* Fixing missing details for Lyngby-Taarbæk. Closing [#105](https://github.com/briis/affalddk/issues/105)
* Bump dependency `pyaffalddk` to version 2.0.31


  ## Version 2.1.9

  **Date**: `2024-05-28`

  ## What's Changed

* Fixing missing details for Slagelse and Randers. Closing [#97](https://github.com/briis/affalddk/issues/97)
* Bump dependency `pyaffalddk` to version 2.0.30

## [Dependabot](https://github.com/apps/dependabot) updates

  ## Version 2.1.8

  **Date**: `2024-05-12`

  ## What's Changed

* Fixing missing details for Vejen and Randers. Closing [#87](https://github.com/briis/affalddk/issues/87) and [pyaffalddk #3](https://github.com/briis/pyaffalddk/issues/3)
* Bump dependency `pyaffalddk` to version 2.0.29

  ## Version 2.1.7

  **Date**: `2024-05-04`

  ## What's Changed

- Added new Categories `Madaffald` and `Restaffald`
- Added new category images for `restaffald` and `madaffald`
- Fixed missing containers for Glostrup Kommune. Closing [#79](https://github.com/briis/affalddk/issues/79)
- Fixed missing containers for Egedal Kommune. Closing [#84](https://github.com/briis/affalddk/issues/84)
- Fixed missing containers for Lyngby-Taarbæk Kommune. Closing [#83](https://github.com/briis/affalddk/issues/83)
- Fixed missing Tekstil container for Solrød Kommune.
- Bump dependency `pyaffalddk` to version 2.0.28

  ## Version 2.1.6

  **Date**: `2024-04-22`

  ## What's Changed

- Modified change from `pyaffalddk` 2.0.25, as it caused problems for many with the category Storskrald. It will now work for all, including Gladsaxe. Closing [#76](https://github.com/briis/affalddk/issues/76)
- Added more details to warning if category not found. Makes it easier to debug when errors are reported.
- Bump dependency `pyaffalddk` to version 2.0.26

  ## Version 2.1.5

  **Date**: `2024-04-19`

  ## What's Changed

- Added new category Plast, MDK, Glas & Metal.
- Added missing containers for Varde kommune. Closing #75
- Support for Gladsaxe kommunes storskrald definition by @DeKi90
- Bump dependency `pyaffalddk` to version 2.0.24

  ## Version 2.1.4

  **Date**: `2024-04-16`

  This is a minor release, with a Hotfix for Faxe Kommune

  ## What's Changed

- Added `|` as separator to Next Pickup sensor, to easier identify items.
- Added missing containers for Papir & Plast and Metal & Glas for Faxe kommune. Closing #71
- Bump dependency `pyaffalddk` to version 2.0.23

  ## Version 2.1.3

  **Date**: `2024-04-07`

  ## What's Changed

- Added missing container for Svendborg kommune. Closing [#68](https://github.com/briis/affalddk/issues/68)
- Added missing container for Mariagerfjord kommune. Closing [#67](https://github.com/briis/affalddk/issues/67)
- Imporoved error handling on sensor entities.
- Bump dependency `pyaffalddk` to version 2.0.22

  ## Version 2.1.2

  **Date**: `2024-04-05`

  ## What's Changed

- Re-added `Miljøboks` for Gentofte kommune as it was placed in the wrong location for 2.1.1. Closing [#64](https://github.com/briis/affalddk/issues/64)
- Bump dependency `pyaffalddk` to version 2.0.21

  ## Version 2.1.1

  **Date**: `2024-04-03`

  ## What's Changed

- Found the real error for the sensors not being updated when containers have been collected. All data is now updated correctly according to the update interval set. Closing [#61](https://github.com/briis/affalddk/issues/61)
- Added `Miljøboks` for Gentofte kommune. Closing [#64](https://github.com/briis/affalddk/issues/64)
- Bump dependency `pyaffalddk` to version 2.0.20

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

