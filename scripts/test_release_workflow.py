from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
BUILD_SCRIPT = ROOT / "scripts" / "build-pdf.sh"


def load_workflow() -> dict:
    return yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_release_can_only_be_started_manually() -> None:
    workflow = load_workflow()
    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] == "false"


def test_only_environment_guarded_publish_job_can_write() -> None:
    jobs = load_workflow()["jobs"]
    assert jobs["prepare"]["permissions"] == {"contents": "read", "actions": "read"}
    assert jobs["publish"]["environment"] == "release"
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert jobs["publish"]["needs"] == "prepare"


def test_pdf_is_an_explicit_opt_in_not_a_release_requirement() -> None:
    workflow = load_workflow()
    setting = workflow["on"]["workflow_dispatch"]["inputs"]["include_pdf"]
    assert setting["type"] == "boolean"
    assert setting["default"] == "false"
    pdf_steps = [step for step in workflow["jobs"]["prepare"]["steps"]
                 if step["name"] in {
                     "Install PDF build dependencies",
                     "Test the installed PDF reader with all three locales",
                     "Build all three PDFs from the same page order",
                     "Verify PDF text, coverage, and filenames",
                 }]
    assert len(pdf_steps) == 4
    assert all(step["if"] == "${{ inputs.include_pdf }}" for step in pdf_steps)
    for name in ("Run blocking repository gates", "Run the full release content-health scan",
                 "Render one trilingual Release body"):
        step = next(step for step in workflow["jobs"]["prepare"]["steps"] if step["name"] == name)
        assert "if" not in step


def test_optional_asset_guards_cover_check_upload_and_exact_draft_inventory() -> None:
    publish = load_workflow()["jobs"]["publish"]
    assert publish["env"]["INCLUDE_PDF"] == "${{ inputs.include_pdf }}"
    steps = {step["name"]: step for step in publish["steps"]}
    check = steps["Recheck main and requested assets before writing"]["run"]
    assert 'if [ "$INCLUDE_PDF" = true ]; then' in check
    assert check.index('if [ "$INCLUDE_PDF" = true ]; then') < check.index('for locale in zh-TW zh-Hans en')
    upload = steps["Create or refresh a Draft Release"]["run"]
    assert upload.index('if [ "$INCLUDE_PDF" = true ]; then') < upload.index('gh release upload')
    verify = steps["Verify the Draft Release before publishing"]["run"]
    assert ': > /tmp/expected-assets.txt' in verify
    assert 'if [ "$INCLUDE_PDF" = true ]; then' in verify
    assert 'diff -u /tmp/expected-assets.txt /tmp/actual-assets.txt' in verify


def test_prepare_locks_main_and_builds_all_locales() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count("runs-on: ubuntu-24.04") == 2
    assert "test \"$DISPATCH_REF\" = refs/heads/main" in text
    assert "https://api.github.com/" in text
    assert "environments/release" in text
    assert 'environment_json="$(gh api "repos/$REPOSITORY/environments/release")"' in text
    assert "required_reviewers" in text
    assert "test \"$sha\" = \"$remote_main\"" in text
    assert "for locale in zh-TW zh-Hans en" in text
    assert "validate-pdfs" in text
    assert "--mode release" in text


def test_publish_rechecks_sha_and_verifies_draft_before_publish() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count('test "$current_main" = "$LOCKED_SHA"') == 2
    assert text.count('test "$(git rev-list -n 1 "$RELEASE_VERSION")" = "$LOCKED_SHA"') == 2
    assert 'git ls-remote --exit-code --tags origin "refs/tags/$RELEASE_VERSION"' in text
    draft = text.index("Create or refresh a Draft Release")
    verify = text.index("Verify the Draft Release before publishing")
    publish = text.index("Publish and verify the Release")
    assert draft < verify < publish
    draft_verify_block = text[verify:publish]
    assert 'gh release view "$RELEASE_VERSION" --repo "$REPOSITORY"' in draft_verify_block
    assert "--json isDraft,targetCommitish,body,assets" in draft_verify_block
    assert 'test "$(jq -r .isDraft /tmp/release.json)" = true' in draft_verify_block
    assert 'test "$(jq -r .targetCommitish /tmp/release.json)" = "$LOCKED_SHA"' in draft_verify_block
    assert "releases/tags/" not in draft_verify_block
    refresh_block = text[draft:verify]
    existing_draft_branch = refresh_block.split("          else", maxsplit=1)[0]
    assert 'gh release edit "$RELEASE_VERSION"' in existing_draft_branch
    assert '--draft --target "$LOCKED_SHA" --title "$title"' in existing_draft_branch
    publish_command = text.index(
        'gh release edit "$RELEASE_VERSION" --repo "$REPOSITORY" --draft=false --latest',
        publish,
    )
    tag_fetch = text.index(
        'git fetch --force origin "refs/tags/$RELEASE_VERSION:refs/tags/$RELEASE_VERSION"',
        publish,
    )
    assert publish_command < tag_fetch
    for locale in ("zh-TW", "zh-Hans", "en"):
        assert f'awesome-agentic-ai-zh-$RELEASE_VERSION-{locale}.pdf' in text


def test_pdf_builder_reads_manifest_instead_of_hardcoding_pages() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert 'release_manifest.py validate --strict-urls --version "$RELEASE_VERSION"' in text
    assert "release_manifest.py assemble" in text
    assert "stages/01-llm-basics" not in text
    assert "LANG_VARIANT must be zh-TW, zh-Hans, or en" in text
