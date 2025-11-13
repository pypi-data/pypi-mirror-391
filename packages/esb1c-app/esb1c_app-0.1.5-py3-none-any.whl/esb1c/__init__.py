import re
import requests
from typing import List, Dict, Optional

class Application:
    def __init__(self, url: str, client_id: str, client_secret: str):
        self.url: Url = Url(url)

        self.channels: Channels = Channels()
        self.sender: Optional[Channel] = None
        self.receiver: Optional[Channel] = None

        self.id_token: str = self.get_token(client_id, client_secret)
        
        self.get_metadata()
        self.get_runtime_channels()
        
        self.amqp_url: str = self.get_amqp_url()

    def __repr__(self):
        return f"Application(url={self.url})"
    
    def _request(self, method: str, url: str, **kwargs):
        kwargs.setdefault("verify", True)
        kwargs.setdefault("timeout", 10)
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get_token(self, client_id, client_secret):
        auth_url = f"{self.url.base_url}/auth/oidc/token"
        resp = self._request(
            "post",
            auth_url,
            data="grant_type=client_credentials",
            auth=(client_id, client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        return resp.json()["id_token"]
    
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
        headers = {"Authorization": f"Bearer {self.id_token}"}
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
        return f"amqp://{self.id_token}:{self.id_token}@{self.url.host}:{self.port_amqp}{self.url.vhost}"

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
    
    def __str__(self):
        return f"Channel({self.channel}: access={self.access}{', active' if self.destination else ''})"

    def to_dict(self):
        return {
            "channel": self.channel,
            "channel_description": self.channel_description,
            "process": self.process,
            "process_description": self.process_description,
            "destination": self.destination,
            "access": self.access,
        }

class Channels(List[Channel]):
    """Коллекция каналов"""
    def __init__(self):
        super().__init__()
        self.senders: List[Channel] = [] 
        self.receivers: List[Channel] = []

    def __repr__(self):
        return f"Channels list(channels={len(self)})"

    def to_dict(self):
        return [ch.to_dict() for ch in self]

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

class Url:
    """URL приложения"""
    def __init__(self, url: str):
        self.url: str = url
        self._parse_url()

    def __repr__(self):
        return f"Url({self.url!r})"
    
    def __str__(self):
        return f"{self.url}"
    
    def to_dict(self):
        return {
            "url": self.url,
            "base_url": self.base_url,
            "host": self.host,
            "port": self.port,
            "application_name": self.application_name,
            "vhost": self.vhost,
        }

    def _parse_url(self):
        m = re.match(r"(?P<base_url>https?:\/\/(?P<host>.+?))\/applications\/(?P<application>.*)", self.url)
        if not m:
            raise ValueError(
                f"Неверный формат url приложения: {self.url}."
                "Ожидается 'http(s)://host(:port)/applications/name'"
            )
        self.base_url: str = m.group("base_url")
        host_port = m.group("host").split(":")
        self.host: str = host_port[0]
        self.port: int = int(host_port[1]) if len(host_port) > 1 else 443 if self.base_url.startswith("https") else 80
        self.application_name: str = m.group("application")
        self.vhost: str = f"/applications/{self.application_name}"
