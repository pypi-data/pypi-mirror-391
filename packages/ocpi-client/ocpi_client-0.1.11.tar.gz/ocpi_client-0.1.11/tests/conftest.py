import logging
from sys import stderr, stdout

import httpx
import loguru
from ocpi_pydantic.v221.enum import OcpiModuleIdEnum, OcpiInterfaceRoleEnum, OcpiConnectorTypeEnum, OcpiTokenTypeEnum, OcpiWhitelistTypeEnum, OcpiConnectorFormatEnum, OcpiPowerTypeEnum, OcpiCdrDimensionTypeEnum, OcpiSessionStatusEnum, OcpiTariffDimensionTypeEnum, OcpiTariffTypeEnum, OcpiDayOfWeekEnum, OcpiStatusCodeEnum, OcpiPartyRoleEnum
from ocpi_pydantic.v221.versions import OcpiEndpoint
from ocpi_client.models import OcpiParty
import pytest_asyncio

from ocpi_client import OcpiClient



_FROM_COUNTRY_CODE = 'TW'
_FROM_PARTY_ID = 'WNC'



@pytest_asyncio.fixture
async def party_fixture():
    return OcpiParty(
        country_code='TW',
        party_id='EVO',
        party_roles=[OcpiPartyRoleEnum.EMSP, OcpiPartyRoleEnum.CPO],
        versions_url='https://api.evo.net/ocpi/versions',
        credentials_token_for_receiving_request_from_party='aaa',

        credentials_token_for_sending_register_to_party='bbb',
        credentials_token_for_sending_request_to_party='ccc',
        
        v221_endpoints=[
            OcpiEndpoint(identifier=OcpiModuleIdEnum.credentials, role=OcpiInterfaceRoleEnum.RECEIVER, url='https://api.evo.net/ocpi/v221/credentials'),
            OcpiEndpoint(identifier=OcpiModuleIdEnum.credentials, role=OcpiInterfaceRoleEnum.SENDER, url='https://api.evo.net/ocpi/v221/credentials'),
        ],
    )



@pytest_asyncio.fixture
async def logger_fixture():
    _format = ''.join([
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | ',
        '<level>{level: <8}</level> | ',
        '<magenta>{process.name}</magenta>:<yellow>{thread.name}</yellow> | ',
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    ])
    logger = loguru.logger
    logger.remove() # Remove pre-configured STDERR hanlder
    logger.add(stdout, level=logging.DEBUG, format=_format)
    logger.add(stderr, level=logging.WARNING, format=_format)
    return logger



@pytest_asyncio.fixture
async def ocpi_client(party_fixture: OcpiParty, logger_fixture: logging.Logger):
    return OcpiClient(
        httpx_async_client=httpx.AsyncClient(),
        from_country_code=_FROM_COUNTRY_CODE,
        from_party_id=_FROM_PARTY_ID,
        to_party=party_fixture,
        logger=logger_fixture,
    )