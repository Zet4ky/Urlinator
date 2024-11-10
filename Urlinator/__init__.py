from ._external.bitdefender import BitdefenderClient
from ._external.drweb import DrwebClient
from ._external.kaspersky import KasperskyClient



__all__ = [
    "get_report",
]

def get_report(url: str) -> dict:
    """Gather security report data for the given URL."""
    report = {}
    try:
        report.update(KasperskyClient().gather_data(url))
        #report.update(DrwebClient().gather_data(url))

    except Exception as e:
        report['error'] = str(e)
    return report
