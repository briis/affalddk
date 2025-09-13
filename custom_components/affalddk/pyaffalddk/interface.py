import aiohttp
import base64
import datetime as dt
import logging
import re
import json
from urllib.parse import urlparse, parse_qsl, quote
from bs4 import BeautifulSoup

from .const import GH_API


_LOGGER = logging.getLogger(__name__)


def clean_name(name):
    # removes everything from the last comma if postalcode in last part
    return re.sub(r',\s*\d{4}.*$', '', name)


class AffaldDKNotSupportedError(Exception):
    """Raised when the municipality is not supported."""


class AffaldDKNotValidAddressError(Exception):
    """Raised when the address is not found."""


class AffaldDKNoConnection(Exception):
    """Raised when no data is received."""


class AffaldDKGarbageTypeNotFound(Exception):
    """Raised when new garbage type is detected."""


class AffaldDKAPIBase:
    """Base class for the API."""

    def __init__(self, municipality_id, session=None) -> None:
        """Initialize the class."""
        self.municipality_id = municipality_id
        self.session = session
        self.address_list = {}
        if self.session is None:
            self.session = aiohttp.ClientSession()
        self.today = dt.date.today()
        self.year = self.today.year

    async def get_address(self, address_name):
        if address_name in self.address_list:
            return self.address_list[address_name]['id'], address_name
        return None, None

        self.url_search = "https://api.dataforsyningen.dk/adresser"

    async def get_df_address_list(self, code, zipcode, street, house_number):
        url_search = "https://api.dataforsyningen.dk/adresser"
        para = {'kommunekode': code, 'q': f'{street} {house_number}'.strip(), 'struktur': 'mini'}
        data = await self.async_get_request(url_search, para=para)
        self.address_list = {}
        for item in data:
            if str(zipcode) in item['postnr']:
                self.update_address_list(item, 'betegnelse', 'id')
        return list(self.address_list.keys())

    async def get_kvhx(self, code, address_name):
        url_search = "https://api.dataforsyningen.dk/adresser"
        item = self.address_list.get(address_name)
        if item:
            para = {'kommunekode': code, 'id': item['id']}
            row = await self.async_get_request(url_search, para=para)
            return row[0]["kvhx"], address_name

    def update_address_list(self, item, name_key, id_key):
        name = clean_name(item[name_key])
        if name in self.address_list:
            name += ' *'
            while name in self.address_list:
                name += '*'
        self.address_list[name] = {'id': item[id_key], 'fullname': item[name_key]}

    async def async_get_request(self, url, headers=None, para=None, as_json=True, new_session=False):
        return await self.async_api_request('GET', url, headers, para, as_json, new_session)

    async def async_post_request(self, url, headers={"Content-Type": "application/json"}, para=None, as_json=True, new_session=False):
        return await self.async_api_request('POST', url, headers, para, as_json, new_session)

    async def async_postform_request(self, url, headers={"Content-Type": "application/x-www-form-urlencoded"}, para=None, as_json=True, new_session=False):
        return await self.async_api_request('POSTform', url, headers, para, as_json, new_session)

    async def async_api_request(self, method, url, headers, para=None, as_json=True, new_session=False):
        """Make an API request."""

        if new_session:
            session = aiohttp.ClientSession()
        else:
            session = self.session

        data = None
        if method == 'POST':
            json_input = para
            data_input = None
            params_input = None
        elif method == 'POSTform':
            method = 'POST'
            json_input = None
            data_input = para
            params_input = None
        else:
            json_input = None
            data_input = None
            params_input = para

        async with session.request(method, url, headers=headers, json=json_input, params=params_input, data=data_input) as response:
            if response.status != 200:
                if new_session:
                    await session.close()

                if response.status == 400:
                    raise AffaldDKNotSupportedError(
                        "Municipality not supported")

                if response.status == 404:
                    raise AffaldDKNotSupportedError(
                        "Municipality not supported")

                if response.status == 503:
                    raise AffaldDKNoConnection(
                        "System API is currently not available")

                raise AffaldDKNoConnection(
                    f"Error {response.status} from {url}")
            if as_json:
                data = await response.json()
            else:
                data = await response.text()
            if new_session:
                await session.close()

            return data


