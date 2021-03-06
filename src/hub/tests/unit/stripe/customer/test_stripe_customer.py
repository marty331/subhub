# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import time
import json
from unittest import TestCase
from mock import patch

from stripe.util import convert_to_stripe_object
from stripe.error import InvalidRequestError

from hub.vendor.customer import (
    StripeCustomerCreated,
    StripeCustomerDeleted,
    StripeCustomerSourceExpiring,
    StripeCustomerSubscriptionCreated,
    StripeCustomerSubscriptionUpdated,
    StripeCustomerSubscriptionDeleted,
)
from hub.shared.exceptions import ClientError
from hub.shared.db import SubHubDeletedAccountModel


class StripeCustomerCreatedTest(TestCase):
    def setUp(self) -> None:
        fixture_dir = "src/hub/tests/unit/fixtures/"
        with open(f"{fixture_dir}stripe_cust_created_event.json") as fh:
            self.customer_created_event = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_cust_created_event_missing_name.json") as fh:
            self.customer_created_event_missing_name = json.loads(fh.read())

        run_pipeline_patcher = patch("hub.routes.pipeline.RoutesPipeline.run")
        self.addCleanup(run_pipeline_patcher.stop)
        self.mock_run_pipeline = run_pipeline_patcher.start()

    def test_run(self):
        self.mock_run_pipeline.return_value = None
        did_run = StripeCustomerCreated(self.customer_created_event).run()
        assert did_run

    def test_create_payload(self):
        expected_payload = {
            "event_id": "evt_00000000000000",
            "event_type": "customer.created",
            "email": "user123@tester.com",
            "customer_id": "cus_00000000000000",
            "name": "Jon Tester",
            "user_id": "user123",
        }
        actual_payload = StripeCustomerCreated(
            self.customer_created_event
        ).create_payload()

        assert actual_payload == expected_payload

    def test_create_payload_missing_name(self):
        expected_payload = {
            "event_id": "evt_00000000000000",
            "event_type": "customer.created",
            "email": "user123@tester.com",
            "customer_id": "cus_00000000000000",
            "name": "",
            "user_id": "user123",
        }
        actual_payload = StripeCustomerCreated(
            self.customer_created_event_missing_name
        ).create_payload()

        assert actual_payload == expected_payload


