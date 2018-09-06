# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii

from ontology.common.error_code import ErrorCode
from ontology.exception.exception import SDKException
from ontology.smart_contract.neo_contract.abi.abi_info import AbiInfo


class AssetAllocation(object):
    def __init__(self, sdk):
        self.__sdk = sdk
        self.__contract_address = bytearray()
        self.__abi = {
            "functions": [{"name": "create_template", "parameters": [{"name": "rule", "type": ""}], "returntype": ""},
                          {"name": "create_instance",
                           "parameters": [{"name": "template_id", "type": ""}, {"name": "metadata", "type": ""},
                                          {"name": "payments", "type": ""}, {"name": "payer_threshold", "type": ""},
                                          {"name": "payee_threshold", "type": ""}, {"name": "payees", "type": ""},
                                          {"name": "reviewer", "type": ""}], "returntype": ""}, {"name": "input_asset",
                                                                                                 "parameters": [{
                                                                                                     "name": "instance_id",
                                                                                                     "type": ""},
                                                                                                     {
                                                                                                         "name": "amount",
                                                                                                         "type": ""},
                                                                                                     {
                                                                                                         "name": "payer",
                                                                                                         "type": ""}],
                                                                                                 "returntype": ""},
                          {"name": "lock",
                           "parameters": [{"name": "instance_id", "type": ""}, {"name": "lock_time", "type": ""},
                                          {"name": "locker", "type": ""}], "returntype": ""}, {"name": "confirm",
                                                                                               "parameters": [{
                                                                                                   "name": "instance_id",
                                                                                                   "type": ""},
                                                                                                   {
                                                                                                       "name": "confirmer",
                                                                                                       "type": ""}],
                                                                                               "returntype": ""},
                          {"name": "set_quota",
                           "parameters": [{"name": "instance_id", "type": ""}, {"name": "quota", "type": ""}],
                           "returntype": ""}, {"name": "refund", "parameters": [{"name": "instance_id", "type": ""},
                                                                                {"name": "operator", "type": ""}],
                                               "returntype": ""}, {"name": "main",
                                                                   "parameters": [{"name": "operation", "type": ""},
                                                                                  {"name": "args", "type": ""}],
                                                                   "returntype": ""}]}
        self.__update_abi_info()

    def set_contract_address(self, contract_address: str or bytearray or bytes):
        if len(contract_address) == 20:
            if isinstance(contract_address, bytes):
                self.__contract_address = bytearray(contract_address)
                self.__update_abi_info()
            elif isinstance(contract_address, bytearray):
                self.__contract_address = contract_address
                self.__update_abi_info()
            else:
                raise SDKException(ErrorCode.param_err('the data type of the contract address unsupported.'))
        elif isinstance(contract_address, str) and len(contract_address) == 40:
            self.__contract_address = binascii.a2b_hex(contract_address)
            self.__update_abi_info()
        else:
            raise SDKException(ErrorCode.param_err('the length of contract address should be 20 bytes.'))

    def __update_abi_info(self):
        functions = self.__abi['functions']
        try:
            events = self.__abi['events']
        except KeyError:
            events = list()
        self.__abi_info = AbiInfo(self.get_contract_address(is_hex=True), 'main', functions, events)

    def get_contract_address(self, is_hex: bool = True) -> str or bytearray:
        if is_hex:
            array_address = self.__contract_address
            array_address.reverse()
            return binascii.b2a_hex(array_address)
        else:
            return self.__contract_address

    def get_abi(self) -> dict:
        return self.__abi
