import re
import requests
from typing import List, Dict, Optional

class Application:
    def __init__(self, url: str, client_id: str, client_secret: str):
        self.url = url

        self.channels: Channels = Channels()
        self.sender: Optional[Channel] = None
        self.receiver: Optional[Channel] = None

        self._parse_url()
        self.id_token = self.get_token(client_id, client_secret)
        self.get_metadata()
        self.get_runtime_channels()
        self.get_amqp_url()

    def __repr__(self):
        return f"Application(url={self.url})"
    
    def _parse_url(self):
        m = re.match(r"(?P<base_url>https?:\/\/(?P<host>.+?))\/applications\/(?P<application>.*)", self.url)
        if not m:
            raise ValueError(
                f"Неверный формат url приложения: {self.url}."
                "Ожидается 'http(s)://host(:port)/applications/name'"
            )
        self.base_url = m.group("base_url")
        self.host = m.group("host").split(":")[0]
        self.application = m.group("application")

    def _request(self, method: str, url: str, **kwargs):
        kwargs.setdefault("verify", True)
        kwargs.setdefault("timeout", 10)
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get_token(self, client_id, client_secret):
        auth_url = f"{self.base_url}/auth/oidc/token"
        resp = self._request(
            "post",
            auth_url,
            data="grant_type=client_credentials",
            auth=(client_id, client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        self.id_token = resp.json()["id_token"]
        return self.id_token
    
    def get_metadata(self):
        channel_url = f"{self.url}/sys/esb/metadata/channels"
        headers = {"Authorization": f"Bearer {self.id_token}"}
        resp = self._request(
            "get",
            channel_url,
            headers=headers,
            )
        resp_json = resp.json()

        self.channels._load_channels(resp_json)
        return self.channels

    def get_runtime_channels(self):
        channel_url = f"{self.url}/sys/esb/runtime/channels"
        headers = {"Authorization": "Bearer " + self.id_token}
        resp = self._request(
            "get",
            channel_url,
            headers=headers,
            )
        resp_json = resp.json()

        self.port_amqp = resp_json.get("port")

        self.channels._set_sender_channel(resp_json.get("items"))
        self.channels._set_receiver_channel(resp_json.get("items"))

        self.sender = next((ch for ch in self.channels.senders if ch.destination), None)
        self.receiver = next((ch for ch in self.channels.receivers if ch.destination), None)

        return {"senders": self.channels.senders, "receivers": self.channels.receivers}

    def _set_sender_channel(self, channel_name):
        for ch in self.channels:
            if ch.channel == channel_name:
                self.sender_channel = ch
                break
    
    def _set_receiver_channel(self, channel_name):
        for ch in self.channels:
            if ch.channel == channel_name:
                self.receiver_channel = ch
                break

    def get_amqp_url(self):
        vhost = f"/applications/{self.application}"
        self.amqp_url = f"amqp://{self.id_token}:{self.id_token}@{self.host}:{self.port_amqp}{vhost}"
        return self.amqp_url

class Channel():
    """Канал"""
    def __init__(self, channel, process, **kwargs: Dict):
        self.channel = channel
        self.channel_description = kwargs.get("channelDescription")
        self.process = process
        self.process_description = kwargs.get("processDescription")
        self.destination = kwargs.get("destination")
        self.access = kwargs.get("access")

    def __repr__(self):
        return f"Channel({self.channel}: access={self.access}{', active' if self.destination else ''})"
    
class Channels(List[Channel]):
    """Коллекция каналов"""
    def __init__(self):
        super().__init__()
        self.senders: List[Channel] = [] 
        self.receivers: List[Channel] = []

    def __repr__(self):
        return f"Channels list(channels={len(self)})"

    def _load_channels(self, items: List[Dict]):
        if items:
            for item in items:
                self.append(Channel(**item))
        self.senders.clear()
        self.senders.extend([c for c in self if c.access == "WRITE_ONLY"]) 
        self.receivers.clear()
        self.receivers.extend([c for c in self if c.access == "READ_ONLY"])
    
    def _set_sender_channel(self, runtime_channel: Optional[List[Dict]]):
        if not runtime_channel:
            return
        for ch in self.senders:
            for item in runtime_channel:
                if ch.channel == item["channel"] and ch.process == item["process"]:
                    ch.destination = item["destination"]

    def _set_receiver_channel(self, runtime_channel: Optional[List[Dict]]):
        if not runtime_channel:
            return
        for ch in self.receivers:
            for item in runtime_channel:
                if ch.channel == item["channel"] and ch.process == item["process"]:
                    ch.destination = item["destination"]
