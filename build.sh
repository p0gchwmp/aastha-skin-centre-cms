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
  python manage.py audit_release_signoff \
    --json audit-artifacts/release-signoff.json
  python manage.py build_cutover_manifest \
    --json audit-artifacts/cutover-manifest.json
  python manage.py test \
    home.test_quality_gates \
    home.test_initialize_cms \
    home.test_cutover_manifest \
    home.test_local_search \
    home.test_release_signoff \
    home.test_seo_foundation \
    home.test_seo_verification \
    seo_support.test_audit_seo_content \
    seo_support.tests
fi

python manage.py bootstrap_admin --if-configured
python manage.py check --deploy
