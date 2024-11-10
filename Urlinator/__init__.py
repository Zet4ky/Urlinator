from ._external.bitdefender import BitdefenderClient
from ._external.drweb import DrwebClient  # NOTE:XXX: DrWeb is slow, inaccurate and may throw unexpected errors due to lack of testing



__all__ = [
    "get_report",
]

def get_report(url: str) -> dict:
    """Gather security report data for the given URL."""
    report = {}
    try:
        report.update(BitdefenderClient().gather_data(url))
        report.update(DrwebClient().gather_data(url))

    except Exception as e:
        report['error'] = str(e)
    return report
