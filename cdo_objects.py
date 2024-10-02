#!/usr/bin/env python3
import logging
from json import dumps
from time import sleep
from cdo.cdo import CDOObjects
from dotenv import dotenv_values
from requests.exceptions import HTTPError, Timeout, TooManyRedirects

logging.basicConfig()
logger = logging.getLogger("cdo_objects")
logger.setLevel(logging.WARNING)


def write_output_file(objects: list, output_file: str) -> None:
    """Save the json output to a file"""
    with open(output_file, mode="w") as write_file:
        write_file.write(dumps(objects, indent=4))
    logger.warning(f"File written: {output_file}")


def get_objects(cdo: CDOObjects, query, obj_count: int, limit: int = 199) -> list[dict]:
    """Call the CDO UI API as many times as need to get all network objects and object-groups matching the query"""
    objects = []
    offset = 0
    burndown = obj_count
    while True:
        logger.warning(f"Total Objects Retrieved: {len(objects)}. Getting the next {limit} objects")

        try:
            objs = cdo.get_objects(query, offset=offset, limit=limit)
        except Timeout as e:
            logger.error(f"API did not respond within the timeout window {e}")
            raise SystemExit(e)
        except HTTPError as e:
            logger.error(f"HTTP Error {e.response.status_code} returned from API: {e.response.reason}")
            raise SystemExit(e)
        except TooManyRedirects as e:
            logger.error(f"Too many redirects. Do you have the correct URL?")
            raise SystemExit(e)

        for obj in objs:
            objects.append(
                {
                    "name": obj.get("name"),
                    "uid": obj.get("uid"),
                    "tags": obj.get("tags"),
                    "objectType": obj.get("objectType"),
                    "elements": obj.get("elements"),
                    "overrides": obj.get("overrides", []),
                    "overrideContents": obj.get("overrideContents", []),
                }
            )
        burndown -= limit
        if burndown <= 0:
            break
        offset += limit
        sleep(1)  # Don't hammer the CDO UI API
    logger.warning(f"{len(objects)} objects retrieved from CDO")
    return objects


def main(cdo_token: str, cdo_region: str, query: str, output_file="objects.json") -> None:
    cdo = CDOObjects(cdo_token, cdo_region)

    # Get the number of objects that we need to retreive for API paging
    obj_count = cdo.get_objects(query, count=True)

    # Call the API as many times as needed to get all of the objects
    logger.warning(f"Retrieving {obj_count} objects...")
    objects = get_objects(cdo, query, obj_count["aggregationQueryResult"])

    # Do whatever you want with the results....slice and dice to your liking
    write_output_file(objects, output_file)


if __name__ == "__main__":
    config = dotenv_values(".env")

    # Next steps if desired: Take this as an input value if you wish to search for specific objects and object-groups
    # search = "bad_actors"
    search = config.get("SEARCH")

    # This is the aegis way of getting all objects and network objects
    query = (
        "q=((cdoInternal%3Afalse)+AND+(isReadOnly%3Afalse+OR+metadata.CDO_FMC_READONLY%3Atrue"
        "+OR+objectType%3ASGT_GROUP))+AND+(NOT+issueType%3AINCONSISTENT+AND+NOT+issues%3ASHARED)"
        "+AND+(NOT+deviceType%3AFMC_MANAGED_DEVICE)+AND+((objectType%3A*NETWORK*))"
    )

    if search:
        # If we do not want all objects, search just for the objects with the given names
        query = f"{query[:2]}(name%3A*{search}*)+AND+{query[2:]}"

    main(config.get("CDO_TOKEN"), config.get("CDO_REGION").upper(), query)
