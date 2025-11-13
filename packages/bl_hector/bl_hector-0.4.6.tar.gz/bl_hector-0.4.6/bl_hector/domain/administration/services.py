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

import datetime
import secrets
from uuid import uuid4

from .entities import Challenge, User
from .value_objects import ChallengeId, ChallengeValue

SECOND = 1
MINUTE = 60 * SECOND
DEFAULT_LIFE_TIME = 10 * MINUTE


def create_challenge_for(user: User) -> Challenge:
    return Challenge(
        ChallengeId(str(uuid4())),
        ChallengeValue(secrets.token_hex(16)),
        datetime.datetime.now() + datetime.timedelta(minutes=DEFAULT_LIFE_TIME),
        user.id,
    )
