#!/usr/bin/env bash

if [[ "${1}" == "celery" ]]; then
  celery --app=app.tasks.celery_setup:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=app.tasks.celery_setup:celery flower
fi