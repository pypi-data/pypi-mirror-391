from typing import Any

from ape_pie import APIClient

from openklant_client._resources.actor import ActorResource
from openklant_client._resources.betrokkene import BetrokkeneResource
from openklant_client._resources.digitaal_adres import DigitaalAdresResource
from openklant_client._resources.interne_taak import InterneTaakResource
from openklant_client._resources.klant_contact import KlantContactResource
from openklant_client._resources.onderwerp_object import OnderwerpObjectResource
from openklant_client._resources.partij import PartijResource
from openklant_client._resources.partij_identificator import PartijIdentificatorResource


class OpenKlantClient(APIClient):
    partij: PartijResource
    partij_identificator: PartijIdentificatorResource
    digitaal_adres: DigitaalAdresResource
    klant_contact: KlantContactResource
    onderwerp_object: OnderwerpObjectResource
    actor: ActorResource
    interne_taak: InterneTaakResource
    betrokkene: BetrokkeneResource

    def __init__(
        self,
        base_url: str,
        *,
        token: str,
        request_kwargs: dict[str, Any] | None = None,
    ):
        if request_kwargs is None:
            request_kwargs = {}
        if "headers" not in request_kwargs:
            request_kwargs["headers"] = {}
        request_kwargs["headers"]["Authorization"] = f"Token {token}"

        super().__init__(base_url=base_url, request_kwargs=request_kwargs)

        self.partij = PartijResource(self)
        self.partij_identificator = PartijIdentificatorResource(self)
        self.digitaal_adres = DigitaalAdresResource(self)
        self.klant_contact = KlantContactResource(self)
        self.onderwerp_object = OnderwerpObjectResource(self)
        self.actor = ActorResource(self)
        self.interne_taak = InterneTaakResource(self)
        self.betrokkene = BetrokkeneResource(self)