class NemAffaldAPI(AffaldDKAPIBase):
    # NemAffaldService API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._token = None
        self._id = None
        self.street = None
        self.base_url = f'https://nemaffaldsservice.{self.municipality_id}.dk'

    @property
    async def token(self):
        if self._token is None:
            await self._get_token()
        return self._token

    async def _get_token(self):
        data = ''
        async with self.session.get(self.base_url) as response:
            data = await response.text()

        if data:
            match = re.search(
                r'name="__RequestVerificationToken"\s+[^>]*value="([^"]+)"', data)
            if match:
                self._token = match.group(1)

    async def get_address_list(self, zipcode, street, house_number):
        url = self.base_url + '/WasteHome/AddressByTerm'
        para = {'term': f'{street} {house_number}'.strip(), 'limit': 100}
        data = await self.async_get_request(url, para=para, as_json=False)
        data = json.loads(data)
        self.address_list = {}
        for item in data:
            self.update_address_list(item, 'label', 'Id')
        return list(self.address_list.keys())

    async def get_address(self, address_name):
        url = f"{self.base_url}/WasteHome/SearchCustomerRelation"
        data = {'__RequestVerificationToken': await self.token, 'SearchTerm': address_name}
        async with self.session.post(url, data=data) as response:
            if len(response.history) > 1:
                o = urlparse(response.history[1].headers['Location'])
                id = dict(parse_qsl(o.query))['customerId']
                return id, address_name
        return None, None

    async def async_get_ical_data(self, customerid):
        ics_data = ''
        data = {'customerId': customerid, 'type': 'ics'}
        async with self.session.get(f"{self.base_url}/Calendar/GetICaldendar", data=data) as response:
            ics_data = await response.text()
        return ics_data

    async def get_garbage_data(self, address_id):
        return await self.async_get_ical_data(address_id)


class VestForAPI(AffaldDKAPIBase):
    # Vest Forbrænding API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = "https://selvbetjening.vestfor.dk"
        self.url_data = self.baseurl + "/Home/MinSide"
        self.url_search = self.baseurl + "/Adresse/AddressByName"

    async def get_address_list(self, zipcode, street, house_number):
        para = {'term': f'{street} {house_number}'.strip(), 'numberOfResults': 100}
        data = await self.async_get_request(self.url_search, para=para)
        self.address_list = {}
        for item in data:
            if str(zipcode) in item['Postnr']:
                self.update_address_list(item, 'FuldtVejnavn', 'Id')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        para = {'address-selected-id': address_id}
        _ = await self.async_get_request(self.url_data, para=para, as_json=False)
        url = 'https://selvbetjening.vestfor.dk/Adresse/ToemmeDates'
        para = {
            'start': str(self.today + dt.timedelta(days=-1)),
            'end': str(self.today + dt.timedelta(days=60))
            }
        data = await self.async_get_request(url, para=para)
        return data


class PerfectWasteAPI(AffaldDKAPIBase):
    # Perfect Waste API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = "https://europe-west3-perfect-waste.cloudfunctions.net"
        self.url_data = self.baseurl + "/getAddressCollections"
        self.url_search = self.baseurl + "/searchExternalAddresses"

    async def get_address_list(self, zipcode, street, house_number):
        para = {'data': {
            "query": f"{street} {house_number}".strip(),
            "municipality": self.municipality_id,
            "page": 1, "onlyManual": False
            }}

        page = await self.async_post_request(self.url_search, para=para)
        data = page['result']
        while len(page['result']) == 30:
            para['data']['page'] += 1
            page = await self.async_post_request(self.url_search, para=para)
            data += page['result']
        self.address_list = {}
        for item in data:
            if str(zipcode) in item['displayName']:
                self.update_address_list(item, 'displayName', 'addressID')
        return list(self.address_list.keys())

    async def save_to_db(self, address_id):
        url = self.baseurl + '/fetchAddressAndSaveToDb'
        para = {"data": {
            "addressID": address_id, "municipality": self.municipality_id,
            "caretakerCode": None, "isCaretaker": None}}
        await self.async_post_request(url, para=para)

    async def get_garbage_data(self, address_id):
        body = {"data": {
            "addressID": address_id,
            "municipality": self.municipality_id
            }}
        data = await self.async_post_request(self.url_data, para=body)
        return data["result"]


