#!/usr/bin/env bash
# Builds and packs the four OneNexus.* packages from this checkout.
# Run inside the pinned .NET SDK image with the checkout mounted at /src
# (see .github/workflows/onenexus-release.yml); the fixed path and
# ContinuousIntegrationBuild keep the output byte-for-byte reproducible.
set -euo pipefail

out="${1:-/src/.onenexus/out}"
props=(-c Release -p:ContinuousIntegrationBuild=true -p:GeneratePackageOnBuild=false)

rm -rf "$out"
dotnet restore src/JsonSchema/JsonSchema.csproj
dotnet restore src/JsonLogic/JsonLogic.csproj
# JsonSchema.Net packs its main package only with ResourceLanguage=base
# (upstream's publish-schema.yml); without it pack fails with NU5046.
dotnet build src/JsonSchema/JsonSchema.csproj "${props[@]}" -p:ResourceLanguage=base --no-restore
# Build first, then pack --no-build: a plain pack races GeneratePackageOnBuild (NU5026).
dotnet build src/JsonLogic/JsonLogic.csproj "${props[@]}" --no-restore

dotnet pack src/Json.More/Json.More.csproj "${props[@]}" --no-build -o "$out"
dotnet pack src/JsonPointer/JsonPointer.csproj "${props[@]}" --no-build -o "$out"
dotnet pack src/JsonLogic/JsonLogic.csproj "${props[@]}" --no-build -o "$out"
dotnet pack src/JsonSchema/JsonSchema.csproj "${props[@]}" -p:ResourceLanguage=base --no-build -o "$out"
