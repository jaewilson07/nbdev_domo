# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/80_DomoAccount.ipynb.

# %% auto 0
__all__ = ['get_accounts', 'get_account_from_id', 'get_account_config', 'update_account_config', 'update_account_name',
           'create_account_route', 'delete_account_route', 'DomoAccount_Config',
           'DomoAccount_Config_Athena_HighBandwidthConnector', 'DomoAccount_Config_AbstractCredential',
           'DomoAccount_Config_DomoGovernance', 'AccountConfig', 'DomoAccount', 'InvalidAccountError',
           'InvalidAccountConfigError', 'UpdateAccountConfigError', 'DeleteAccountError']

# %% ../nbs/80_DomoAccount.ipynb 3
from typing import Optional, Union
from enum import Enum
from abc import ABC, abstractmethod, abstractclassmethod
from dataclasses import dataclass, field


import datetime as dt
import re

import aiohttp

from fastcore.basics import patch_to
from fastcore.test import test_eq

import nbdev_domo.utils as utils
import nbdev_domo.ResponseGetData as rgd
import nbdev_domo.Transport as tr
import nbdev_domo.DomoAuth as dmda
import nbdev_domo.Logger as lg


# %% ../nbs/80_DomoAccount.ipynb 4
ACCOUNT_ID = 5
ACCOUNT_DATA_PROVIDER_TYPE = "domo-governance-d14c2fef-49a8-4898-8ddd-f64998005600"

