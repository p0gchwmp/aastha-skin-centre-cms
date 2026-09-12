#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python tools/build_visual_cue_assets.py
python tools/generate_responsive_clinical_images.py
python tools/verify_exact_page_snapshots.py
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py initialize_cms
python manage.py sync_doctor_profile_v2
python manage.py bootstrap_admin --if-configured
python manage.py check --deploy
