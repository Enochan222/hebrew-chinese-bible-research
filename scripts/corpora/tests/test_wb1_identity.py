#!/usr/bin/env python3
from __future__ import annotations

import unittest

from scripts.corpora.load_wb1_postgres import stable_uuid


class WB1StableIdentityRegression(unittest.TestCase):
    def test_wb1_preserves_accepted_wb0_uuid_identities(self):
        self.assertEqual(
            stable_uuid("reference-span","1Sam",16,7),
            "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
        )
        self.assertEqual(
            stable_uuid("annotation-layer","OSHB_MORPHHB","MORPHOLOGY"),
            "de8e8f74-c7fe-50ca-9c0d-4716a01d7657",
        )
        self.assertEqual(
            stable_uuid("annotation-layer","BHSA_2021","WB0_WORD_PHRASE_CLAUSE"),
            "d59aeef3-2f5c-5d07-b0da-26a6dec58219",
        )


if __name__=="__main__":
    unittest.main()
