#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from ontology.ont_sdk import OntologySdk
from ontology.account.account import Account
from ontology.exception.exception import SDKException
from ontology.crypto.signature_scheme import SignatureScheme

from smart_contract_test.asset_allocation import AssetAllocation

remote_rpc_address = "http://polaris3.ont.io:20336"
local_rpc_address = 'http://localhost:20336'


class TestAssetAllocation(unittest.TestCase):
    def test_init(self):
        sdk = OntologySdk()
        sdk.set_rpc(remote_rpc_address)
        asset_allocation = AssetAllocation(sdk)
        self.assertTrue(isinstance(asset_allocation, AssetAllocation))

    def test_set_contract_address(self):
        sdk = OntologySdk()
        sdk.set_rpc(remote_rpc_address)
        asset_allocation = AssetAllocation(sdk)
        contract_address = ''
        asset_allocation.set_contract_address(contract_address)


if __name__ == '__main__':
    unittest.main()