class StripeCustomerDeletedTest(TestCase):
    def setUp(self) -> None:
        self.user_id = "user123"
        self.cust_id = "cus_123"
        self.subscription_item = dict(
            current_period_end=1574519675,
            current_period_start=1571841275,
            nickname="Guardian VPN (Monthly)",
            plan_amount=499,
            productId="prod_FvnsFHIfezy3ZI",
            subscription_id="sub_G2qciC6nDf1Hz1",
        )
        self.origin_system = "fxa"

        self.deleted_user = SubHubDeletedAccountModel(
            user_id=self.user_id,
            cust_id=self.cust_id,
            subscription_info=[self.subscription_item],
            origin_system=self.origin_system,
            customer_status="deleted",
        )

        self.deleted_user_no_subscriptions = SubHubDeletedAccountModel(
            user_id=self.user_id,
            cust_id=self.cust_id,
            subscription_info=list(),
            origin_system=self.origin_system,
            customer_status="deleted",
        )
        fixture_dir = "src/hub/tests/unit/fixtures/"
        with open(f"{fixture_dir}stripe_customer_deleted_event.json") as fh:
            self.customer_deleted_event = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_customer_deleted_event_no_metadata.json") as fh:
            self.customer_deleted_event_no_meta = json.loads(fh.read())

        get_deleted_user_patcher = patch("flask.g.subhub_deleted_users.get_user")
        run_pipeline_patcher = patch("hub.routes.pipeline.RoutesPipeline.run")

        self.addCleanup(get_deleted_user_patcher.stop)
        self.addCleanup(run_pipeline_patcher.stop)

        self.mock_get_deleted_user = get_deleted_user_patcher.start()
        self.mock_run_pipeline = run_pipeline_patcher.start()

    def test_run(self):
        self.mock_get_deleted_user.return_value = self.deleted_user
        self.mock_run_pipeline.return_value = None
        did_run = StripeCustomerDeleted(self.customer_deleted_event).run()
        assert did_run

    def test_get_deleted_user(self):
        self.mock_get_deleted_user.return_value = self.deleted_user
        user = StripeCustomerDeleted(self.customer_deleted_event).get_deleted_user()
        assert user == self.deleted_user

    def test_get_deleted_user_no_meta(self):
        self.mock_get_deleted_user.return_value = self.deleted_user
        with self.assertRaises(
            ClientError, msg="subhub_deleted_user could not be fetched - missing keys"
        ):
            StripeCustomerDeleted(
                self.customer_deleted_event_no_meta
            ).get_deleted_user()

    def test_get_deleted_user_not_found(self):
        self.mock_get_deleted_user.return_value = None
        with self.assertRaises(
            ClientError,
            msg=f"subhub_deleted_user is None for customer {self.cust_id} and user {self.user_id}",
        ):
            StripeCustomerDeleted(self.customer_deleted_event).get_deleted_user()

    def test_create_payload(self):
        expected_payload = dict(
            event_id="evt_00000000000000",
            event_type="customer.deleted",
            created=1557511290,
            customer_id=self.cust_id,
            plan_amount=499,
            nickname=[self.subscription_item.get("nickname")],
            subscription_id=f"{self.subscription_item.get('subscription_id')}",
            subscriptionId=f"{self.subscription_item.get('subscription_id')}",
            current_period_end=self.subscription_item.get("current_period_end"),
            current_period_start=self.subscription_item.get("current_period_start"),
            uid=self.user_id,
            eventCreatedAt=1326853478,
            messageCreatedAt=int(time.time()),
            eventId="evt_00000000000000",
        )

        payload = StripeCustomerDeleted(self.customer_deleted_event).create_payload(
            self.deleted_user
        )

        self.assertEqual(payload.keys(), expected_payload.keys())
        if payload["messageCreatedAt"] != expected_payload["messageCreatedAt"]:
            self.assertAlmostEqual(
                payload["messageCreatedAt"],
                expected_payload["messageCreatedAt"],
                delta=10,
            )
            expected_payload["messageCreatedAt"] = payload["messageCreatedAt"]
        self.assertEqual(payload, expected_payload)

    def test_create_payload_no_subscription_data(self):
        expected_payload = dict(
            event_id="evt_00000000000000",
            event_type="customer.deleted",
            created=1557511290,
            customer_id=self.cust_id,
            plan_amount=0,
            nickname=[],
            subscription_id="",
            subscriptionId="",
            current_period_end=None,
            current_period_start=None,
            uid=self.user_id,
            eventCreatedAt=1326853478,
            messageCreatedAt=int(time.time()),
            eventId="evt_00000000000000",
        )

        payload = StripeCustomerDeleted(self.customer_deleted_event).create_payload(
            self.deleted_user_no_subscriptions
        )

        self.assertEqual(payload.keys(), expected_payload.keys())
        if payload["messageCreatedAt"] != expected_payload["messageCreatedAt"]:
            self.assertAlmostEqual(
                payload["messageCreatedAt"],
                expected_payload["messageCreatedAt"],
                delta=10,
            )
            expected_payload["messageCreatedAt"] = payload["messageCreatedAt"]
        self.assertEqual(payload, expected_payload)


