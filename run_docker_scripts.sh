#!/bin/bash
export ENVIRONMENT="DEV"
echo $ENVIRONMENT
if [ "$ENVIRONMENT" == "DEV" ]; then
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
elif [ "$ENVIRONMENT" == "QA" ]; then
exec uvicorn src.main:app --host 0.0.0.0 --port 9050
fi