"""
Craigslist City & Category Discovery
Automatically discovers all available Craigslist locations and job categories.
"""
import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List
from pathlib import Path
import re
from utils import get_logger

logger = get_logger(__name__)


class CraigslistDiscovery:
    """Discovers all Craigslist cities and categories."""

    def __init__(self):
        self.cache_file = Path("data/craigslist_locations.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def discover_all_locations(self) -> Dict[str, Dict]:
        """
        Discover all Craigslist locations by scraping the sites page.
        Returns dict organized by country and state.
        """
        logger.info("Discovering Craigslist locations...")

        try:
            # Craigslist has a page listing all sites
            response = requests.get(
                'https://www.craigslist.org/about/sites',
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch sites page: {response.status_code}")
                return self._load_from_cache()

            soup = BeautifulSoup(response.text, 'html.parser')

            locations = {
                'US': {},  # US by state
                'Canada': {},  # Canada by province
                'International': {}  # Other countries
            }

            # Find all location boxes
            # US locations are in div.colmask
            us_section = soup.find('div', class_='colmask')
            if us_section:
                locations['US'] = self._parse_us_locations(us_section)

            # International locations
            intl_section = soup.find('div', class_='box', text=re.compile('international'))
            if intl_section:
                intl_parent = intl_section.find_parent('div', class_='box')
                if intl_parent:
                    locations['International'] = self._parse_intl_locations(intl_parent)

            # Save to cache
            self._save_to_cache(locations)

            logger.info(f"Discovered {sum(len(states) for states in locations['US'].values())} US cities")

            return locations

        except Exception as e:
            logger.error(f"Error discovering locations: {e}", exc_info=True)
            return self._load_from_cache()

    def _parse_us_locations(self, section) -> Dict[str, List[Dict]]:
        """Parse US locations organized by state."""
        states = {}

        # Find all state boxes
        for box in section.find_all('div', class_='box'):
            # State name is in h4
            state_header = box.find('h4')
            if not state_header:
                continue

            state_name = state_header.text.strip()
            cities = []

            # Cities are in <a> tags
            for link in box.find_all('a'):
                href = link.get('href', '')
                if not href or not href.startswith('http'):
                    continue

                # Extract city code from URL
                # Format: https://CITY.craigslist.org
                match = re.match(r'https://([^.]+)\.craigslist\.org', href)
                if match:
                    city_code = match.group(1)
                    city_name = link.text.strip()

                    cities.append({
                        'name': city_name,
                        'code': city_code,
                        'url': href
                    })

            if cities:
                states[state_name] = cities

        return states

    def _parse_intl_locations(self, section) -> Dict[str, List[Dict]]:
        """Parse international locations."""
        countries = {}

        for box in section.find_all('div', class_='box'):
            country_header = box.find('h4')
            if not country_header:
                continue

            country_name = country_header.text.strip()
            cities = []

            for link in box.find_all('a'):
                href = link.get('href', '')
                if not href:
                    continue

                match = re.match(r'https://([^.]+)\.craigslist\.org', href)
                if match:
                    city_code = match.group(1)
                    city_name = link.text.strip()

                    cities.append({
                        'name': city_name,
                        'code': city_code,
                        'url': href
                    })

            if cities:
                countries[country_name] = cities

        return countries

    def discover_job_categories(self) -> List[Dict]:
        """
        Discover all job categories by scraping a Craigslist jobs page.
        """
        logger.info("Discovering job categories...")

        try:
            # Use San Francisco as reference
            response = requests.get(
                'https://sfbay.craigslist.org/search/jjj',
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )

            if response.status_code != 200:
                return self._get_default_categories()

            soup = BeautifulSoup(response.text, 'html.parser')

            categories = []

            # Find category links in sidebar
            # They're usually in a list with class "cats"
            cat_section = soup.find('ul', class_='categories')
            if cat_section:
                for link in cat_section.find_all('a'):
                    href = link.get('href', '')
                    if '/search/' in href:
                        # Extract category code
                        match = re.search(r'/search/([a-z]+)', href)
                        if match:
                            cat_code = match.group(1)
                            cat_name = link.text.strip()

                            # Clean up name
                            cat_name = cat_name.replace('\n', ' ').strip()

                            categories.append({
                                'name': cat_name,
                                'code': cat_code
                            })

            if not categories:
                return self._get_default_categories()

            logger.info(f"Discovered {len(categories)} job categories")
            return categories

        except Exception as e:
            logger.error(f"Error discovering categories: {e}")
            return self._get_default_categories()

    def _get_default_categories(self) -> List[Dict]:
        """Return default job categories if discovery fails."""
        return [
            {'name': 'All Jobs', 'code': 'jjj'},
            {'name': 'Software / QA / DBA', 'code': 'sof'},
            {'name': 'Engineering', 'code': 'eng'},
            {'name': 'Web / HTML / Info Design', 'code': 'web'},
            {'name': 'Systems / Networking', 'code': 'sad'},
            {'name': 'Sales / Business Development', 'code': 'sls'},
            {'name': 'Marketing / PR / Advertising', 'code': 'mar'},
            {'name': 'Business / Management', 'code': 'bus'},
            {'name': 'Accounting / Finance', 'code': 'acc'},
            {'name': 'Science / Biotech', 'code': 'sci'},
            {'name': 'Education / Teaching', 'code': 'edu'},
            {'name': 'Government', 'code': 'gov'},
            {'name': 'Healthcare', 'code': 'hea'},
            {'name': 'Human Resources', 'code': 'hum'},
            {'name': 'Legal / Paralegal', 'code': 'lgl'},
            {'name': 'Real Estate', 'code': 'rea'},
            {'name': 'Retail / Wholesale', 'code': 'ret'},
            {'name': 'Food / Hospitality', 'code': 'foo'},
            {'name': 'Skilled Trades / Craft', 'code': 'trd'},
            {'name': 'General Labor', 'code': 'lab'},
            {'name': 'Transportation', 'code': 'trp'},
            {'name': 'Security', 'code': 'sec'},
            {'name': 'Salon / Spa / Fitness', 'code': 'spa'},
            {'name': 'Non-profit', 'code': 'npo'},
            {'name': 'Creative / Art / Design', 'code': 'crp'},
            {'name': 'Media / Journalism', 'code': 'med'},
            {'name': 'Customer Service', 'code': 'csr'},
            {'name': 'Admin / Office', 'code': 'ofc'},
            {'name': 'Architecture / Interior Design', 'code': 'arch'},
            {'name': 'TV / Film / Video', 'code': 'tfr'},
            {'name': 'Writing / Editing', 'code': 'wri'}
        ]

    def _save_to_cache(self, data: Dict):
        """Save discovered locations to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved locations to cache: {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _load_from_cache(self) -> Dict:
        """Load locations from cache file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                logger.info("Loaded locations from cache")
                return data
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")

        # Return default US cities if cache doesn't exist
        return self._get_default_us_cities()

    def _get_default_us_cities(self) -> Dict:
        """Return a curated list of major US cities."""
        return {
            'US': {
                'California': [
                    {'name': 'San Francisco Bay Area', 'code': 'sfbay', 'url': 'https://sfbay.craigslist.org'},
                    {'name': 'Los Angeles', 'code': 'losangeles', 'url': 'https://losangeles.craigslist.org'},
                    {'name': 'San Diego', 'code': 'sandiego', 'url': 'https://sandiego.craigslist.org'},
                    {'name': 'Sacramento', 'code': 'sacramento', 'url': 'https://sacramento.craigslist.org'},
                    {'name': 'Orange County', 'code': 'orangecounty', 'url': 'https://orangecounty.craigslist.org'},
                ],
                'New York': [
                    {'name': 'New York City', 'code': 'newyork', 'url': 'https://newyork.craigslist.org'},
                    {'name': 'Buffalo', 'code': 'buffalo', 'url': 'https://buffalo.craigslist.org'},
                    {'name': 'Albany', 'code': 'albany', 'url': 'https://albany.craigslist.org'},
                ],
                'Texas': [
                    {'name': 'Austin', 'code': 'austin', 'url': 'https://austin.craigslist.org'},
                    {'name': 'Houston', 'code': 'houston', 'url': 'https://houston.craigslist.org'},
                    {'name': 'Dallas', 'code': 'dallas', 'url': 'https://dallas.craigslist.org'},
                    {'name': 'San Antonio', 'code': 'sanantonio', 'url': 'https://sanantonio.craigslist.org'},
                ],
                'Washington': [
                    {'name': 'Seattle', 'code': 'seattle', 'url': 'https://seattle.craigslist.org'},
                ],
                'Massachusetts': [
                    {'name': 'Boston', 'code': 'boston', 'url': 'https://boston.craigslist.org'},
                ],
                'Illinois': [
                    {'name': 'Chicago', 'code': 'chicago', 'url': 'https://chicago.craigslist.org'},
                ],
                'Colorado': [
                    {'name': 'Denver', 'code': 'denver', 'url': 'https://denver.craigslist.org'},
                ],
                'Georgia': [
                    {'name': 'Atlanta', 'code': 'atlanta', 'url': 'https://atlanta.craigslist.org'},
                ],
                'Florida': [
                    {'name': 'Miami', 'code': 'miami', 'url': 'https://miami.craigslist.org'},
                    {'name': 'Orlando', 'code': 'orlando', 'url': 'https://orlando.craigslist.org'},
                    {'name': 'Tampa', 'code': 'tampa', 'url': 'https://tampa.craigslist.org'},
                ],
                'Arizona': [
                    {'name': 'Phoenix', 'code': 'phoenix', 'url': 'https://phoenix.craigslist.org'},
                ],
                'Oregon': [
                    {'name': 'Portland', 'code': 'portland', 'url': 'https://portland.craigslist.org'},
                ],
                'Pennsylvania': [
                    {'name': 'Philadelphia', 'code': 'philadelphia', 'url': 'https://philadelphia.craigslist.org'},
                ],
                'District of Columbia': [
                    {'name': 'Washington DC', 'code': 'washingtondc', 'url': 'https://washingtondc.craigslist.org'},
                ],
                'North Carolina': [
                    {'name': 'Raleigh', 'code': 'raleigh', 'url': 'https://raleigh.craigslist.org'},
                ],
                'Minnesota': [
                    {'name': 'Minneapolis', 'code': 'minneapolis', 'url': 'https://minneapolis.craigslist.org'},
                ],
                'Michigan': [
                    {'name': 'Detroit', 'code': 'detroit', 'url': 'https://detroit.craigslist.org'},
                ],
            },
            'Canada': {},
            'International': {}
        }

    def get_all_locations_flat(self) -> List[Dict]:
        """Get all locations as a flat list with state/country info."""
        locations = self.discover_all_locations()
        flat_list = []

        for country, states in locations.items():
            for state, cities in states.items():
                for city in cities:
                    flat_list.append({
                        **city,
                        'state': state,
                        'country': country
                    })

        return flat_list


def refresh_locations():
    """Refresh the locations cache."""
    discovery = CraigslistDiscovery()
    locations = discovery.discover_all_locations()
    categories = discovery.discover_job_categories()

    print(f"Discovered {sum(len(cities) for states in locations.get('US', {}).values() for cities in states)} US cities")
    print(f"Discovered {len(categories)} job categories")

    return locations, categories


if __name__ == "__main__":
    refresh_locations()