class StripeCustomerSourceExpiringTest(TestCase):
    def setUp(self) -> None:
        fixture_dir = "src/hub/tests/unit/fixtures/"
        with open(f"{fixture_dir}stripe_cust_test1.json") as fh:
            cust_test1 = json.loads(fh.read())
        self.customer = convert_to_stripe_object(cust_test1)

        with open(f"{fixture_dir}stripe_sub_test1.json") as fh:
            self.subscription = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_sub_test2.json") as fh:
            self.subscription2 = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_plan_test1.json") as fh:
            self.plan = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_prod_test1.json") as fh:
            prod_test1 = json.loads(fh.read())
        self.product = convert_to_stripe_object(prod_test1)

        with open(f"{fixture_dir}stripe_source_expiring_event.json") as fh:
            self.source_expiring_event = json.loads(fh.read())

        customer_patcher = patch("stripe.Customer.retrieve")
        product_patcher = patch("stripe.Product.retrieve")
        run_pipeline_patcher = patch("hub.routes.pipeline.RoutesPipeline.run")

        self.addCleanup(customer_patcher.stop)
        self.addCleanup(product_patcher.stop)
        self.addCleanup(run_pipeline_patcher.stop)

        self.mock_customer = customer_patcher.start()
        self.mock_product = product_patcher.start()
        self.mock_run_pipeline = run_pipeline_patcher.start()

    def test_run(self):
        self.subscription["plan"] = self.plan
        self.customer.subscriptions["data"].append(self.subscription)
        self.mock_customer.return_value = self.customer
        self.mock_product.return_value = self.product
        self.mock_run_pipeline = None

        did_run = StripeCustomerSourceExpiring(self.source_expiring_event).run()

        assert did_run

    def test_run_no_subscriptions(self):
        self.mock_customer.return_value = self.customer
        self.mock_run_pipeline = None
        did_run = StripeCustomerSourceExpiring(self.source_expiring_event).run()
        assert did_run

    def test_run_customer_not_found(self):
        self.mock_customer.side_effect = InvalidRequestError(
            message="message", param="param"
        )
        self.mock_run_pipeline = None
        with self.assertRaises(InvalidRequestError):
            StripeCustomerSourceExpiring(self.source_expiring_event).run()

    def test_create_payload(self):
        self.subscription["plan"] = self.plan
        self.customer.subscriptions["data"].append(self.subscription2)
        self.customer.subscriptions["data"].append(self.subscription)
        self.mock_product.return_value = self.product

        expected_payload = dict(
            event_id="evt_00000000000000",
            event_type="customer.source.expiring",
            email="test@example.com",
            nickname="Project Guardian (Monthly)",
            customer_id="cus_00000000000000",
            last4="4242",
            brand="Visa",
            exp_month=5,
            exp_year=2019,
        )

        payload = StripeCustomerSourceExpiring(
            self.source_expiring_event
        ).create_payload(self.customer)
        assert payload == expected_payload

    def test_create_payload_no_subscriptions(self):
        self.mock_product.return_value = self.product

        expected_payload = dict(
            event_id="evt_00000000000000",
            event_type="customer.source.expiring",
            email="test@example.com",
            nickname="",
            customer_id="cus_00000000000000",
            last4="4242",
            brand="Visa",
            exp_month=5,
            exp_year=2019,
        )
        payload = StripeCustomerSourceExpiring(
            self.source_expiring_event
        ).create_payload(self.customer)
        assert payload == expected_payload


