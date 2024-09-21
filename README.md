# cdo_objects

## Abstract
This script will extract the network objects and object-groups from Cisco Defense Orchestrator.

This is using the CDO UI API and is not recommneded for use. See the CDO Public API at https://developer.cisco.com/docs/cisco-defense-orchestrator/ for the API one should use. 

This script is provided as-is without warranty or conditions. See the LICENSE.txt file for more information.

## Script Usage
To use the script
1. Edit the env_sample file and add your CDO API key and CDO region endpoint
2. Rename the env_sample file as .env
3. Install the needed libraries in requirements.txt with
   `pip3 install -r requirements.txt`
4. Run the script with
   `python3 cdo_objects.py`

The script will retrieve all of the objects/object-groups from CDO and pretty print the json output to the screen as well as save it to the file `objects.json` in the directory where the script is run. 
