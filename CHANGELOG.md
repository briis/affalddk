# Changelog for Renoweb Home Assistant Integration


  ## Version 2.0.0-Beta-2

  **Date**: `2024-03-03`

  ### Changes

  **Please see the release notes for Beta1 before installing**

I have now been through all Municipalities and checked if they work with this Integration. There are 47 Munipalities that will work , and if you don't see your municipality in the Dropdown List, then it will not work.

As there are new sensors added you will also have to redownload the `renoweb_images.zip` file from this release, and copy the content to your `www/renoweb` folder again.

* Added new function to support Municipalities that only supply weekdays. (Albertslund, Furesø).
* Added new garbage type `plastmadkarton` which holds *Plast & Mad-Drikkekartoner*
* Added new garbage type `plastmetalmadmdk` which holds *Plast, Metal, Mad & Drikkekartoner*
* Added new garbage type `pappapir` which holds *Pap & Papir*
* Added new garbage type `tekstil` which holds *Tekstilaffald*
* Added new garbage type `glasplast` which holds *Glas, Plast & Madkartoner*
* Added new garbage type `plastmetalpapir` which holds *Plast, Metal & Papir*
* Fixed bug when Type String could be in more than pickup type. Happens when partial strings are the same.
* Removed the following Municipalities as they are not supported:
  * Balleup
  * Billund
  * Fanø
  * Favrskov
  * Fredericia
  * Frederikshavn
  * Guldborgsund
  * Haderslev
  * Herning
  * Holbæk
  * Holstebro
  * Ikast-Brande
  * Ishøj - They use the API, but do not supply dates, only textual descriptions, which cannot be converted to dates.
  * Kalundborg
  * Kolding
  * Læsø
  * Lolland
  * Middelfart
  * Morsø
  * Norddjurs
  * Nordfyns
  * Nyborg
  * Odder
  * Odense
  * Silkeborg
  * Skanderborg
  * Skive
  * Struer
  * Syddjurs
  * Thisted
  * Vejle
  * Vesthimmerland
  * Viborg
  * Tønder - They use the API in a Non-Standard way. Still under investigation if I can retrieve the data
  * Vallensbæk


  ## Version 2.0.0-Beta-1

  **Date**: `2024-03-02`

  ### Changes

  **BREAKING CHANGE**: This is a complete rewrite of the V1.x Integration. There is no code left from the previous version, and as a result of that, there is NO DIRECT UPGRADE from version 1.x to V2.0.

  I have also used the opportunity to ensure this Integration delivers on the latest Home Assistant Requirements.

  The major changes are:
  - I now use a new API. The V1 API was based on a Renoweb API that is being phased ot, and over the last few months I have seen more and more municipalities disappearing from the supported municipalities. The new API is the same most Municipalities use, when you go to their official web page and search for your address and then get Pickup Schedules.
  - The `Sensors` are new, and not named the same way as the V1 sensors. Thus there is no upgrade path. With each sensor I now also iclude the official Pictograms as Entity Pictures, which you can use in your dashboard. **Note**: This image files must be installed manually - please see the README file).
  - There is a new local `Calendar` entity created, which has a full-day event every time there is a Pick-up. The event will contain a Description and what content is being picked up.
  - The `Binary Sensors` have not been created. If anyone uses these, raise an issue on Github.
  - **BREAKING**: As statet above all sensors will get new names and new unique ID's so you will have to change all your automations, scripts and dashboards to use the new sensor names. I am sorry for that, but it could not be avoided.


#### UPGRADING FROM VERSION 1.X

Here is the suggested *"Upgrade"* Procedure:

##### Remove your current Renoweb setup
1. Go to *Settings* | *Devices & Services
2. Click on *Renoweb Garbage Collection*
3. Click on the 3 dots to the right of each address you installed, and click *Delete*


##### Add Renoweb V2.0 to your system
**This only applies while we are running the Beta, after that just you the normal Installation/
Upgrade procedures**

* Go to *HACS* and then click on *Integrations*
* Find *Renoweb Garbage Collection* and click on it.
* In the upper right corner, click on the 3 dots, and select *Redownload*
* Now, **very important**, toggle the switch, *Show beta version* to On.
* The system will think a bit, and should then contain a list with Beta and Released version.
* Find the latest Beta version and click *Download*
* Once completed, restart Home Assistant
* When the system comes back:
  * Go to Configuration and Integrations
  * Click the + ADD INTEGRATION button in the lower right corner.
  * Search for *Renoweb** and click the integration.

