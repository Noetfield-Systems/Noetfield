"""Offline policy fixtures; never contact real recipients."""
import unittest
from dataclasses import replace
from noetfield_governance.communication_policy import (
    Identity, Relationship, resolve, enforce_envelope, corporate_sender, CommunicationRejected,
)

class CommunicationPolicyTests(unittest.TestCase):
    def setUp(self):
        self.rel = Relationship("venture-a","entity-a","buyer@example.org",
            "native:contact:1","native-crm","owner","review reply",context_checked=True)
        self.native = Identity("native@example.org","entity-a","venture-a",
            frozenset({"technical","commercial","research","customer_support"}),
            "native","native@example.org",True,True,"provider:verified")
        self.specialist = replace(self.native,address="tech@example.org",kind="specialist")
    def route(self,rel=None,identities=None,intent="technical",authority="standing:1"):
        return resolve(venture="venture-a",entity="entity-a",intent=intent,
            relationship=rel or self.rel,identities=identities or (self.native,self.specialist),
            authority_ref=authority)
    def test_native(self):
        self.assertEqual(self.route(),self.native)
    def test_existing_thread(self):
        self.assertEqual(self.route(replace(self.rel,thread_sender=self.specialist.address)),self.specialist)
    def test_authorized_fallback(self):
        self.assertEqual(self.route(identities=(replace(self.native,available=False),self.specialist)),self.specialist)
    def test_cross_venture(self):
        with self.assertRaises(CommunicationRejected):
            self.route(identities=(replace(self.native,venture="other"),))
    def test_unverified_alias(self):
        with self.assertRaises(CommunicationRejected):
            self.route(identities=(replace(self.native,verified=False),))
    def test_no_default_sender(self):
        with self.assertRaises(CommunicationRejected):
            self.route(identities=(replace(self.native,authority_ref=""),))
    def test_duplicate(self):
        with self.assertRaises(CommunicationRejected):
            self.route(replace(self.rel,prior_attempt=True))
    def test_optout(self):
        with self.assertRaises(CommunicationRejected):
            self.route(replace(self.rel,suppressed=True))
    def test_missing_context(self):
        with self.assertRaises(CommunicationRejected):
            self.route(replace(self.rel,context_checked=False))
    def test_wrong_entity(self):
        with self.assertRaises(CommunicationRejected):
            self.route(replace(self.rel,entity="other"))
    def test_missing_standing_authority(self):
        with self.assertRaises(CommunicationRejected):
            self.route(authority="")
    def test_wrong_envelope(self):
        with self.assertRaises(CommunicationRejected):
            enforce_envelope(identity=self.native,sender="wrong@example.org",
                recipient=self.rel.recipient,reply_to=self.native.reply_to,relationship=self.rel)
    def test_corporate_transport_boundary(self):
        self.assertEqual(corporate_sender("operations@noetfield.com"),"operations@noetfield.com")
        for address in ("","hello@trustfield.ca","unknown@noetfield.com"):
            with self.assertRaises(CommunicationRejected):
                corporate_sender(address)
