# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from stripe import Customer, Subscription
from stripe.error import InvalidRequestError
from typing import Dict, Any, Optional

from sub.shared import vendor, utils
from sub.shared.exceptions import IntermittentError, ServerError, EntityNotFoundError
from sub.shared.db import SubHubAccount
from sub.shared.cfg import CFG
from shared.log import get_logger

logger = get_logger()


def create_customer(
    subhub_account: SubHubAccount,
    user_id: str,
    email: str,
    source_token: str,
    origin_system: str,
    display_name: str,
) -> Customer:
    _validate_origin_system(origin_system)
    # First search Stripe to ensure we don't have an unlinked Stripe record
    # already in Stripe
    customer = search_customers(email=email, user_id=user_id)

    # If we have a mis-match on the source_token, overwrite with the
    # new one.
    if customer is not None and customer.default_source != source_token:
        customer = vendor.modify_customer(
            customer_id=customer.id,
            source_token=source_token,
            idempotency_key=utils.get_indempotency_key(),
        )

    # No existing Stripe customer, create one.
    if not customer:
        customer = vendor.create_stripe_customer(
            source_token=source_token,
            email=email,
            userid=user_id,
            name=display_name,
            idempotency_key=utils.get_indempotency_key(),
        )
    # Link the Stripe customer to the origin system id
    db_account = subhub_account.new_user(
        uid=user_id, origin_system=origin_system, cust_id=customer.id
    )

    new_user = subhub_account.save_user(db_account)
    if not new_user:
        # Clean-up the Stripe customer record since we can't link it
        vendor.delete_stripe_customer(customer_id=customer.id)
        logger.error("unable to save user or link it")
        raise IntermittentError("error saving db record")

    logger.debug("create customer", customer=customer)
    return customer


def search_customers(email: str, user_id: str) -> Optional[Customer]:
    """
    Locate Stripe Customer by email
    If a Customer is found:
        If the userid in the metadata does not match the user_id provided
            :raise ServerError
        Else
            :return Customer
    Else:
        :return None

    :param email:
    :param user_id:
    :return:
    """
    customers = vendor.get_customer_list(email=email)
    for possible_customer in customers.data:
        if possible_customer.email == email:
            # If the userid doesn't match, the system is damaged.
            if possible_customer.metadata.get("userid") != user_id:
                customer_message = "customer email exists but userid mismatch"
                raise ServerError(customer_message)

            return possible_customer
    return None


def existing_or_new_customer(
    subhub_account: SubHubAccount,
    user_id: str,
    email: str,
    source_token: str,
    origin_system: str,
    display_name: str,
) -> Customer:
    _validate_origin_system(origin_system)
    customer = fetch_customer(subhub_account, user_id)
    logger.debug("fetch customer", customer=customer)
    if not customer:
        return create_customer(
            subhub_account, user_id, email, source_token, origin_system, display_name
        )
    return existing_payment_source(customer, source_token)


def fetch_customer(subhub_account: SubHubAccount, user_id: str) -> Customer:
    customer = None
    db_account = subhub_account.get_user(user_id)
    if db_account:
        customer = vendor.retrieve_stripe_customer(customer_id=db_account.cust_id)
    logger.debug("fetch customer", customer=customer)
    return customer


def find_customer(subhub_account: SubHubAccount, user_id: str) -> Customer:
    """
    Find Customer by user_id
    If user is not found or is deleted:
        :raise EntityNotFoundError
    :param subhub_account:
    :param user_id:
    :return:
    """
    try:
        customer = fetch_customer(subhub_account, user_id)
    except InvalidRequestError as e:
        customer = None
        if e.http_status != 404:
            raise e

    if customer is None or customer.get("deleted"):
        raise EntityNotFoundError(message="Customer not found", error_number=4000)
    return customer


def find_customer_subscription(customer: Customer, sub_id: str) -> Dict[str, Any]:
    """
    Locate a Customer's Subscription by ID
    If the Customer object does not contain the subscription
        :raise EntityNotFoundError
    :param customer:
    :param sub_id:
    :return:
    """
    subscription = next(
        (sub for sub in customer["subscriptions"]["data"] if sub["id"] == sub_id), None
    )
    if subscription is None:
        raise EntityNotFoundError("Subscription not found", error_number=4001)
    return subscription


def existing_payment_source(existing_customer: Customer, source_token: str) -> Customer:
    """
    If Customer does not have an existing Payment Source and has not been Deleted:
        - Set the Customer's payment source to the new token
        - return the updated Customer
    Else
        - return the provided customer
    :param existing_customer:
    :param source_token:
    :return:
    """
    if not existing_customer.get("sources"):
        if not existing_customer.get("deleted"):
            existing_customer = vendor.modify_customer(
                customer_id=existing_customer["id"],
                source_token=source_token,
                idempotency_key=utils.get_indempotency_key(),
            )
            logger.info("add source", existing_customer=existing_customer)
        else:
            logger.info("stripe customer is marked as deleted. cannot add source.")
    logger.debug("existing payment source", existing_customer=existing_customer)
    return existing_customer


def subscribe_customer(customer: Customer, plan_id: str) -> Subscription:
    """
    Subscribe Customer to Plan
    :param customer:
    :param plan_id:
    :return: Subscription Object
    """
    sub = vendor.build_stripe_subscription(
        customer.id, plan_id=plan_id, idempotency_key=utils.get_indempotency_key()
    )
    return sub


def has_existing_plan(customer: Dict[str, Any], plan_id: str) -> bool:
    """
    Check if user has the existing plan in an active or trialing state.
    :param customer:
    :param plan_id:
    :return: True if user has existing plan, otherwise False
    """
    if customer.get("subscriptions"):
        for item in customer["subscriptions"]["data"]:
            if item["plan"]["id"] == plan_id and item["status"] in [
                "active",
                "trialing",
            ]:
                return True
    return False


def _validate_origin_system(origin_system: str):
    """
    This function validates a request's origin_system to validate that is permitted.  This
    allows us to ensure that callers are permitted by configuration to interact with this application.
    :param origin_system: The originating system in Mozilla
    """
    if origin_system not in CFG.ALLOWED_ORIGIN_SYSTEMS:
        logger.info("origin systems", origins=CFG.ALLOWED_ORIGIN_SYSTEMS)
        msg = f"origin_system={origin_system} not one of allowed origin system values, please contact a system administrator in the #subscription-platform channel."
        raise InvalidRequestError(message=msg, param=str(origin_system))
