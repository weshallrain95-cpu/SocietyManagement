"""First visit as an owner or a customer: a short welcome that remembers their name and answers."""

import pytest

from .conftest import api_for, make_user

pytestmark = pytest.mark.django_db


def test_customer_and_owner_welcome_answers_are_kept_per_mode(db):
    u = make_user("9876500001")
    c = api_for(u)
    assert c.get("/v1/me").json()["profile"] == {}
    r = c.patch(
        "/v1/me",
        {"display_name": "Riya Kapoor", "email": "riya@example.com", "preferred_lang": "mr",
         "profile": {"customer": {"intent": "rent", "move_in": "1-3m", "contact": "whatsapp", "areas": ["a", "b"], "welcomed": True}}},
        format="json",
    )  # fmt: skip
    assert r.status_code == 200, r.content
    me = r.json()
    assert me["display_name"] == "Riya Kapoor" and me["email"] == "riya@example.com" and me["preferred_lang"] == "mr"
    assert me["profile"]["customer"]["intent"] == "rent" and me["profile"]["customer"]["welcomed_at"]
    u.refresh_from_db()
    assert b"riya@example.com" not in bytes(u.email_enc)  # stored encrypted

    r = c.patch("/v1/me", {"profile": {"owner": {"flats": "2-3", "plan": "rent", "welcomed": True}}}, format="json")
    prof = r.json()["profile"]
    assert prof["owner"]["flats"] == "2-3" and prof["customer"]["intent"] == "rent"  # the customer answers stay


@pytest.mark.parametrize("bad", [{"landlord": {}}, {"customer": {"intent": "steal"}}, {"owner": {"religion": "x"}}])
def test_only_known_welcome_answers(db, bad):
    c = api_for(make_user("9876500002"))
    assert c.patch("/v1/me", {"profile": bad}, format="json").status_code == 400
