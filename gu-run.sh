#!/bin/bash
cd /workspace/v2

gunicorn -b 0.0.0.0:4444 --workers 1 --threads 100 app:app