-------------

<details>
  <summary><b>VERSION 1.x Changes </b></summary>

  ## Version 1.0.1

  **Date**: `2024-01-08`

  ### Changes
  - Adding a workaround for addresses and houses numbers with multile houses. (Like 2, 2A, "b etc.). You can now type the house number as <HOUSE_NUMBER>,<ID> and it will get the correct address. In order to to get the ID you can use the [renoweb.py](https://github.com/briis/pyrenoweb) program and follow the instructions below:

    To get the ID number you can execute the following commands using the renoweb.py program:

    Get the Municipality ID: `python3 renoweb.py municipality` Pick your ID from the list
    Get the Road ID: `python3 renoweb.py road <MUNICIPALITY_ID> <ZIP_CODE> <ROAD_NAME>`
    Get the Address ID (This is the ID used above): `python3 renoweb.py address <MUNICIPALITY_ID><ROAD_ID> <HOUSE_NUMBER>``

    Now pick the right ID from the last list of houses.

  Or if you can't get this to work, send me your address and I will find it for you 😀


  ## Version 1.0.0

  - `ADDED`: For each Bin there will now be a binary_sensor called `binary_sensor.BIN_NAME_valid`. This sensor will show if data for this specific bin is valid. I use it personally with the conditional card, to only show a card if the data is valid.
  - `CHANGED`: I have now rewritten some of the function to try and create more automatic recovery, should the sensor not get data on start on after an update. It will keep trying for a while, but if it takes too long it will give up, and not try again before the next timed update (Which per default is 6 hours). I did this a while ago and I do believe this introduces a **Breaking Change** as the sensors will get new names. (I honestly can't remember if this was the case) If this happens, just delete the Integration and re-add it, and then update you cards and automations with the new names. Sorry for any inconvinience.

  ## Version 0.1.16

  - `FIXED`: Ensuring all Unit of Measurrement are always the same (dage). This ensures that the sensors can be used with Helpers like the Min/Max helper.
  - `ADDED`: Added new sensor called `sensor.renoweb_days_until_next_pickup`, which shows the number of days until the next pick-up of any of the containers.

  ## Version 0.1.15

  - `FIXED`: Fixing deprecated `async_get_registry` that might start showing up in HA 2022.6

  ## Version 0.1.14

  * `FIXED`: Fixes issue #10, with a deprecation warning about `device_state_attributes`.

  ## Version 0.1.13

  * `FIXED`: **BREAKING CHANGE** Det viser sig at i nogle kommuner vil der forekomme afhentninger der hedder det samme - eksempelvis Haveaffald - men forekommer på forskellige tidspunkter. Hvis såddane forkommer, så ville kun den sidste af disse blive registreret. Denne version løser dette problem, ved at tilføje et unikt id til navnet. Men ved at gøre dette, så bryder det med tidligere versioner, som kun genererede et unikt id baseret på type. Så når man har opdateret til denne version, er det nødvendigt at:
    * Slette integration, fra *Integrations* siden og derefter tilføje den igen.
    * Rette på de sider hvor man viser sensorerne da de nu, for de flestes vedkommende, har fået nye navne
    * Rette i eventuelle automatiseringer, som anvender disse sensorer, af samme årsag som ovenfor.

    Beklager dette, men det er den eneste måde at sikre at alle data vises for alle.
    Fixer issue #7
  * `FIXED`: Tilføjet **iot_class** til `manifest.json`, som krævet af Home Assistant fra version 2021.5

  ## Version 0.1.12-Beta

  * `FIXED`: BREAKING CHANGE Det viser sig at i nogle kommuner vil der forekomme afhentninger der hedder det samme - eksempelvis Haveaffald - men forekommer på forskellige tidspunkter. Hvis såddane forkommer, så ville kun den sidste af disse blive registreret. Denne version løser dette problem, ved at tilføje et unikt id til navnet. Men ved at gøre dette, så bryder det med tidligere versioner, som kun genererede et unikt id baseret på type. Så når man har opdateret til denne version, er det nødvendigt at:
    * Slette integration, fra *Integrations* siden og derefter tilføje den igen.
    * Rette på de sider hvor man viser sensorerne da de nu, for de flestes vedkommende, har fået nye navne
    * Rette i eventuelle automatiseringer, som anvender disse sensorer, af samme årsag som ovenfor.

    Beklager dette, men det er den eneste måde at sikre at alle data vises for alle.
</details>