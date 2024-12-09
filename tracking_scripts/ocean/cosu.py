import decimal
import pendulum, json
import time
from bs4 import BeautifulSoup as bs
import requests
from .base import ShippingContainer
from tracking_scripts.ocean import utils

class COSUContainerBuilder(object):

    def __init__(self):
        self._instance = None

    def __call__(self, container_number, **_ignored):
        if not self._instance:
            self._instance = COSUContainer(container_number)
        return self._instance

class COSUContainer(ShippingContainer):

    def __init__(self, container_number):
        super().__init__(cn=container_number)
        self.shipping_line = "COSCO"

        # Validate and separate container number
        separated = utils.validate_container_number(number=self.number, separate=True)
        self.searchable_number = separated[0] + "  " + separated[1]

        # URLs for tracking
        self.url = f"https://elines.coscoshipping.com/ebtracking/public/containers/{self.number}?timestamp={{0}}"
        self.tracking_url = f"https://elines.coscoshipping.com/ebusiness/cargoTracking?trackingType=CONTAINER&number={self.number}"

        self.updates = []
        self.get_updates()

    def get_updates(self, tz="UTC"):
        s = requests.session()
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "elines.coscoshipping.com",
            "language": "en_US",
            "Referer": self.tracking_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "sys": "eb",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        }

        s.headers.update(headers)
        ts = str(float(round(decimal.Decimal(time.time()), 3))).replace(".", "")
        self.r = s.get(self.url.format(ts))  
        print("Response Content: ", self.r.content)

        j = self.r.json()  
        print("Parsed JSON: ", j)

        container_data = j.get('data', {}).get('content', {}).get('containers', [])[0]  
        container = {
            "containerNumber": container_data.get('container', {}).get('containerNumber', ''),
            "containerType": container_data.get('container', {}).get('containerType', '')
        }

        self.updates = []
        for status in container_data.get('containerCircleStatus', []):
            self.updates.append({
                "uuid": status.get('uuid', ''),
                "containerNumber": status.get('containerNumber', ''),
                "containerNumberStatus": status.get('containerNumberStatus', ''),
                "location": status.get('location', ''),
                "timeOfIssue": status.get('timeOfIssue', ''),
                "transportation": status.get('transportation', '')
            })

        result = {
            "container": container,
            "containerCircleStatus": self.updates
        }

        result = json.dumps(result, indent=2)
        print("Final Result: ", result)

        return result
