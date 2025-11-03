from dataclasses import dataclass


@dataclass
class CoreConfigurator:
    max_gsq_units: int
    hub_response_timeout: int