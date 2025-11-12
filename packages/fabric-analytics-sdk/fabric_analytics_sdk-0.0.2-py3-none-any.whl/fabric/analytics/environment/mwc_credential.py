from typing import Any

from fabric.analytics.environment.base.credentials import (
    IFabricAnalyticsMWCCredential,
    MwcAccessToken,
    MWCTokenRequestPayloadV1,
    MWCTokenRequestPayloadV2,
)
from fabric.analytics.rest.fabric_client import FabricRestClient


class MWCTokenCredentialV1(IFabricAnalyticsMWCCredential):
    def __init__(
        self,
        payload: MWCTokenRequestPayloadV1,
    ):
        self.payload = payload
        super().__init__()

    def get_mwc_token(
        self,
        **kwargs: Any,
    ) -> MwcAccessToken:
        client = FabricRestClient()
        resp = client.get("powerbi/globalservice/v201606/clusterDetails")
        resp.raise_for_status()

        cluster_url = resp.json()["clusterUrl"]

        resp = FabricRestClient(endpoint=cluster_url).post(
            "metadata/v201606/generatemwctoken",
            data=self.payload.to_json(),
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            raise Exception("failed refresh mwc token!")
        return MwcAccessToken.build_from_json(resp.json())


class MWCTokenCredentialV2(IFabricAnalyticsMWCCredential):
    def __init__(
        self,
        payload: MWCTokenRequestPayloadV2,
    ):
        self.payload = payload
        super().__init__()

    def get_mwc_token(
        self,
        **kwargs: Any,
    ) -> MwcAccessToken:
        client = FabricRestClient()
        resp = client.get("powerbi/globalservice/v201606/clusterDetails")
        resp.raise_for_status()

        cluster_url = resp.json()["clusterUrl"]

        resp = FabricRestClient(endpoint=cluster_url).post(
            "metadata/v201606/generatemwctokenv2",
            data=self.payload.to_json(),
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            raise Exception("failed refresh mwc token!")
        return MwcAccessToken.build_from_json(resp.json())
