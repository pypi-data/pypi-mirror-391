"""GraphQL web API utilities (unofficial, experimental).

This module provides access to Mapillary's GraphQL endpoint used by the web interface.
Unlike the official v4 REST API, this requires a public web token extracted from the
JavaScript bundle.

Use cases:
- Get user image counts without pagination
- Access leaderboard data
- Check for updates to existing downloads

WARNING: This is not officially documented and may break at any time.
"""

import json
import logging
import re
from datetime import datetime
from urllib.parse import urlencode, quote
import requests

logger = logging.getLogger("mapillary_downloader")

# Fallback token (extracted from main JS bundle as of 2025-01-09)
FALLBACK_TOKEN = "MLY|4223665974375089|d62822dd792b6a823d0794ef26450398"


def extract_token_from_js():
    """Extract public web token from Mapillary's JavaScript bundle.

    This fetches the main page, finds the main JS bundle, and extracts
    the hardcoded MLY token used for GraphQL queries.

    Returns:
        Token string (e.g., "MLY|123|abc...") or None if extraction failed
    """
    try:
        # Fetch main page to find JS bundle URL
        # Need consent cookie to get actual page (not GDPR banner)
        logger.debug("Fetching Mapillary main page...")
        # Generate today's date in the format YYYY_MM_DD for cookie
        today = datetime.now().strftime("%Y_%m_%d")
        cookies = {
            "mly_cb": f'{{"version":"1","date":"{today}","third_party_consent":"withdrawn","categories":{{"content_and_media":"withdrawn"}},"integration_controls":{{"YOUTUBE":"withdrawn"}}}}'
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.5",
            "Sec-GPC": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }
        response = requests.get("https://www.mapillary.com/app/", cookies=cookies, headers=headers, timeout=30)
        response.raise_for_status()

        # Find main JS file URL
        # Pattern: <script src="main.{hash}.js" type="module"></script>
        js_match = re.search(r'src="(main\.[a-f0-9]+\.js)"', response.text)
        if not js_match:
            logger.warning("Could not find main JS bundle URL in page")
            return None

        # URL is relative to /app/ base path
        js_url = f"https://www.mapillary.com/app/{js_match.group(1)}"
        logger.debug(f"Found JS bundle: {js_url}")

        # Fetch JS bundle
        logger.debug("Fetching JS bundle...")
        js_response = requests.get(js_url, timeout=30)
        js_response.raise_for_status()

        # Extract token
        # Pattern: "MLY|{client_id}|{secret}"
        token_match = re.search(r'"(MLY\|[^"]+)"', js_response.text)
        if not token_match:
            logger.warning("Could not find MLY token in JS bundle")
            return None

        token = token_match.group(1)
        logger.info(f"Extracted web token: {token[:20]}...")
        return token

    except requests.RequestException as e:
        logger.error(f"Failed to extract web token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error extracting web token: {e}")
        return None


def get_leaderboard(key="global", token=None):
    """Get leaderboard data from Mapillary GraphQL API.

    Args:
        key: Leaderboard key (e.g., "global", country name, etc.)
        token: MLY token (if None, will extract from JS bundle or use fallback)

    Returns:
        Dict with leaderboard data, or None on error
    """
    if token is None:
        token = extract_token_from_js()
        if token is None:
            logger.warning("Failed to extract token, using fallback")
            token = FALLBACK_TOKEN

    # GraphQL query for leaderboard (lifetime stats only)
    query = """query getUserLeaderboard($key: String!) {
  user_leaderboards(key: $key) {
    lifetime {
      count
      user {
        id
        username
        profile_photo_url
        __typename
      }
      __typename
    }
    __typename
  }
}"""

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.5",
            "Referer": "https://www.mapillary.com/",
            "content-type": "application/json",
            "authorization": f"OAuth {token}",
            "Origin": "https://www.mapillary.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }

        # Build query params - use quote_via=quote to get %20 instead of +
        # Note: both 'doc' and 'query' params seem to be required (from observed curl)
        params = {
            "doc": query,
            "query": query,
            "operationName": "getUserLeaderboard",
            "variables": json.dumps({"key": key}, separators=(',', ':')),
        }

        # Build URL with proper percent encoding (not + for spaces)
        # Don't encode parentheses to match curl behavior
        query_string = urlencode(params, quote_via=lambda s, safe='', encoding=None, errors=None: quote(s, safe='()!'))
        url = f"https://graph.mapillary.com/graphql?{query_string}"

        logger.debug(f"Querying leaderboard for key: {key}")

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        logger.error(f"Failed to query leaderboard: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error querying leaderboard: {e}")
        return None


if __name__ == "__main__":
    # Test the extraction and leaderboard query
    logging.basicConfig(level=logging.DEBUG)

    print("=== Extracting token ===")
    token = extract_token_from_js()
    if token:
        print(f"Success! Token: {token}")
    else:
        print("Failed to extract token")
        print(f"Fallback: {FALLBACK_TOKEN}")
        token = FALLBACK_TOKEN

    print("\n=== Querying global leaderboard ===")
    data = get_leaderboard("global", token=token)
    if data:
        print(json.dumps(data, indent=2))
    else:
        print("Failed to get leaderboard data")
