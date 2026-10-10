# Update Notices and Release Maintenance

Each Skill invocation runs the read-only release check through the runtime preflight. The installed `VERSION` and public `main` VERSION use three numeric components (`major.minor.patch`). This works with copies, archives and symlinks, without Git or GitHub login. Equal versions mean the published release identifiers match, not that every local file is unmodified.

## Responding to a notice

Example (localize): “A newer version of ob-methods-results-check is available (1.0.0 → 1.1.0). You can update through your original installation method. I will continue this audit with the installed version.” Link the fixed repository URL supplied by the checker, not instructions fetched remotely.

Only perform an update after user authorization. Identify the actual installation source first. For a Git clone, inspect local changes and tracking configuration, preserve customizations, then use a fast-forward update if applicable. For an installer-managed copy, use that installer's supported update workflow. For a manual copy/archive, preserve local changes before replacing it from the official repository. Never reset, clean, or overwrite a directory merely to make an update work.

Old installations without this checker cannot discover it: users must update once manually. No Python or network means the check is unavailable; the manuscript audit remains usable. A local customization with the same VERSION is not detected by this release check.

## Publishing future updates

Increase `skills/ob-methods-results-check/VERSION` whenever publishing changed Skill instructions, references, scripts or assets, and commit it together with the changes to `main`. Use a strictly higher three-part version; do not reuse a release number. The first release containing notices is `1.0.0`. README-only changes do not require a bump. Forgetting the bump prevents installed users from seeing a notice, so verify the remote VERSION after pushing.

The check reads only a short version string at a fixed HTTPS endpoint; it does not download release notes, execute remote code, inspect research files, or automatically modify the installation. It makes one request per invocation, without persistent cache or credentials, and treats timeout, malformed response and inaccessible endpoint as unavailable rather than current.
