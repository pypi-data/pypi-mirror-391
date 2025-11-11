from typing import List


class FastDfsConf:
    def __init__(self, tracker_servers: str|List[str], connect_timeout: int = 6,
                 network_timeout: int = 6, store_path_index = -1):
        if not tracker_servers or (isinstance(tracker_servers, str) and str(tracker_servers).strip() == ""):
            raise ValueError('fastdfs.tracker_servers is required')
        if isinstance(tracker_servers, str):
            self.tracker_servers: List[str] = tracker_servers.split(',')
        else:
            self.tracker_servers = tracker_servers
        if not connect_timeout:
            connect_timeout = 6
        self.connect_timeout = connect_timeout
        if not network_timeout:
            network_timeout = 6
        self.network_timeout = network_timeout
        if store_path_index < -1 or store_path_index > 255:
            raise ValueError('fastdfs.store_path_index must be between -1 and 255')
        self.store_path_index = store_path_index