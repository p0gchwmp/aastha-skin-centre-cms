#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python tools/build_visual_cue_assets.py
python tools/generate_responsive_clinical_images.py
python tools/audit_clinical_result_images.py
python tools/verify_exact_page_snapshots.py
npm --prefix frontend install --no-audit --no-fund
npm --prefix frontend run build
for js in home/static/js/editorial-v37*.js home/static/js/appointment-form-controller.js; do
  if [ -f "$js" ]; then
    node --check "$js"
  fi
done
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py initialize_cms
python manage.py audit_editorial_v37

if [[ "${RENDER_EXTERNAL_HOSTNAME:-}" == "aastha-editorial-cms-staging.onrender.com" ]]; then
  mkdir -p audit-artifacts
  python manage.py check_launch_config
  python manage.py audit_seo_content \
    --json audit-artifacts/staging-seo-content.json \
    --fail-on-errors
  python manage.py qa_cms_release
fi

python manage.py bootstrap_admin --if-configured
python manage.py check --deploy
