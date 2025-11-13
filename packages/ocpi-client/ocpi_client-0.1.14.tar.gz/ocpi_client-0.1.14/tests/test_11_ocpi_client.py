from datetime import UTC, datetime
from decimal import Decimal
from http import HTTPStatus

from ocpi_pydantic.v221.cdrs import OcpiCdr
from ocpi_pydantic.v221.commands import OcpiCommandResult, OcpiCommandResultTypeEnum
from ocpi_pydantic.v221.locations.connector import OcpiConnector
from ocpi_pydantic.v221.locations.location import OcpiHours, OcpiLocation, OcpiGeoLocation
from ocpi_pydantic.v221.locations.evse import OcpiEvse
from ocpi_pydantic.v221.sessions import OcpiSession
from ocpi_pydantic.v221.tariffs import OcpiTariff, OcpiTariffElement, OcpiPriceComponent
from ocpi_pydantic.v221.tokens import OcpiToken, OcpiLocationReferences, OcpiAuthorizationInfo, OcpiTokenListResponse
from pytest_httpx import HTTPXMock
from ocpi_client import OcpiClient
import pytest



class TestOcpiClient:
    location: OcpiLocation
    evse: OcpiEvse
    connector: OcpiConnector
    tokens: list[OcpiToken]
    tariff: OcpiTariff
    session: OcpiSession
    cdr: OcpiCdr


    @pytest.mark.asyncio
    async def test_post_command_result(self, ocpi_client: OcpiClient):
        response = await ocpi_client.post_command_result(
            response_url='https://0faa0d3b646847e3bee1e1122193c73d.api.mockbin.io/',
            result=OcpiCommandResult(result=OcpiCommandResultTypeEnum.ACCEPTED),
        )
        assert response
        assert response.status_code == HTTPStatus.OK
        ocpi_client.logger.debug(response)


    # @pytest.mark.asyncio
    # async def test_put_location(self, ocpi_client: OcpiClient, location: OcpiLocation) -> None:
    #     location.coordinates.latitude = '24.878'
    #     location.coordinates.longitude = '121.211'
    #     location.postal_code = '325'
    #     location.city = '桃園市'
    #     location.address = '龍潭區百年路 1 號'
    #     location.opening_times = OcpiHours(twentyfourseven=True)
    #     location.publish = True
    #     TestOcpiClient.location = location

    #     response = await ocpi_client.put_location(location=await TestOcpiClient.location)
    #     assert response


    # @pytest.mark.asyncio
    # async def test_get_location(self, ocpi_client: OcpiClient):
    #     location = await ocpi_client.get_location(location_id=TestOcpiClient.location.id)
    #     assert location
    #     assert location.id == TestOcpiClient.location.id


    # @pytest.mark.asyncio
    # async def test_put_evse(self, ocpi_client: OcpiClient, evse: OcpiEvse, connector: OcpiConnector):
    #     evse.floor_level = '1F'
    #     TestOcpiClient.evse = evse

    #     connector.standard = OcpiConnectorTypeEnum.IEC_62196_T2_COMBO
    #     connector.power_type = OcpiPowerTypeEnum.AC_2_PHASE
    #     connector.max_voltage = 380
    #     connector.max_amperage = 100
    #     TestOcpiClient.connector = connector
        
    #     response = await ocpi_client.put_evse(ocpi_location_id=TestOcpiClient.location.id, ocpi_evse=await TestOcpiClient.evse)
    #     assert response


    # @pytest.mark.asyncio
    # async def test_get_tokens(self, ocpi_client: OcpiClient):
    #     TestOcpiClient.tokens = await ocpi_client.get_tokens()
    #     assert TestOcpiClient.tokens


    # @pytest.mark.asyncio
    # async def test_put_tariff(self, ocpi_client: OcpiClient):
    #     now = datetime.now(UTC).replace(second=0, microsecond=0)
    #     TestOcpiClient.tariff = OcpiTariff(
    #         country_code=_FROM_COUNTRY_CODE,
    #         party_id=_FROM_PARTY_ID,
    #         id=f'TEST{now.strftime("%Y%m%d%H%M%S")}', # TEST20241012234343
    #         currency='TWD',
    #         type=OcpiTariffTypeEnum.PROFILE_FAST,
    #         elements=[OcpiTariffElement(price_components=[OcpiPriceComponent(
    #             type=OcpiTariffDimensionTypeEnum.ENERGY,
    #             price=Decimal('10'),
    #             vat=5,
    #             step_size=1,
    #         )])],
    #         last_updated=now,
    #     )
    #     response = await ocpi_client.put_tariff(tariff=TestOcpiClient.tariff)


    # @pytest.mark.asyncio
    # async def test_get_tariff(self, ocpi_client: OcpiClient):
    #     response = await ocpi_client.get_tariff(tariff_id=TestOcpiClient.tariff.id)
    #     assert response


    # @pytest.mark.asyncio
    # async def test_delete_tariff(self, ocpi_client: OcpiClient):
    #     response = await ocpi_client.delete_tariff(tariff_id=TestOcpiClient.tariff.id)
