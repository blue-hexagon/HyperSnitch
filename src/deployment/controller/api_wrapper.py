import sys
from time import sleep
from typing import Mapping, List, Optional, Union

import requests

from src.main.conf.conf_parser import ConfigLoader
from src.utils.logger import ConsoleLogger


class DOProvider:
    """
        This class ins't pretty, it works for the purpose
        but could make use of some refactoring and additonal HTTP status checks branching
     """
    api_base_url = "https://api.digitalocean.com/v2"
    api_key: str = ConfigLoader().load_config(with_env=True).digital_ocean.api_key
    logger = ConsoleLogger()

    @classmethod
    def headers(cls) -> Mapping[str, str]:
        return {"Authorization": f"Bearer {cls.api_key}", "Content-Type": "application/json"}

    @classmethod
    def create_vps(
            cls, droplet_name: str, api_slug: str, region: str, image: str, count: int, tag: List[str], ssh_keys: Optional[List[str]] = None
    ) -> str:

        payload = {
            "names": [droplet_name + "-" + str(x + 1) for x in range(count)],
            "region": region,
            "size": api_slug,
            "image": image,
            "ssh_keys": ssh_keys,
            "backups": False,
            "ipv6": True,
            "user_data": None,
            "private_networking": None,
            "volumes": None,
            "tags": tag,
        }
        response = requests.post(cls.api_base_url + "/droplets", headers=cls.headers(), json=payload)

        if response.status_code == 202:
            cls.logger.info(f"Droplet(s) with name(s):`{droplet_name}` successfully: {response.json()}")
            cls.logger.info(f"Droplet info: {response.json()}")
            droplet_id = response.json()['droplets'][0]['id']
            droplet_detail_url = f'https://api.digitalocean.com/v2/droplets/{droplet_id}'
            while True:
                detail_response = requests.get(droplet_detail_url, headers=cls.headers())
                if detail_response.status_code == 200:
                    detail_info = detail_response.json()
                    try:
                        ip_address = detail_info['droplet']['networks']['v4'][0]['ip_address']
                        cls.logger.info(f'Droplet created with IP address: {ip_address}')
                    except IndexError as e:
                        cls.logger.warning('Failed to retrieve droplet details - sleeping for 5 seconds.')
                        sleep(5)
                        continue
                    return ip_address
                else:
                    cls.logger.warning('Failed to retrieve droplet details - sleeping for 5 seconds.')
                    sleep(5)
        else:
            cls.logger.error(f"Failed to create {droplet_name}: {response.json()}")
            sys.exit(1)

    @classmethod
    def add_ssh_key(cls, key_name, public_key):
        data = {
            "name": key_name,
            "public_key": public_key,
        }
        response = requests.post(f"{cls.api_base_url}/account/keys", headers=cls.headers(), json=data)
        if response.status_code == 201:
            cls.logger.info("Uploaded public key successfully!")
        else:
            cls.logger.error(f"Failed to upload public key, error: {response.status_code}")
        return response.json()

    @classmethod
    def list_ssh_keys(cls):
        url = f"{cls.api_base_url}/account/keys"
        headers = {"Authorization": f"Bearer {cls.api_key}"}
        ssh_keys = []

        while url:  # Loop to handle pagination
            response = requests.get(url, headers=headers)
            data = response.json()
            ssh_keys.extend(data['ssh_keys'])  # Add keys from current page

            # Get the 'next' page URL if it exists
            url = data.get('links', {}).get('pages', {}).get('next', None)

        return ssh_keys

    @classmethod
    def get_ssh_key_fingerprints_from_names(cls, name: List[str]) -> List[str]:
        fingerprints = []
        ssh_keys = cls.list_ssh_keys()

        for ssh_key in ssh_keys:
            if ssh_key["name"] in name:  # Check for matching names
                fingerprints.append(ssh_key["fingerprint"])
        cls.logger.info(f"Found fingerpints: {[fp for fp in fingerprints]}")
        return fingerprints

    @classmethod
    def destroy_vps(cls, tag: Union[str, List[str]]) -> bool:
        if type(tag) == str:
            response = requests.delete(cls.api_base_url + f"/droplets?tag_name={tag}", headers=cls.headers())
        elif type(tag) == list:
            response = requests.delete(cls.api_base_url + f"/droplets?tag_name={tag}", headers=cls.headers())
        if response.status_code == 204:
            cls.logger.info(f"Droplets with `{tag}` deleted successfully.")
            return True
        else:
            cls.logger.error(f"Failed to delete droplets with tag `{tag}.")
            return False

    @classmethod
    def get_ssh_key_ids_from_names(cls, name: List[str]) -> List[str]:
        ids = []
        ssh_keys = cls.list_ssh_keys()

        for ssh_key in ssh_keys:
            if ssh_key["name"] in name:  # Check for matching names
                ids.append(ssh_key["id"])
        cls.logger.info(f"Found SSH-key IDs: {ids} for name: {name}")
        return ids

    @classmethod
    def delete_ssh_key(cls, name):
        ids = DOProvider.get_ssh_key_ids_from_names([name])
        for _id in ids:
            response = requests.delete(f"{cls.api_base_url}/account/keys/{_id}", headers={"Authorization": f"Bearer {cls.api_key}"})
            if response.status_code == 204:
                cls.logger.info("Deleted SSH key successfully!")
            else:
                cls.logger.error(f"Failed to delete SSH key, error: {response.status_code}")
