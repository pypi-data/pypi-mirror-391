# Hector --- A collection manager.
# Copyright © 2023 Bioneland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Optional

import webauthn
from webauthn.helpers.structs import (
    AuthenticationCredential,
    PublicKeyCredentialDescriptor,
    RegistrationCredential,
)

from bl_hector.domain.administration.entities import (
    Challenge,
    Credential,
    RelyingParty,
    User,
)


def credential_creation_options(
    rp: RelyingParty, user: User, challenge: Challenge
) -> str:
    pcco = webauthn.generate_registration_options(
        rp_id=rp.id,
        rp_name=rp.name,
        user_id=str(user.id),
        user_name=user.name,
        challenge=bytes(challenge),
    )
    return webauthn.options_to_json(pcco)


def parse_credentials(
    data: bytes, challenge: Challenge, rp: RelyingParty, user: User
) -> Optional[Credential]:
    try:
        verification = webauthn.verify_registration_response(
            credential=RegistrationCredential.parse_raw(data),
            expected_challenge=bytes(challenge),
            expected_origin=rp.origin,
            expected_rp_id=rp.id,
        )
        return Credential(
            verification.credential_id, verification.credential_public_key, user.id
        )
    except Exception as exc:
        logging.exception(exc)
        return None


def authentication_options(
    rp: RelyingParty, user: User, credentials: list[Credential], challenge: Challenge
) -> str:
    allowed_credentials = [
        PublicKeyCredentialDescriptor(id=credential.id) for credential in credentials
    ]
    authentication_options = webauthn.generate_authentication_options(
        rp_id=rp.id,
        allow_credentials=allowed_credentials,
        challenge=bytes(challenge),
    )
    return webauthn.options_to_json(authentication_options)


def verify_credentials(
    data: bytes,
    challenge: Challenge,
    rp: RelyingParty,
    user: User,
    credentials: list[Credential],
) -> bool:
    try:
        auth_credential = AuthenticationCredential.parse_raw(data)
    except Exception as exc:
        logging.exception(exc)
        return False

    auth_id = webauthn.base64url_to_bytes(auth_credential.id)
    if not (credential := next((c for c in credentials if c.id == auth_id), None)):
        logging.info("No matching credentials.")
        return False

    webauthn.verify_authentication_response(
        credential=auth_credential,
        expected_challenge=bytes(challenge),
        expected_origin=rp.origin,
        expected_rp_id=rp.id,
        credential_public_key=credential.public_key,
        credential_current_sign_count=0,
    )
    return True
