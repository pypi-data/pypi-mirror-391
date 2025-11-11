#! /usr/bin/env python

import os
import json

print(json.dumps(dict(os.environ), sort_keys=True, indent=2))
