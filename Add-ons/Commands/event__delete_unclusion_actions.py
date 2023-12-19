import argparse
import datetime
from waapi import WaapiClient

import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    filename=datetime.datetime.now().strftime('%Y%m%d%H%M%S.log'),
)

parser = argparse.ArgumentParser(description='Delete non-inclusion actions for selected events')
parser.add_argument('id', nargs='+', help='An event ID (GUID)')

with WaapiClient() as client:
    try:
        # Get selected events & their actions
        selected_events = client.call("ak.wwise.ui.getSelectedObjects")
        print(f"getSelectedObjects{selected_events}")

        events = []
        for event in selected_events['objects']:
            print(f"event['id']: {event['id']}")
            args = {
                "from": {"id": [event["id"]]},
                "transform": [{"select": ['children']}]
            }

            options = {
                "return": ['@Target', 'inclusion', 'id']
            }
            actions = client.call("ak.wwise.core.object.get", args, options=options) or []
            print(f"actions: {actions}")
            for action in actions['return']:
                print(f"action: {action}")
                if action["inclusion"] is False:
                    events.append(action)

        # Delete non-inclusion actions
        for action in events:
            logging.info('Deleting action with ID: %s', action['@Target']['id'])
            client.call("ak.wwise.core.object.delete", object=action["id"])

        logging.info('Deleted %s non-inclusion actions from %s events.', len(events), len(set(event['id'] for event in events)))
    except Exception as e:
        print(f"An error occurred: {e}")
