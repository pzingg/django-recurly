"""Template tags for working with Recurly.js"""

from django import template
from django.template import Library, Node, Variable, loader

from django_recurly.utils import recurly
from django_recurly.models import Account
from django_recurly.helpers.recurlyjs import get_config, get_subscription_form, get_billing_info_update_form

register = template.Library()


@register.inclusion_tag('django_recurly/base_script.html', takes_context=True)
def recurly_script_block(context, plan_code):
    return {
        'user': context['user'],
        'plan_code': plan_code
    }


@register.simple_tag
def recurly_config():
    return get_config()


@register.simple_tag(takes_context=True)
def subscription_form(context, plan_code, target_element="#recurly-container", protected_params={}, unprotected_params={}):
    from django_recurly.utils import dict_merge

    user = context['user']
    account = None

    if user.is_authenticated():
        try:
            # Grab the recurly account details (could be different from app user details)
            account = user.recurly_account.get().get_account()
        except Account.DoesNotExist:
            # Pre-populate the form fields with user data
            account = recurly.Account(**user._wrapped.__dict__)

        # TODO: (IW) Simplify
        if 'account' in unprotected_params:
            unprotected_params["account"] = dict_merge(account.to_dict(js=True), unprotected_params["account"])
        else:
            unprotected_params["account"] = account.to_dict(js=True)

    return get_subscription_form(plan_code=plan_code, user=user, protected_params=protected_params, unprotected_params=unprotected_params)


@register.simple_tag(takes_context=True)
def billing_info_update_form(context, target_element="#recurly-container", protected_params={}, unprotected_params={}):
    from django_recurly.utils import dict_merge

    user = context['user']
    account = None

    if user.is_authenticated():
        try:
            # Grab the recurly account details (could be different from app user details)
            account = user.recurly_account.get().get_account()
        except Account.DoesNotExist:
            # Pre-populate the form fields with user data
            account = recurly.Account(**user._wrapped.__dict__)

        #TODO: (IW) Simplify
        if 'account' in unprotected_params:
            unprotected_params["account"] = dict_merge(account.to_dict(js=True), unprotected_params["account"])
        else:
            unprotected_params["account"] = account.to_dict(js=True)

    return get_billing_info_update_form(user=user, account=account)


@register.simple_tag(takes_context=True)
def has_active_account(context):
    user = context['user']

    if not user:
        return False

    try:
        user.recurly_account.get().is_active()
    except Account.DoesNotExist:
        return False