class RenowebghAPI(AffaldDKAPIBase):
    # Renoweb servicegh API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_data = "https://servicesgh.renoweb.dk/v1_13/"
        self.uuid = base64.b64decode(GH_API).decode('utf-8')
        self.headers = {'Accept-Encoding': 'gzip'}

    async def get_address_list(self, zipcode, street, house_number):
        road_id = await self.get_road(zipcode, street)
        if road_id:
            url = self.url_data + 'GetJSONAdress.aspx'
            para = {'apikey': self.uuid, 'municipalitycode': self.municipality_id, 'roadid': road_id}
            if house_number:
                para['streetBuildingIdentifier'] = house_number
            data = await self.async_get_request(url, para=para, headers=self.headers)
            self.address_list = {}
            for item in data['list']:
                if str(zipcode) in item['presentationString']:
                    self.update_address_list(item, 'presentationString', 'id')
            return list(self.address_list.keys())
        return []

    async def get_road(self, zipcode, street):
        url = self.url_data + 'GetJSONRoad.aspx'
        data = {
            'apikey': self.uuid, 'municipalitycode': self.municipality_id,
            'roadname': street
        }
        js = await self.async_get_request(url, para=data, headers=self.headers)
        for item in js['list']:
            if str(zipcode) in item['name']:
                return item['id']
        return None

    async def get_garbage_data(self, address_id, fullinfo=0, shared=0):
        url = self.url_data + 'GetJSONContainerList.aspx'
        data = {
            'apikey': self.uuid, 'municipalitycode': self.municipality_id,
            'adressId': address_id, 'fullinfo': fullinfo, 'supportsSharedEquipment': shared,
            }
        js = await self.async_get_request(url, para=data, headers=self.headers)
        if js:
            return js['list']
        return []


class AffaldOnlineAPI(AffaldDKAPIBase):
    # Affald online / Renoweb API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = "https://www.affaldonline.dk/api/address/"
        uuid = base64.b64decode(self.municipality_id).decode('utf-8')
        self.headers = {
            'X-Client-Provider': uuid,
            'X-Client-Type': 'Kunde app',
            'X-Client-Version': '22',
        }

    async def get_address_list(self, zipcode, street, house_number):
        para = {'q': f'{street} {house_number}'.strip(), 'page': 1}
        page = await self.async_get_request(self.url_base + 'search', para=para, headers=self.headers)
        data = page['results']
        while len(page['results']) == 50:
            para['page'] += 1
            page = await self.async_get_request(self.url_base + 'search', para=para, headers=self.headers)
            data += page['results']
        self.address_list = {}
        for item in data:
            if str(zipcode) in item['displayName']:
                self.update_address_list(item, 'displayName', 'addressId')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        para = {'groupBy': 'date', 'addressId': address_id}
        data = await self.async_get_request(self.url_base + 'collections', para=para, headers=self.headers)
        return data


class OpenExperienceAPI(AffaldDKAPIBase):
    # Open Experience API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = f"https://{self.municipality_id}"

    async def get_address_list(self, zipcode, street, house_number):
        address = f'{street} {house_number}'.strip()
        url = self.url_base + f'search/address/{quote(address)}/limit/200'
        data = await self.async_get_request(url)
        self.address_list = {}
        for item in sorted(data['results'], key=lambda x: int(x["addressId"])):
            if str(zipcode) in item['displayName']:
                self.update_address_list(item, 'displayName', 'addressId')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        url = self.url_base + f'address/{address_id}/collections'
        data = await self.async_get_request(url)
        return data