class StripeCustomerSubscriptionCreatedTest(TestCase):
    def setUp(self) -> None:
        fixture_dir = "src/hub/tests/unit/fixtures/"
        with open(f"{fixture_dir}stripe_cust_test1.json") as fh:
            cust_test1 = json.loads(fh.read())
        self.customer = convert_to_stripe_object(cust_test1)

        with open(f"{fixture_dir}stripe_cust_no_metadata.json") as fh:
            cust_no_metadata = json.loads(fh.read())
        self.customer_missing_user = convert_to_stripe_object(cust_no_metadata)

        with open(f"{fixture_dir}stripe_cust_test1_deleted.json") as fh:
            cust_test1_deleted = json.loads(fh.read())
        self.deleted_customer = convert_to_stripe_object(cust_test1_deleted)

        with open(f"{fixture_dir}stripe_prod_test1.json") as fh:
            prod_test1 = json.loads(fh.read())
        self.product = convert_to_stripe_object(prod_test1)

        with open(f"{fixture_dir}stripe_in_test1.json") as fh:
            invoice_test1 = json.loads(fh.read())
        self.invoice = convert_to_stripe_object(invoice_test1)

        with open(f"{fixture_dir}stripe_ch_test1.json") as fh:
            charge_test1 = json.loads(fh.read())
        self.charge = convert_to_stripe_object(charge_test1)

        with open(f"{fixture_dir}stripe_sub_created_event.json") as fh:
            self.subscription_created_event = json.loads(fh.read())

        customer_patcher = patch("stripe.Customer.retrieve")
        product_patcher = patch("stripe.Product.retrieve")
        invoice_patcher = patch("stripe.Invoice.retrieve")
        preview_invoice_patcher = patch("stripe.Invoice.upcoming")
        charge_patcher = patch("stripe.Charge.retrieve")
        run_pipeline_patcher = patch("hub.routes.pipeline.AllRoutes.run")

        self.addCleanup(customer_patcher.stop)
        self.addCleanup(product_patcher.stop)
        self.addCleanup(invoice_patcher.stop)
        self.addCleanup(preview_invoice_patcher.stop)
        self.addCleanup(charge_patcher.stop)
        self.addCleanup(run_pipeline_patcher.stop)

        self.mock_customer = customer_patcher.start()
        self.mock_product = product_patcher.start()
        self.mock_invoice = invoice_patcher.start()
        self.mock_preview_invoice = preview_invoice_patcher.start()
        self.mock_charge = charge_patcher.start()
        self.mock_run_pipeline = run_pipeline_patcher.start()

    def test_run(self):
        self.mock_customer.return_value = self.customer
        self.mock_invoice.return_value = self.invoice
        self.mock_preview_invoice.return_value = self.invoice
        self.mock_charge.return_value = self.charge
        self.mock_product.return_value = self.product
        self.mock_run_pipeline = None

        did_run = StripeCustomerSubscriptionCreated(
            self.subscription_created_event
        ).run()

        assert did_run

    def test_get_user_id(self):
        self.mock_customer.return_value = self.customer

        expected_user_id = "user123"
        user_id = StripeCustomerSubscriptionCreated(
            self.subscription_created_event
        ).get_user_id("cust_123")

        assert user_id == expected_user_id

    def test_get_user_id_fetch_error(self):
        self.mock_customer.side_effect = InvalidRequestError(
            message="invalid data", param="bad data"
        )

        with self.assertRaises(InvalidRequestError):
            StripeCustomerSubscriptionCreated(
                self.subscription_created_event
            ).get_user_id("cust_123")

    def test_get_user_id_deleted_cust(self):
        self.mock_customer.return_value = self.deleted_customer

        with self.assertRaises(ClientError):
            StripeCustomerSubscriptionCreated(
                self.subscription_created_event
            ).get_user_id("cust_1")

    def test_get_user_id_none_error(self):
        self.mock_customer.return_value = self.customer_missing_user

        with self.assertRaises(ClientError):
            StripeCustomerSubscriptionCreated(
                self.subscription_created_event
            ).get_user_id("cust_123")

    def test_create_payload(self):
        self.mock_invoice.return_value = self.invoice
        self.mock_charge.return_value = self.charge
        self.mock_product.return_value = self.product
        self.mock_preview_invoice.return_value = self.invoice

        user_id = "user123"

        expected_payload = dict(
            event_id="evt_00000000000000",
            event_type="customer.subscription.created",
            uid=user_id,
            active=True,
            subscriptionId="sub_00000000000000",  # required by FxA
            subscription_id="sub_00000000000000",
            productName="Project Guardian",
            productId="prod_test1",
            eventId="evt_00000000000000",  # required by FxA
            eventCreatedAt=1326853478,  # required by FxA
            messageCreatedAt=int(time.time()),  # required by FxA
            invoice_id="in_test123",
            plan_amount=500,
            customer_id="cus_00000000000000",
            nickname="Project Guardian (Monthly)",
            created=1519435009,
            canceled_at=1519680008,
            cancel_at=None,
            cancel_at_period_end=False,
            currency="usd",
            current_period_start=1519435009,
            current_period_end=1521854209,
            next_invoice_date=1555354567,
            invoice_number="3B74E3D0-0001",
            brand="Visa",
            last4="0019",
            charge="ch_test1",
        )

        payload = StripeCustomerSubscriptionCreated(
            self.subscription_created_event
        ).create_payload(user_id)

        self.assertEqual(payload.keys(), expected_payload.keys())
        if payload["messageCreatedAt"] != expected_payload["messageCreatedAt"]:
            self.assertAlmostEqual(
                payload["messageCreatedAt"],
                expected_payload["messageCreatedAt"],
                delta=10,
            )
            expected_payload["messageCreatedAt"] = payload["messageCreatedAt"]
        self.assertEqual(payload, expected_payload)

    def test_create_payload_product_fetch_error(self):
        self.mock_invoice.return_value = self.invoice
        self.mock_charge.return_value = self.charge
        self.mock_product.side_effect = InvalidRequestError(
            message="invalid data", param="bad data"
        )

        with self.assertRaises(InvalidRequestError):
            StripeCustomerSubscriptionCreated(
                self.subscription_created_event
            ).create_payload("cust_123")

    def test_create_payload_invoice_fetch_error(self):
        self.mock_invoice.side_effect = InvalidRequestError(
            message="invalid data", param="bad data"
        )
        self.mock_charge.return_value = self.charge
        self.mock_product.return_value = self.product

        with self.assertRaises(InvalidRequestError):
            StripeCustomerSubscriptionCreated(
                self.subscription_created_event
            ).create_payload("cust_123")

    def test_create_payload_charge_fetch_error(self):
        self.mock_invoice.return_value = self.invoice
        self.mock_charge.side_effect = InvalidRequestError(
            message="invalid data", param="bad data"
        )

        with self.assertRaises(InvalidRequestError):
            StripeCustomerSubscriptionCreated(
                self.subscription_created_event
            ).create_payload("cust_123")


