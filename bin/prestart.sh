#!/bin/bash

set -e

# run pending migrations
alembic upgrade head