class OpenExperienceLiveAPI(AffaldDKAPIBase):
    # Open Experience API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = "https://live.affaldsapi.dk/"
        uuid = base64.b64decode(self.municipality_id[1:]).decode('utf-8')
        self.headers = {'X-Auth-Token': uuid}
        self.mid = self.municipality_id[0]

    async def get_address_list(self, zipcode, street, house_number):
        address = f'{street} {house_number}'.strip()
        url = self.url_base + f'address/v1/search/{self.mid}/{quote(address)}/100'
        data = await self.async_get_request(url, headers=self.headers)
        self.address_list = {}
        for item in sorted(data, key=lambda x: int(x["id"])):
            if str(zipcode) in item['name']:
                self.update_address_list(item, 'name', 'id')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        url = self.url_base + f'arrangements/v1/collections/calendar/{self.mid}/{address_id}'
        data = await self.async_get_request(url, headers=self.headers)
        return data


class ProvasAPI(AffaldDKAPIBase):
    # Provas API (Haderslev)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = "https://platform-api.wastehero.io/api-crm-portal/v1/"
        self._token = None

    @property
    async def token(self):
        if not self._token:
            vars = {"username": "", "password": ""}
            url = self.url_base + 'company/provas-portal.wastehero.io/login'
            data = await self.async_post_request(url, para=vars)
            self._token = data.get('token')
        return self._token

    async def get_address_list(self, zipcode, street, house_number):
        headers = {'X-API-Key': await self.token}
        address = f'{street} {house_number}, {zipcode}'.strip()
        url = self.url_base + 'property/'
        data = await self.async_get_request(url, para={'search': address, 'limit':100}, headers=headers)
        self.address_list = {}
        for item in data:
            item['name'] = item['location']['name']
            if str(zipcode) in item['name']:
                self.update_address_list(item, 'name', 'id')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        headers = {'X-API-Key': await self.token}
        url = self.url_base + f'property/{address_id}/collection_log'
        params = {
            'from_date': str(self.today + dt.timedelta(days=-1)),
            'to_date': str(self.today + dt.timedelta(days=60))
        }
        data = await self.async_get_request(url, para=params, headers=headers)
        return data


class RenoDjursAPI(AffaldDKAPIBase):
    # Reno Djurs API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = "https://minside.renodjurs.dk"

    async def get_address_list(self, zipcode, street, house_number):
        address = f'{street} {house_number}*, {zipcode}'.strip()
        url = self.url_base + '/Default.aspx/GetAddress'
        data = await self.async_post_request(url, para={'address': address.strip()})
        self.address_list = {}
        for item in data['d']:
            if str(zipcode) in item['label']:
                self.update_address_list(item, 'label', 'value')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        url = self.url_base + '/Ordninger.aspx?id=55424'
        data = await self.async_get_request(url, as_json=False)
        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table", class_="table--compact")

        headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
        rows = []
        for tr in table.find("tbody").find_all("tr"):
            td = tr.find_all("td")
            if len(td) == len(headers):
                row_data = {h: td.get_text(strip=True) for h, td in zip(headers, td)}
                if row_data['Næste tømningsdag']:
                    rows.append(row_data)
        return rows


