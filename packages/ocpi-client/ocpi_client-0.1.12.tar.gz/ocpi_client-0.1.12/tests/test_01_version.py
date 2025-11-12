from ocpi_pydantic.v221.enum import OcpiConnectorTypeEnum, OcpiVersionNumberEnum, OcpiPowerTypeEnum, OcpiTariffTypeEnum, OcpiTariffDimensionTypeEnum, OcpiStatusEnum, OcpiStatusCodeEnum, OcpiSessionStatusEnum
from ocpi_pydantic.v221.versions import OcpiVersion, OcpiVersionsResponse
from pytest_httpx import HTTPXMock
from ocpi_client import OcpiClient
import pytest



class TestVersion:
    @pytest.mark.asyncio
    async def test_get_versions(self, ocpi_client: OcpiClient, httpx_mock: HTTPXMock):
        response_model = OcpiVersionsResponse(
            data=[OcpiVersion(version=OcpiVersionNumberEnum.v221, url='https://api.evo.net/ocpi/v221')],
            status_code=OcpiStatusCodeEnum.SUCCESS,
        )
        httpx_mock.add_response(json=response_model.model_dump(mode='json'))
        versions = await ocpi_client.get_versions()
        assert versions
        assert not ocpi_client.client.is_closed


    # @pytest.mark.asyncio
    # async def test_get_version_details(self, ocpi_client: OcpiClient):
    #     endpoints = await ocpi_client.get_version_details(version=OcpiVersionNumberEnum.v221)
    #     # logger.debug(endpoints)
    #     assert endpoints