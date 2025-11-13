from ocpi_pydantic.v221.enum import OcpiPartyRoleEnum, OcpiVersionNumberEnum, OcpiPowerTypeEnum, OcpiTariffTypeEnum, OcpiTariffDimensionTypeEnum, OcpiStatusEnum, OcpiStatusCodeEnum, OcpiSessionStatusEnum
from ocpi_pydantic.v221.credentials import OcpiCredentialsResponse, OcpiCredentials, OcpiCredentialsRole
from ocpi_pydantic.v221.locations import OcpiBusinessDetails
import pytest
from pytest_httpx import HTTPXMock

from ocpi_client import OcpiClient



class TestCredential:
    @pytest.mark.asyncio
    async def test_get_credentials(self, ocpi_client: OcpiClient, httpx_mock: HTTPXMock):
        response_model = OcpiCredentialsResponse(
            data=OcpiCredentials(
              token='TOKEN',
              url='https://api.evo.net/ocpi/v221',
              roles=[
                OcpiCredentialsRole(role=OcpiPartyRoleEnum.CPO, business_details=OcpiBusinessDetails(name='EVO'), party_id='EVO', country_code='TW'),
                OcpiCredentialsRole(role=OcpiPartyRoleEnum.EMSP, business_details=OcpiBusinessDetails(name='EVO'), party_id='EVO', country_code='TW'),
              ],
            ),
            status_code=OcpiStatusCodeEnum.SUCCESS,
        )
        httpx_mock.add_response(json=response_model.model_dump(mode='json'))
        credenitals = await ocpi_client.get_credentials(version=OcpiVersionNumberEnum.v221)
        assert credenitals