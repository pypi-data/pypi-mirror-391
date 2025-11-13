# Accounts

Types:

```python
from itellicoai.types import (
    Account,
    ConversationDirection,
    ConversationStatus,
    ConversationType,
    AccountListConversationsResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}/conversations">client.accounts.<a href="./src/itellicoai/resources/accounts/accounts.py">list_conversations</a>(account_id, \*\*<a href="src/itellicoai/types/account_list_conversations_params.py">params</a>) -> <a href="./src/itellicoai/types/account_list_conversations_response.py">AccountListConversationsResponse</a></code>
- <code title="get /v1/accounts/current">client.accounts.<a href="./src/itellicoai/resources/accounts/accounts.py">retrieve_current</a>() -> <a href="./src/itellicoai/types/account.py">Account</a></code>

## Subaccounts

Types:

```python
from itellicoai.types.accounts import SubaccountListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/subaccounts">client.accounts.subaccounts.<a href="./src/itellicoai/resources/accounts/subaccounts.py">create</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/subaccount_create_params.py">params</a>) -> <a href="./src/itellicoai/types/account.py">Account</a></code>
- <code title="get /v1/accounts/{account_id}/subaccounts/{subaccount_id}">client.accounts.subaccounts.<a href="./src/itellicoai/resources/accounts/subaccounts.py">retrieve</a>(subaccount_id, \*, account_id) -> <a href="./src/itellicoai/types/account.py">Account</a></code>
- <code title="patch /v1/accounts/{account_id}/subaccounts/{subaccount_id}">client.accounts.subaccounts.<a href="./src/itellicoai/resources/accounts/subaccounts.py">update</a>(subaccount_id, \*, account_id, \*\*<a href="src/itellicoai/types/accounts/subaccount_update_params.py">params</a>) -> <a href="./src/itellicoai/types/account.py">Account</a></code>
- <code title="get /v1/accounts/{account_id}/subaccounts">client.accounts.subaccounts.<a href="./src/itellicoai/resources/accounts/subaccounts.py">list</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/subaccount_list_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/subaccount_list_response.py">SubaccountListResponse</a></code>

## Providers

Types:

```python
from itellicoai.types.accounts import (
    ModelCatalogProvider,
    ModelRange,
    ProviderListModelsResponse,
    ProviderListTranscribersResponse,
    ProviderListVoicesResponse,
)
```

Methods:

- <code title="get /v1/accounts/{account_id}/providers/models">client.accounts.providers.<a href="./src/itellicoai/resources/accounts/providers.py">list_models</a>(account_id) -> <a href="./src/itellicoai/types/accounts/provider_list_models_response.py">ProviderListModelsResponse</a></code>
- <code title="get /v1/accounts/{account_id}/providers/transcribers">client.accounts.providers.<a href="./src/itellicoai/resources/accounts/providers.py">list_transcribers</a>(account_id) -> <a href="./src/itellicoai/types/accounts/provider_list_transcribers_response.py">ProviderListTranscribersResponse</a></code>
- <code title="get /v1/accounts/{account_id}/providers/voices">client.accounts.providers.<a href="./src/itellicoai/resources/accounts/providers.py">list_voices</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/provider_list_voices_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/provider_list_voices_response.py">ProviderListVoicesResponse</a></code>

## PhoneNumbers

Types:

```python
from itellicoai.types.accounts import PhoneNumber, PhoneNumberListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/phone-numbers">client.accounts.phone_numbers.<a href="./src/itellicoai/resources/accounts/phone_numbers.py">create</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/phone_number_create_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/phone_number.py">PhoneNumber</a></code>
- <code title="get /v1/accounts/{account_id}/phone-numbers/{phone_number_id}">client.accounts.phone_numbers.<a href="./src/itellicoai/resources/accounts/phone_numbers.py">retrieve</a>(phone_number_id, \*, account_id) -> <a href="./src/itellicoai/types/accounts/phone_number.py">PhoneNumber</a></code>
- <code title="patch /v1/accounts/{account_id}/phone-numbers/{phone_number_id}">client.accounts.phone_numbers.<a href="./src/itellicoai/resources/accounts/phone_numbers.py">update</a>(phone_number_id, \*, account_id, \*\*<a href="src/itellicoai/types/accounts/phone_number_update_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/phone_number.py">PhoneNumber</a></code>
- <code title="get /v1/accounts/{account_id}/phone-numbers">client.accounts.phone_numbers.<a href="./src/itellicoai/resources/accounts/phone_numbers.py">list</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/phone_number_list_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/phone_number_list_response.py">PhoneNumberListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/phone-numbers/{phone_number_id}">client.accounts.phone_numbers.<a href="./src/itellicoai/resources/accounts/phone_numbers.py">delete</a>(phone_number_id, \*, account_id) -> None</code>

## SipTrunks

Types:

```python
from itellicoai.types.accounts import SipTrunk, SipTrunkListResponse
```

Methods:

- <code title="post /v1/accounts/{account_id}/sip-trunks">client.accounts.sip_trunks.<a href="./src/itellicoai/resources/accounts/sip_trunks.py">create</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/sip_trunk_create_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/sip_trunk.py">SipTrunk</a></code>
- <code title="get /v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}">client.accounts.sip_trunks.<a href="./src/itellicoai/resources/accounts/sip_trunks.py">retrieve</a>(sip_trunk_id, \*, account_id) -> <a href="./src/itellicoai/types/accounts/sip_trunk.py">SipTrunk</a></code>
- <code title="patch /v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}">client.accounts.sip_trunks.<a href="./src/itellicoai/resources/accounts/sip_trunks.py">update</a>(sip_trunk_id, \*, account_id, \*\*<a href="src/itellicoai/types/accounts/sip_trunk_update_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/sip_trunk.py">SipTrunk</a></code>
- <code title="get /v1/accounts/{account_id}/sip-trunks">client.accounts.sip_trunks.<a href="./src/itellicoai/resources/accounts/sip_trunks.py">list</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/sip_trunk_list_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/sip_trunk_list_response.py">SipTrunkListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}">client.accounts.sip_trunks.<a href="./src/itellicoai/resources/accounts/sip_trunks.py">delete</a>(sip_trunk_id, \*, account_id) -> None</code>

## Analytics

Types:

```python
from itellicoai.types.accounts import UsageGroupBy, AnalyticsGetUsageResponse
```

Methods:

- <code title="get /v1/accounts/{account_id}/analytics/usage">client.accounts.analytics.<a href="./src/itellicoai/resources/accounts/analytics.py">get_usage</a>(account_id, \*\*<a href="src/itellicoai/types/accounts/analytics_get_usage_params.py">params</a>) -> <a href="./src/itellicoai/types/accounts/analytics_get_usage_response.py">AnalyticsGetUsageResponse</a></code>

# Agents

Types:

```python
from itellicoai.types import (
    AgentResponse,
    AmbientSound,
    AzureTranscriber,
    CaptureSettings,
    DeepgramTranscriber,
    Denoising,
    InactivitySettings,
    InitialMessage,
    InterruptSettings,
    ResponseTiming,
    Volume,
    AgentListResponse,
)
```

Methods:

- <code title="post /v1/accounts/{account_id}/agents">client.agents.<a href="./src/itellicoai/resources/agents.py">create</a>(account_id, \*\*<a href="src/itellicoai/types/agent_create_params.py">params</a>) -> <a href="./src/itellicoai/types/agent_response.py">AgentResponse</a></code>
- <code title="get /v1/accounts/{account_id}/agents/{agent_id}">client.agents.<a href="./src/itellicoai/resources/agents.py">retrieve</a>(agent_id, \*, account_id) -> <a href="./src/itellicoai/types/agent_response.py">AgentResponse</a></code>
- <code title="patch /v1/accounts/{account_id}/agents/{agent_id}">client.agents.<a href="./src/itellicoai/resources/agents.py">update</a>(agent_id, \*, account_id, \*\*<a href="src/itellicoai/types/agent_update_params.py">params</a>) -> <a href="./src/itellicoai/types/agent_response.py">AgentResponse</a></code>
- <code title="get /v1/accounts/{account_id}/agents">client.agents.<a href="./src/itellicoai/resources/agents.py">list</a>(account_id, \*\*<a href="src/itellicoai/types/agent_list_params.py">params</a>) -> <a href="./src/itellicoai/types/agent_list_response.py">AgentListResponse</a></code>
- <code title="delete /v1/accounts/{account_id}/agents/{agent_id}">client.agents.<a href="./src/itellicoai/resources/agents.py">archive</a>(agent_id, \*, account_id) -> None</code>