class AffaldWebAPI(AffaldDKAPIBase):
    # Herning API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = "https://affaldsweb.net/affaldweb"
        self.url_search = "https://affaldsweb.net/dagrenovation/find_veje.php"

    async def get_address_list(self, zipcode, street, house_number):
        address = f'{street} {house_number}'.strip()
        letters_encoded = quote(address.encode('windows-1252'))

        url = f"{self.url_search}?getCountriesByLetters=1&letters={letters_encoded}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
        }
        data = await self.async_post_request(url, headers=headers, as_json=False)
        self.address_list = {}
        for line in data.split('|'):
            if line:
                id, name = line.split('###')
                self.update_address_list({'name': name, 'id': id}, 'name', 'id')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        url = self.url_base + '/ruter.php'
        params = {"ejdnr": address_id}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        data = await self.async_get_request(url, para=params, headers=headers, as_json=False)

        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table")
        header_row = table.find('tr')
        header_cells = header_row.find_all(['th', 'td'])
        headers = [cell.get_text(strip=True) for cell in header_cells]
        if ['Beholder-id', 'Tømningsdag'] == headers[2:]:
            data = []
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                row_data = [cell.get_text(separator=' ', strip=True) for cell in cells]
                data.append({'Beholder-id': row_data[2], 'Tømningsdag': row_data[3]})
            return data

    def get_weekday_and_weeks(self, item):
        weekday, rest = item['Tømningsdag'].split(None, 1)
        weeks = []
        if 'Ugenumre:' in rest:
            this_week = self.today.isocalendar()[1]
            for w in rest.split('Ugenumre:')[1].split(','):
                if int(w) < this_week:
                    weeks.append([int(w), self.year + 1])
                else:
                    weeks.append([int(w), self.year])
        elif 'ulige' in rest.lower():
            weeks.append([-1, self.year])
        else:
            weeks.append([-2, self.year])
        return weekday, weeks


class SilkeborgAPI(AffaldDKAPIBase):
    # Silkeborg API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = 'https://www.affaldonline.dk/kalender/silkeborg'

    async def get_address_list(self, zipcode, street, house_number):
        self.address_list = {}
        # street
        url = f"{self.url_base}/acCal.php"
        streets = await self.async_get_request(url, para={'term': street.strip()}, as_json=False)
        streets = json.loads(streets)

        # house numbers
        url = f"{self.url_base}/husnrCal.php"
        for street in streets:
            if str(zipcode) in str(street['postnr']):
                params = {
                    'vejnavn': street['vejnavn'],
                    'postnr': street['postnr'],
#                    'postdist': item['Bynavn'],
                }
                data = await self.async_get_request(url, para=params, as_json=False)
                soup = BeautifulSoup(data, "html.parser")
                for opt in soup.select("select#SelHusNr option"):
                    number = opt.text.strip()
                    if house_number in number:
                        item = {
                            'name': f"{street['vejnavn']} {number}, {street['postnr']} {street['Bynavn']}",
                            'id': opt["value"]
                        }
                        self.update_address_list(item, 'name', 'id')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        url = self.url_base + '/showInfo.php'
        data = await self.async_postform_request(url, para={'values': address_id}, as_json=False)
        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table")
        results = []
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                date = cols[0].get_text(strip=True)
                desc = cols[1].get_text(strip=True)
                for desc in cols[1].get_text(strip=True).split(', '):
                    results.append({
                        'Materiel': desc.strip(),
                        'Tømningsdag': self.get_next_upcoming_date(date)
                        })
        return results

    def get_next_upcoming_date(self, date_str):
        current_year = self.today.year
        candidates = []

        for part in date_str.split(','):
            part = part.strip()
            try:
                # Parse as this year first
                dt_this_year = dt.datetime.strptime(f"{part}-{current_year}", "%d-%m-%Y").date()
                if dt_this_year >= self.today:
                    candidates.append(dt_this_year)
                else:
                    # If in the past, add with next year
                    dt_next_year = dt.datetime.strptime(f"{part}-{current_year + 1}", "%d-%m-%Y").date()
                    candidates.append(dt_next_year)
            except ValueError:
                continue
        return min(candidates) if candidates else None


