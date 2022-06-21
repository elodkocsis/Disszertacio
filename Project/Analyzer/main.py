import signal

from src.server.anvil_server import start_server
from src.utils.signal_handler import signal_handler

if __name__ == '__main__':
    # register signal handling method
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # start_server(uplink_url="ws://localhost:80/_/uplink",
    #              key="server_HMNV5XCTSHFNQS3JRGJYC333-6ES3MVIULUSBJRZV")
    start_server(uplink_url="wss://anvil.works/uplink",
                 key="server_HMNV5XCTSHFNQS3JRGJYC333-6ES3MVIULUSBJRZV")
