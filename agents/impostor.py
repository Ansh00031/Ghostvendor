"""Agent 2: Vendor Impostor Agent.
Impersonates third-party client SDKs (Stripe, SendGrid, Auth0, OpenAI)
and channels responses through the Chaos Engine.
"""

from typing import Any, Dict, Optional


class MockResponseObj:
    """Wrapper that can support both dictionary access and attribute access."""
    def __init__(self, data: Any):
        self._data = data
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    setattr(self, k, MockResponseObj(v))
                elif isinstance(v, list):
                    setattr(self, k, [MockResponseObj(x) if isinstance(x, dict) else x for x in v])
                else:
                    setattr(self, k, v)

    def __getitem__(self, item):
        if isinstance(self._data, dict):
            return self._data[item]
        raise TypeError(f"'{type(self._data).__name__}' object is not subscriptable")

    def __contains__(self, item):
        return item in self._data if isinstance(self._data, dict) else False

    def get(self, item, default=None):
        if isinstance(self._data, dict):
            return self._data.get(item, default)
        return default

    def __repr__(self):
        return repr(self._data)


class VendorImpostorFactory:
    """Creates mock client objects that emulate external APIs."""

    @staticmethod
    def create_stripe_client(chaos_engine, baseline_data: Dict[str, Any]):
        class Charges:
            def create(self, **kwargs):
                return chaos_engine.execute(baseline_data)
        
        class MockStripe:
            charges = Charges()
        return MockStripe()

    @staticmethod
    def create_sendgrid_client(chaos_engine, baseline_data: Dict[str, Any]):
        class SendEndpoint:
            def post(self, request_body=None, **kwargs):
                res = chaos_engine.execute(baseline_data)
                return MockResponseObj(res)
        
        class Mail:
            send = SendEndpoint()
            
        class MockSendGrid:
            mail = Mail()
        return MockSendGrid()

    @staticmethod
    def create_auth0_client(chaos_engine, baseline_data: Dict[str, Any]):
        class UsersEndpoint:
            def get(self, token, **kwargs):
                return chaos_engine.execute(baseline_data)
        
        class MockAuth0:
            users = UsersEndpoint()
        return MockAuth0()

    @staticmethod
    def create_openai_client(chaos_engine, baseline_data: Dict[str, Any]):
        class CompletionsEndpoint:
            def create(self, **kwargs):
                res = chaos_engine.execute(baseline_data)
                return MockResponseObj(res)
                
        class ChatEndpoint:
            completions = CompletionsEndpoint()
            
        class MockOpenAI:
            chat = ChatEndpoint()
        return MockOpenAI()

    @classmethod
    def get_client_for_vendor(cls, vendor_name: str, chaos_engine, baseline_data: Dict[str, Any]):
        v = vendor_name.lower()
        if "stripe" in v:
            return cls.create_stripe_client(chaos_engine, baseline_data)
        elif "sendgrid" in v:
            return cls.create_sendgrid_client(chaos_engine, baseline_data)
        elif "auth0" in v:
            return cls.create_auth0_client(chaos_engine, baseline_data)
        elif "openai" in v:
            return cls.create_openai_client(chaos_engine, baseline_data)
        else:
            # Generic client fallback
            class GenericClient:
                def call(self, *args, **kwargs):
                    return chaos_engine.execute(baseline_data)
            return GenericClient()