class StripeCustomerSubscriptionDeletedTest(TestCase):
    def setUp(self) -> None:
        fixture_dir = "src/hub/tests/unit/fixtures/"
        with open(f"{fixture_dir}stripe_cust_test1.json") as fh:
            cust_test1 = json.loads(fh.read())
        self.customer = convert_to_stripe_object(cust_test1)

        with open(f"{fixture_dir}stripe_cust_no_metadata.json") as fh:
            cust_no_metadata = json.loads(fh.read())
        self.customer_missing_user = convert_to_stripe_object(cust_no_metadata)

        with open(f"{fixture_dir}stripe_cust_test1_deleted.json") as fh:
            cust_test1_deleted = json.loads(fh.read())
        self.deleted_customer = convert_to_stripe_object(cust_test1_deleted)

        with open(f"{fixture_dir}stripe_sub_deleted_event.json") as fh:
            self.subscription_deleted_event = json.loads(fh.read())

        customer_patcher = patch("stripe.Customer.retrieve")
        run_pipeline_patcher = patch("hub.routes.pipeline.RoutesPipeline.run")

        self.addCleanup(customer_patcher.stop)
        self.addCleanup(run_pipeline_patcher.stop)

        self.mock_customer = customer_patcher.start()
        self.mock_run_pipeline = run_pipeline_patcher.start()

    def test_run(self):
        self.mock_customer.return_value = self.customer
        self.mock_run_pipeline.return_value = None

        did_run = StripeCustomerSubscriptionDeleted(
            self.subscription_deleted_event
        ).run()

        assert did_run

    def test_get_user_id(self):
        self.mock_customer.return_value = self.customer

        expected_user_id = "user123"
        user_id = StripeCustomerSubscriptionDeleted(
            self.subscription_deleted_event
        ).get_user_id("cust_123")

        assert user_id == expected_user_id

    def test_get_user_id_deleted_cust(self):
        self.mock_customer.return_value = self.deleted_customer

        with self.assertRaises(ClientError):
            StripeCustomerSubscriptionDeleted(
                self.subscription_deleted_event
            ).get_user_id("cust_1")

    def test_get_user_id_fetch_error(self):
        self.mock_customer.side_effect = InvalidRequestError(
            message="invalid data", param="bad data"
        )

        with self.assertRaises(InvalidRequestError):
            StripeCustomerSubscriptionDeleted(
                self.subscription_deleted_event
            ).get_user_id("cust_123")

    def test_get_user_id_none_error(self):
        self.mock_customer.return_value = self.customer_missing_user

        with self.assertRaises(ClientError):
            StripeCustomerSubscriptionDeleted(
                self.subscription_deleted_event
            ).get_user_id("cust_123")

    def test_create_payload(self):
        expected_payload = {
            "uid": "user123",
            "active": False,
            "subscriptionId": "sub_00000000000000",
            "productId": "prod_00000000000000",
            "eventId": "evt_00000000000000",
            "eventCreatedAt": 1326853478,
            "messageCreatedAt": int(time.time()),
        }

        actual_payload = StripeCustomerSubscriptionDeleted(
            self.subscription_deleted_event
        ).create_payload("user123")

        self.assertEqual(actual_payload.keys(), expected_payload.keys())
        if actual_payload["messageCreatedAt"] != expected_payload["messageCreatedAt"]:
            self.assertAlmostEqual(
                actual_payload["messageCreatedAt"],
                expected_payload["messageCreatedAt"],
                delta=10,
            )
            expected_payload["messageCreatedAt"] = actual_payload["messageCreatedAt"]
        self.assertEqual(actual_payload, expected_payload)


