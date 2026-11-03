# OneNexus build of json-everything

This fork builds four json-everything libraries from upstream's MIT source and
publishes them to the onenexus-team GitHub Packages NuGet feed as
`OneNexus.Json.More.Net`, `OneNexus.JsonPointer.Net`, `OneNexus.JsonLogic` and
`OneNexus.JsonSchema.Net`. Upstream's NuGet binaries from 1 Feb 2026 carry the
Open Source Maintenance Fee agreement (`OSMFEULA.txt`); its §4 allows anyone to
"independently compile binaries from the Software's source code without this
Agreement". Package ids are renamed so that a restore can never fall back to
the fee-bearing binaries on nuget.org. Assembly names, namespaces and the
strong-name key are upstream's, so consumers change package names only.

## The one commit

Branch `onenexus/release` is one commit on top of an upstream commit. It adds
only files upstream does not have, so rebasing it never conflicts:

- `Directory.Build.targets` prefixes every `PackageId` with `OneNexus.`
  (project references follow), points the license at MIT `LICENSE`, drops the
  packed `OSMFEULA.txt` and names this fork as the repository.
- `.onenexus/pack.sh` builds and packs inside the pinned .NET SDK image.
- `.onenexus/verify.py` checks ids, dependencies, license, repository commit
  and `lib/` contents before anything is published.
- `.github/workflows/onenexus-release.yml` runs both on an `onenexus-*` tag and
  pushes the packages.

Upstream has no release tags for these packages; every package publishes from
`master`. Take the upstream commit from the released package's nuspec
(`repository commit`) on nuget.org.

## Releasing

Upstream's own workflows publish from `master`, so keep them disabled in this
fork (`gh workflow disable` each one) and never push to `master`. The upgrade
runbook (`platforms/beacon/runbooks/json-everything-upgrade.md` in
one-nexus-ai-platform) has the full steps. In short:

```sh
git fetch upstream
git rebase --onto <upstream-commit> <old-upstream-commit> onenexus/release
docker run --rm -v "$PWD:/src" -w /src --entrypoint bash \
  mcr.microsoft.com/dotnet/sdk:10.0.403 \
  -c 'git config --global --add safe.directory /src && .onenexus/pack.sh'
python3 -I .onenexus/verify.py .onenexus/out "$(git rev-parse HEAD)"
git push --force-with-lease origin onenexus/release
git tag onenexus-<upstream-short-sha> && git push origin onenexus-<upstream-short-sha>
```

Package versions are upstream's. A version already on the feed is never
replaced; the workflow skips it.