# %% ../nbs/80_DomoAccount.ipynb 6
async def get_accounts(
    full_auth: dmda.DomoAuth,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> rgd.ResponseGetData:
    """retrieves a list of all accounts this auth has read access to."""

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts"

    if debug:
        print(url)

    domo_transport = tr.TransportAsync(
        auth_header=await full_auth.generate_auth_header(), session=session
    )

    return await domo_transport.get(url=url)

# %% ../nbs/80_DomoAccount.ipynb 9
async def get_account_from_id(
    account_id: int,
    full_auth: dmda.DomoFullAuth,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> rgd.ResponseGetData:
    """retrieves metadata about an account, does not retrieve configuration settings"""

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}?unmask=true"

    if debug:
        print(url)

    domo_transport = tr.TransportAsync(
        auth_header=await full_auth.generate_auth_header(), session=session
    )

    return await domo_transport.get(url=url)

# %% ../nbs/80_DomoAccount.ipynb 12
async def get_account_config(
    account_id: int,
    data_provider_type: str,
    full_auth: dmda.DomoAuth,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> rgd.ResponseGetData:
    """retrieves account configuration information, does not include metadata"""

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}?unmask=true"

    if debug:
        print(url)

    domo_transport = tr.TransportAsync(
        auth_header=await full_auth.generate_auth_header(), session=session
    )

    return await domo_transport.get(url=url)

# %% ../nbs/80_DomoAccount.ipynb 16
async def update_account_config(
    account_id: int,
    config_body: dict,  # config_body is determined by the data_provider_type
    data_provider_type: str,
    full_auth: dmda.DomoFullAuth,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> rgd.ResponseGetData:
    """updates account configuration.  does not alter metadata"""

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    if debug:
        print(url)

    domo_transport = tr.TransportAsync(
        auth_header=await full_auth.generate_auth_header(), session=session
    )

    return await domo_transport.put(
        url=url, body=config_body, debug=debug, session=session
    )


# %% ../nbs/80_DomoAccount.ipynb 17
async def update_account_name(
    account_id: int,
    account_name: str,
    full_auth: dmda.DomoFullAuth,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> rgd.ResponseGetData:
    """update an account's display name"""

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/name"

    if debug:
        print(url)

    domo_transport = tr.TransportAsync(
        auth_header=await full_auth.generate_auth_header(), session=session
    )

    return await domo_transport.put_text(
        url=url, body=account_name, session=session, debug=debug
    )

# %% ../nbs/80_DomoAccount.ipynb 21
async def create_account_route(
    config_body: dict,  # config body is dependent on data provider type
    full_auth: dmda.DomoFullAuth,  # domo auth
    debug: bool = False,  # for debuggigng
    session: Optional[aiohttp.ClientSession] = None,
) -> rgd.ResponseGetData:  # returns account metadata
    """create a new Domo Account object"""

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts"

    if debug:
        print(url)

    domo_transport = tr.TransportAsync(
        auth_header=await full_auth.generate_auth_header(), session=session
    )

    return await domo_transport.post(
        url=url, body=config_body, debug=debug, session=session
    )

# %% ../nbs/80_DomoAccount.ipynb 23
async def delete_account_route(
    account_id: str,
    full_auth: dmda.DomoFullAuth,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> rgd.ResponseGetData:

    url = (
        f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}"
    )

    if debug:
        print(url)

    domo_transport = tr.TransportAsync(
        auth_header=await full_auth.generate_auth_header(), session=session
    )

    return await domo_transport.delete(url=url, debug=debug, session=session)

# %% ../nbs/80_DomoAccount.ipynb 25
class DomoAccount_Config(ABC):
    """
    Abstract method for defining Domo Account Configuration bodies.
    \n 1. Each implementation should have properties unique to the account configuration.
    \n 2. Each implementation should have an internal classmethod for converting an API response to an object
    \n 3. Each implementation should have an internal method for converting the class object into a json object.
    """

    data_provider_type: str

    @abstractclassmethod
    def _from_json(cls, obj):
        pass

    @abstractmethod
    def to_json(self):
        pass

# %% ../nbs/80_DomoAccount.ipynb 27
@dataclass
class DomoAccount_Config_Athena_HighBandwidthConnector(DomoAccount_Config):
    aws_access_key: str
    aws_secret_key: str = field(repr=False)
    s3_staging_dir: str
    region: str = "us-west-2"
    data_provider_type = "amazon-athena-high-bandwidth"

    @classmethod
    def _from_json(cls, obj):

        dd = utils.DictDot(obj)

        return cls(
            aws_access_key=dd.awsAccessKey,
            aws_secret_key=dd.awsSecretKey,
            s3_staging_dir=dd.s3StagingDir,
            region=dd.region,
        )

    def to_json(self):
        return {
            "awsAccessKey": self.aws_access_key,
            "awsSecretKey": self.aws_secret_key,
            "s3StagingDir": self.s3_staging_dir,
            "region": self.region,
        }


@dataclass
class DomoAccount_Config_AbstractCredential(DomoAccount_Config):
    credentials: str  # typically we recommend implementing dictionaries in the body, but the data is actually stored as a string
    data_provider_type: str = "abstract-credential-store"

    @classmethod
    def _from_json(cls, obj):

        dd = utils.DictDot(obj)

        return cls(
            credentials=dd.credentials,
        )

    def to_json(self):
        return {"credentials": self.credentials}


@dataclass
class DomoAccount_Config_DomoGovernance(DomoAccount_Config):
    api_key: str
    customer: str
    data_provider_type: str = "domo-governance"

    @classmethod
    def _from_json(cls, obj):

        dd = utils.DictDot(obj)

        return cls(api_key=dd.apikey, customer=dd.customer)

    def to_json(self):
        return {"apikey": self.api_key, "customer": self.customer}

# %% ../nbs/80_DomoAccount.ipynb 29
class AccountConfig(Enum):
    """enum to match account types with config classes"""

    amazon_athena_high_bandwidth = DomoAccount_Config_Athena_HighBandwidthConnector
    abstract_credential_store = DomoAccount_Config_AbstractCredential
    domo_governance = DomoAccount_Config_DomoGovernance

# %% ../nbs/80_DomoAccount.ipynb 31
@dataclass
class DomoAccount:
    """class for interacting with Domo Account entities"""

    display_name: str
    data_provider_type: str
    id: int = None

    created_dt: Optional[dt.datetime] = None
    modified_dt: Optional[dt.datetime] = None
    full_auth: dmda.DomoFullAuth = field(repr=False, default=None)

    config: Optional[AccountConfig] = None
    logger: Optional[lg.Logger] = None

    def __post_init__(self):
        if not self.logger:
            self.logger = lg.Logger(app_name="default_domo_account")

    @classmethod
    def _from_json(
        cls,
        obj: dict,
        full_auth: Optional[dmda.DomoFullAuth] = None,
        logger: Optional[lg.Logger] = None,
    ):

        dd = utils.DictDot(obj)

        return cls(
            id=dd.id,
            display_name=dd.displayName,
            data_provider_type=dd.dataProviderType,
            created_dt=utils.convert_epoch_millisecond_to_datetime(dd.createdAt),
            modified_dt=utils.convert_epoch_millisecond_to_datetime(dd.modifiedAt),
            full_auth=full_auth,
            logger=logger,
        )

    @staticmethod
    def config_to_json(display_name, data_provider_type, configuration):
        return {
            "displayName": display_name,
            "dataProviderType": data_provider_type,
            "name": data_provider_type,
            "configurations": configuration,
        }

# %% ../nbs/80_DomoAccount.ipynb 32
class InvalidAccountError(dmda.DomoErrror):
    """return invalid account id sent to API"""

    def __init__(
        self,
        status: Optional[int] = None,  # API request status
        message="invalid account",
        domo_instance: Optional[str] = None,
    ):

        super().__init__(status=status, message=message, domo_instance=domo_instance)


# | export


class InvalidAccountConfigError(dmda.DomoErrror):
    """return if DomoAccount does not have a valid config attribute"""

    def __init__(
        self,
        status: Optional[int] = None,  # API request status
        message="invalid account config",
        domo_instance: Optional[str] = None,
    ):

        super().__init__(status=status, message=message, domo_instance=domo_instance)


class UpdateAccountConfigError(dmda.DomoErrror):
    """return if DomoAccount does not have a valid config attribute"""

    def __init__(
        self,
        status: Optional[int] = None,  # API request status
        message="failed to update account config",
        domo_instance: Optional[str] = None,
    ):

        super().__init__(status=status, message=message, domo_instance=domo_instance)


class DeleteAccountError(dmda.DomoErrror):
    """return if fail to delete Domo Account"""

    def __init__(
        self,
        status: Optional[int] = None,  # API request status
        message="failed to delete account",
        domo_instance: Optional[str] = None,
    ):

        super().__init__(status=status, message=message, domo_instance=domo_instance)

# %% ../nbs/80_DomoAccount.ipynb 33
@patch_to(DomoAccount, cls_method=True)
async def get_from_id(
    cls,
    full_auth: dmda.DomoAuth,
    account_id: int,
    session: aiohttp.ClientSession = None,
    logger: Optional[lg.Logger] = None,
    debug: bool = False,
) -> DomoAccount:
    """
    Retrieves account metadata and attempts to retrieve config information.
    \n To retrieve config data, a matching `DomoAccount_Config` class and `AccountConfig` enum entry must exist.
    * The match is an approximate match based on 'startswith'
    """

    account_res = await get_account_from_id(
        full_auth=full_auth, account_id=account_id, session=session
    )

    if debug:
        print(account_res.response)

    message = f"metadata retreived from get_account_from_id: account - {account_id} from {full_auth.domo_instance}"

    if not account_res.is_success:
        message = f"ERROR - no {message}"
        if logger:
            logger.log_error(
                message=message,
                entity_id=account_id,
                domo_instance=full_auth.domo_instance,
            )

        raise InvalidAccountError(
            message=message,
            domo_instance=full_auth.domo_instance,
            status=account_res.status,
        )

    obj = account_res.response
    acc = cls._from_json(obj, full_auth, logger=logger)

    acc.logger.log_info(
        message=f"SUCCESS - {message}",
        entity_id=account_id,
        domo_instance=full_auth.domo_instance,
    )

    # get account config
    config_res = await get_account_config(
        full_auth=full_auth,
        account_id=acc.id,
        data_provider_type=acc.data_provider_type,
        session=session,
    )

    message = f"config data retrieved from get_account_config: data provider - {acc.data_provider_type} - for account -{account_id} in {full_auth.domo_instance}"

    if not config_res.is_success:
        acc.logger.log_warning(
            message=f"WARNING - no {message}",
            entity_id=account_id,
            domo_instance=full_auth.domo_instance,
        )
        return acc

    acc.logger.log_info(
        message=f"SUCCESS - {message}",
        entity_id=account_id,
        domo_instance=full_auth.domo_instance,
    )

    # map account config to AccountConfig enum
    enum_clean = re.sub("-", "_", acc.data_provider_type)

    config_match = next(
        (
            member.value
            for member in AccountConfig
            if enum_clean.startswith(member.name)
        ),
        None,
    )

    if not config_match:
        return acc

    acc.config = config_match._from_json(config_res.response)

    return acc

# %% ../nbs/80_DomoAccount.ipynb 38
@patch_to(DomoAccount)
async def update_config(
    self,
    config_body: Optional[DomoAccount_Config] = None,
    full_auth: dmda.DomoFullAuth = None,
    debug: bool = False,
    session: aiohttp.ClientSession = None,
):
    """update account configuration, does not update metadata"""
    if not config_body and not self.Config:
        raise InvalidAccountConfigError

    full_auth = full_auth or self.full_auth

    update_account_config_res = await update_account_config(
        full_auth=full_auth,
        account_id=self.id,
        data_provider_type=self.data_provider_type,
        config_body=self.config.to_json(),
        debug=debug,
        session=session,
    )

    message = f"account config updated with update_account_config for account - {self.id} in {full_auth.domo_instance}"

    if not update_account_config_res.is_success:
        message = f"FAILURE - no {message}"
        self.logger.log_error(
            message=message, entity_id=self.id, domo_instance=full_auth.domo_instance
        )

        raise UpdateAccountConfigError(
            status=update_account_config_res.status,
            message=message,
            domo_instance=full_auth.domo_instanec,
        )

    return await self.get_from_id(full_auth=full_auth, account_id=self.id)

# %% ../nbs/80_DomoAccount.ipynb 39
@patch_to(DomoAccount)
async def update_name(
    self,
    account_name: str = None,
    full_auth: dmda.DomoFullAuth = None,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
):
    """updates account display name"""

    full_auth = full_auth or self.full_auth

    update_account_name_res = await update_account_name(
        full_auth=full_auth,
        account_id=self.id,
        account_name=account_name or self.name,
        debug=debug,
        session=session,
    )

    message = f"update name for account - {self.id} in {full_auth.domo_instance}"

    if not update_account_name_res.is_success:
        message = f"FAILURE - {message}"
        self.logger.log_error(
            message=message, entity_id=self.id, domo_instance=full_auth.domo_instance
        )

        raise UpdateAccountConfigError(
            status=update_account_name_res.status,
            message=message,
            domo_instance=full_auth.domo_instance,
        )

    self.logger.log_info(
        message=f"SUCCESS - {message}",
        entity_id=self.id,
        domo_instance=full_auth.domo_instance,
    )

    return await self.get_from_id(full_auth=full_auth, account_id=self.id)

# %% ../nbs/80_DomoAccount.ipynb 42
@patch_to(DomoAccount, cls_method=True)
async def create_account(
    cls,
    display_name: str,
    domoaccount_config: DomoAccount_Config,
    full_auth: dmda.DomoFullAuth,
    debug: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> Union[bool, DomoAccount]:

    """create a new Domo Account object"""

    config_body = domoaccount_config.to_json()

    account_body = cls.config_to_json(
        display_name, domoaccount_config.data_provider_type, configuration=config_body
    )

    res = await create_account_route(
        config_body=account_body,
        full_auth=full_auth,
        debug=debug,
        session=session,
    )

    if debug:
        print(res)

    if res.status != 200:
        return False

    account_obj = res.response
    return await cls.get_from_id(full_auth=full_auth, account_id=account_obj.get("id"))


@patch_to(DomoAccount, cls_method=True)
async def delete_account(
    cls,
    account_id: int,
    full_auth: dmda.DomoFullAuth,
    debug: bool = False,
    session: aiohttp.ClientSession = None,
    logger: Optional[lg.Logger] = None,
) -> bool:  # returns True or False if account successfully deleted

    """classmethod to delete an account"""

    res = await delete_account_route(
        full_auth=full_auth,
        account_id=account_id,
        debug=debug,
        session=session,
    )

    if debug:
        print(res)

    message = f"delete account {account_id} from {full_auth.domo_instance}"

    if res.status != 200:
        message = "FAILURE - {message}"

        if logger:
            logger.log_error(
                message=message,
                entity_id=account_id,
                domo_instance=full_auth.domo_instance,
            )

        raise DeleteAccountError(
            status=res.status, message=message, domo_instance=full_auth.domo_instance
        )

    message = "SUCCESS - {message}"

    if logger:
        logger.log_info(
            message=message, entity_id=account_id, domo_instance=full_auth.domo_instance
        )

    return True