class StripeCustomerSubscriptionUpdatedTest(TestCase):
    def setUp(self) -> None:
        fixture_dir = "src/hub/tests/unit/fixtures/"
        with open(f"{fixture_dir}stripe_cust_test1.json") as fh:
            cust_test1 = json.loads(fh.read())
        self.customer = convert_to_stripe_object(cust_test1)

        with open(f"{fixture_dir}stripe_cust_no_metadata.json") as fh:
            cust_no_metadata = json.loads(fh.read())
        self.customer_missing_user = convert_to_stripe_object(cust_no_metadata)

        with open(f"{fixture_dir}stripe_cust_test1_deleted.json") as fh:
            cust_test1_deleted = json.loads(fh.read())
        self.deleted_customer = convert_to_stripe_object(cust_test1_deleted)

        with open(f"{fixture_dir}stripe_prod_test1.json") as fh:
            prod_test1 = json.loads(fh.read())
        self.product = convert_to_stripe_object(prod_test1)

        with open(f"{fixture_dir}stripe_prod_bad_test1.json") as fh:
            bad_prod_test1 = json.loads(fh.read())
        self.bad_product = convert_to_stripe_object(bad_prod_test1)

        with open(f"{fixture_dir}stripe_in_test1.json") as fh:
            invoice_test1 = json.loads(fh.read())
        self.invoice = convert_to_stripe_object(invoice_test1)

        with open(f"{fixture_dir}stripe_in_test2.json") as fh:
            invoice_test2 = json.loads(fh.read())
        self.incomplete_invoice = convert_to_stripe_object(invoice_test2)

        with open(f"{fixture_dir}stripe_ch_test1.json") as fh:
            charge_test1 = json.loads(fh.read())
        self.charge = convert_to_stripe_object(charge_test1)

        with open(f"{fixture_dir}stripe_ch_test2.json") as fh:
            charge_test2 = json.loads(fh.read())
        self.incomplete_charge = convert_to_stripe_object(charge_test2)

        with open(f"{fixture_dir}stripe_sub_updated_event_cancel.json") as fh:
            self.subscription_cancelled_event = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_sub_updated_event_charge.json") as fh:
            self.subscription_charge_event = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_sub_updated_event_reactivate.json") as fh:
            self.subscription_reactivate_event = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_sub_updated_event_change.json") as fh:
            self.subscription_change_event = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_sub_updated_event_no_trigger.json") as fh:
            self.subscription_updated_event_no_match = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_previous_plan1.json") as fh:
            self.previous_plan = json.loads(fh.read())

        with open(f"{fixture_dir}valid_plan_response.json") as fh:
            self.plan_list = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_prod_test2.json") as fh:
            self.new_product = json.loads(fh.read())

        with open(f"{fixture_dir}stripe_in_test2.json") as fh:
            self.upcoming_invoice = json.loads(fh.read())

        customer_patcher = patch("stripe.Customer.retrieve")
        product_patcher = patch("stripe.Product.retrieve")
        invoice_patcher = patch("stripe.Invoice.retrieve")
        charge_patcher = patch("stripe.Charge.retrieve")
        plan_retrieve_patcher = patch("stripe.Plan.retrieve")
        upcoming_invoice_patcher = patch("stripe.Invoice.upcoming")
        run_pipeline_patcher = patch("hub.routes.pipeline.RoutesPipeline.run")

        self.addCleanup(customer_patcher.stop)
        self.addCleanup(product_patcher.stop)
        self.addCleanup(invoice_patcher.stop)
        self.addCleanup(upcoming_invoice_patcher.stop)
        self.addCleanup(plan_retrieve_patcher.stop)
        self.addCleanup(charge_patcher.stop)
        self.addCleanup(run_pipeline_patcher.stop)

        self.mock_customer = customer_patcher.start()
        self.mock_product = product_patcher.start()
        self.mock_invoice = invoice_patcher.start()
        self.mock_upcoming_invoice = upcoming_invoice_patcher.start()
        self.mock_plan_retrieve = plan_retrieve_patcher.start()
        self.mock_charge = charge_patcher.start()
        self.mock_run_pipeline = run_pipeline_patcher.start()

    def test_run_cancel(self):
        self.mock_customer.return_value = self.customer
        self.mock_product.return_value = self.product
        self.mock_run_pipeline.return_value = None

        did_route = StripeCustomerSubscriptionUpdated(
            self.subscription_cancelled_event
        ).run()
        assert did_route

    def test_run_charge(self):
        self.mock_customer.return_value = self.customer
        self.mock_product.return_value = self.product
        self.mock_invoice.return_value = self.invoice
        self.mock_upcoming_invoice.return_value = self.invoice
        self.mock_charge.return_value = self.charge
        self.mock_run_pipeline.return_value = None
        self.mock_upcoming_invoice.return_value = self.upcoming_invoice

        did_route = StripeCustomerSubscriptionUpdated(
            self.subscription_charge_event
        ).run()
        assert did_route

    def test_run_reactivate(self):
        self.mock_customer.return_value = self.customer
        self.mock_product.return_value = self.product
        self.mock_invoice.return_value = self.invoice
        self.mock_charge.return_value = self.charge
        self.mock_run_pipeline.return_value = None

        did_route = StripeCustomerSubscriptionUpdated(
            self.subscription_reactivate_event
        ).run()
        assert did_route

    def test_run_no_action(self):
        self.mock_customer.return_value = self.customer

        did_route = StripeCustomerSubscriptionUpdated(
            self.subscription_updated_event_no_match
        ).run()
        assert did_route is False

    def test_get_user_id_missing(self):
        self.mock_customer.return_value = self.customer_missing_user

        with self.assertRaises(ClientError):
            StripeCustomerSubscriptionUpdated(
                self.subscription_updated_event_no_match
            ).get_user_id("cust_123")

    def test_get_user_id_fetch_error(self):
        self.mock_customer.side_effect = InvalidRequestError(
            message="invalid data", param="bad data"
        )

        with self.assertRaises(InvalidRequestError):
            StripeCustomerSubscriptionUpdated(
                self.subscription_updated_event_no_match
            ).get_user_id("cust_123")

    def test_get_user_id_deleted_cust(self):
        self.mock_customer.return_value = self.deleted_customer

        with self.assertRaises(ClientError):
            StripeCustomerSubscriptionUpdated(
                self.subscription_updated_event_no_match
            ).get_user_id("cust_1")

    def test_create_payload_error(self):
        self.mock_product.side_effect = InvalidRequestError(
            message="invalid data", param="bad data"
        )

        with self.assertRaises(InvalidRequestError):
            StripeCustomerSubscriptionUpdated(
                self.subscription_updated_event_no_match
            ).create_payload(
                event_type="event.type", user_id="user_123", previous_plan=None
            )

    def test_create_payload_cancelled(self):
        self.mock_product.return_value = self.product

        user_id = "user123"
        event_name = "customer.subscription_cancelled"

        expected_payload = dict(
            event_id="evt_1FXDCFJNcmPzuWtRrogbWpRZ",
            event_type=event_name,
            uid=user_id,
            customer_id="cus_FCUzOhOp9iutWa",
            subscription_id="sub_FCUzkHmNY3Mbj1",
            plan_amount=100,
            nickname="Project Guardian (Daily)",
            canceled_at=None,
            cancel_at=None,
            cancel_at_period_end=True,
            current_period_start=1571949971,
            current_period_end=1572036371,
            invoice_id="in_1FXDCFJNcmPzuWtRT9U5Xvcz",
        )

        actual_payload = StripeCustomerSubscriptionUpdated(
            self.subscription_cancelled_event
        ).create_payload(event_type=event_name, user_id=user_id, previous_plan=None)

        assert actual_payload == expected_payload

    def test_create_payload_recurring_charge(self):
        self.mock_product.return_value = self.product
        self.mock_invoice.return_value = self.invoice
        self.mock_charge.return_value = self.charge
        self.mock_upcoming_invoice.return_value = self.upcoming_invoice

        user_id = "user123"
        event_name = "customer.recurring_charge"

        expected_payload = dict(
            event_id="evt_1FXDCFJNcmPzuWtRrogbWpRZ",
            event_type=event_name,
            uid=user_id,
            customer_id="cus_FCUzOhOp9iutWa",
            subscription_id="sub_FCUzkHmNY3Mbj1",
            plan_amount=100,
            nickname="Project Guardian (Daily)",
            canceled_at=None,
            cancel_at=None,
            cancel_at_period_end=False,
            current_period_start=1571949971,
            current_period_end=1572036371,
            next_invoice_date=1555354567,
            invoice_id="in_1FXDCFJNcmPzuWtRT9U5Xvcz",
            active=True,
            subscriptionId="sub_FCUzkHmNY3Mbj1",  # required by FxA
            productName="Project Guardian",
            eventCreatedAt=1571949975,  # required by FxA
            messageCreatedAt=int(time.time()),  # required by FxA
            created=1559767571,
            eventId="evt_1FXDCFJNcmPzuWtRrogbWpRZ",  # required by FxA
            currency="usd",
            invoice_number="3B74E3D0-0001",
            brand="Visa",
            last4="0019",
            charge="ch_test1",
            proration_amount=1000,
            total_amount=1499,
        )

        actual_payload = StripeCustomerSubscriptionUpdated(
            self.subscription_charge_event
        ).create_payload(event_type=event_name, user_id=user_id, previous_plan=None)

        assert actual_payload == expected_payload

    def test_create_payload_reactivated(self):
        self.mock_product.return_value = self.product
        self.mock_invoice.return_value = self.invoice
        self.mock_charge.return_value = self.charge

        user_id = "user123"
        event_name = "customer.subscription.reactivated"

        expected_payload = dict(
            event_id="evt_1FXDCFJNcmPzuWtRrogbWpRZ",
            event_type=event_name,
            uid=user_id,
            customer_id="cus_FCUzOhOp9iutWa",
            subscription_id="sub_FCUzkHmNY3Mbj1",
            plan_amount=100,
            nickname="Project Guardian (Daily)",
            close_date=1571949975,
            current_period_end=1572036371,
            brand="Visa",
            last4="0019",
        )

        actual_payload = StripeCustomerSubscriptionUpdated(
            self.subscription_reactivate_event
        ).create_payload(event_type=event_name, user_id=user_id, previous_plan=None)

        assert actual_payload == expected_payload

    def test_get_subscription_change(self):
        self.mock_customer.return_value = self.product
        self.mock_invoice.return_value = self.invoice
        self.mock_upcoming_invoice.return_value = self.upcoming_invoice
        self.mock_product.return_value = self.product
        self.mock_plan_retrieve.return_value = self.previous_plan

        expected_sub_change = dict(
            close_date=1571949975,
            nickname_old="Previous Product (Monthly)",
            nickname_new="Test Plan Original",
            event_type="customer.subscription.upgrade",
            plan_amount_old=499,
            plan_amount_new=999,
            proration_amount=1000,
            current_period_end=1572036371,
            invoice_number="3B74E3D0-0001",
            invoice_id="in_test1",
            interval="month",
        )

        payload = dict(
            event_id="evt_change_test",
            event_type="customer.subscription.updated",
            uid=None,
            customer_id="cus_123",
            subscription_id="sub_123",
            plan_amount=999,
            nickname="Test Plan Original",
        )

        actual_sub_change = StripeCustomerSubscriptionUpdated(
            self.subscription_change_event
        ).get_subscription_change(
            payload=payload,
            previous_plan=self.previous_plan,
            new_product=self.new_product,
        )
        assert expected_sub_change == actual_sub_change
