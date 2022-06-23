from anvil import *
import anvil.server


def get_heartbeat() -> bool:
    """Method which checks if the server is online."""
    try:
        return anvil.server.call('heartbeat')
    except Exception as e:
        print(f"Exception while trying to call heartbeat: {e}")
        show_notification(message="Couldn't connect to server!")

    return False


def show_notification(message: str, style: str = "danger"):
    """Method which shows an error notification."""
    Notification(message,
                 title="Server error",
                 style=style).show()
