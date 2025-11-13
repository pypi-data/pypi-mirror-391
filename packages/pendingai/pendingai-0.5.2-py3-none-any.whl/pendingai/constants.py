#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
from datetime import datetime, tzinfo
from typing import Optional

local_tz: Optional[tzinfo] = datetime.now().astimezone().tzinfo
"""Local timezone info for a system runtime."""
local_tz_name: str = datetime.now().astimezone().tzname() or "UTC"
"""Local timezone name for a system runtime."""


smiles_regex = re.compile(r"^[A-Za-z0-9@\.\+\-\[\]\(\)\=:\#\%\*\$/\\]+$", re.ASCII)
"""Regular expression pattern for validating SMILES strings."""