class IkastBrandeAPI(AffaldDKAPIBase):
    # Ikast / Brande API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = "https://skrald.ikast-brande.dk/Adresse"

    async def get_address_list(self, zipcode, street, house_number):
        address = f'{street} {house_number}'.strip()
        url = f"{self.url_base}/Typeahead"
        data = await self.async_post_request(url, para={'query': address.strip(), 'limit': 30000})
        self.address_list = {}
        for item in data:
            if str(zipcode) in item['Beliggenhed']:
                self.update_address_list(item, 'Beliggenhed', 'AdresseId')
        return list(self.address_list.keys())

    async def get_garbage_data(self, address_id):
        url = self.url_base + '/SubmitAdresse'
        params = {
            "hiddenPrevController": "Tomningsinfo",
            "hiddenPrevAction": "Index",
            "hiddenSiteType": "R",
            "hiddenId": address_id
        }

        data = await self.async_post_request(url, para=params, as_json=False)
        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table")
        header_row = table.find('tr')
        header_cells = header_row.find_all(['th', 'td'])
        headers = [cell.get_text(strip=True) for cell in header_cells]
        if headers[3] == 'Kommende tømninger':
            data = []
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if cells:
                    row_data = [cell.get_text(separator=' ', strip=True) for cell in cells]
                    if row_data[3]:
                        data.append({
                            'Materiel': row_data[0],
                            'Tømningsdag': self.get_next_upcoming_date(row_data[3])
                            })

            return data

    def get_next_upcoming_date(self, date_str):
        current_year = self.today.year
        candidates = []

        for part in date_str.split(','):
            part = part.strip()
            try:
                # Parse as this year first
                dt_this_year = dt.datetime.strptime(f"{part}-{current_year}", "%d-%m-%Y").date()
                if dt_this_year >= self.today:
                    candidates.append(dt_this_year)
                else:
                    # If in the past, add with next year
                    dt_next_year = dt.datetime.strptime(f"{part}-{current_year + 1}", "%d-%m-%Y").date()
                    candidates.append(dt_next_year)
            except ValueError:
                continue
        return min(candidates) if candidates else None


class RenoSydAPI(AffaldDKAPIBase):
    # Reno Syd API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_base = "https://skoda-selvbetjeningsapi.renosyd.dk/api/v1"

    async def get_address_list(self, zipcode, street, house_number):
        return await self.get_df_address_list(self.municipality_id, zipcode, street, house_number)

    async def get_address(self, address_name):
        kvhx, address_name = await self.get_kvhx(self.municipality_id, address_name)
        if kvhx:
            url = self.url_base + f'/adresser/{kvhx}/standpladser'
            data = await self.async_get_request(url)
            if data:
                return data[0]['nummer'], address_name

    async def get_garbage_data(self, address_id):
        url = f"{self.url_base}/toemmekalender?nummer={address_id}"
        data = await self.async_get_request(url)
        return data[0]["planlagtetømninger"]


class AarhusAffaldAPI(AffaldDKAPIBase):
    # Aarhus Forsyning API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_data = "https://portal-api.kredslob.dk/api/calendar/address/"
        self.url_search = "https://api.dataforsyningen.dk/adresser"

    async def get_address_list(self, zipcode, street, house_number):
        return await self.get_df_address_list(751, zipcode, street, house_number)

    async def get_address(self, address_name):
        return await self.get_kvhx(751, address_name)

    async def get_garbage_data(self, address_id):
        url = f"{self.url_data}{address_id}"
        data = await self.async_get_request(url)
        return data[0]["plannedLoads"]


class OdenseAffaldAPI(AffaldDKAPIBase):
    # Odense Renovation API
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_data = "https://mit.odenserenovation.dk/api/Calendar/GetICalCalendar?addressNo="
        self.url_search = "https://mit.odenserenovation.dk/api/Calendar/CommunicationHouseNumbers?addressString="

    async def get_address_list(self, zipcode, street, house_number):
        address = f'{street} {house_number}'.strip()
        url = f"{self.url_search}{quote(address)}"
        data = await self.async_get_request(url)
        self.address_list = {}
        for item in data:
            if str(zipcode) in item['PostCode']:
                self.update_address_list(item, 'FullAddress', 'AddressNo')
        return list(self.address_list.keys())

    async def async_get_ical_data(self, address_id):
        """Get data from iCal API."""
        url = f"{self.url_data}{address_id}"
        data = await self.async_get_request(url, as_json=False)
        return data

    async def get_garbage_data(self, address_id):
        return await self.async_get_ical_data(address_id)
