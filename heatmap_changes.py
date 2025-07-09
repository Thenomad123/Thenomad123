name: CI/CD - Build, Scan, Tag, Notify

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      security-events: write

    steps:
    - name: Checkout repo
      uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 20

    - name: Extract version from package.json
      id: version
      run: echo "VERSION=$(node -p \"require('./package.json').version\")" >> $GITHUB_OUTPUT

    - name: Log in to GHCR
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Cache Docker layers
      uses: actions/cache@v4
      with:
        path: /tmp/.buildx-cache
        key: ${{ runner.os }}-buildx-${{ github.sha }}
        restore-keys: |
          ${{ runner.os }}-buildx-

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/vscode-docs:latest
          ghcr.io/${{ github.repository_owner }}/vscode-docs:${{ steps.version.outputs.VERSION }}
        cache-from: type=local,src=/tmp/.buildx-cache
        cache-to: type=local,dest=/tmp/.buildx-cache

    - name: Run security scan with Trivy
      uses: aquasecurity/trivy-action@v0.16.1
      with:
        image-ref: ghcr.io/${{ github.repository_owner }}/vscode-docs:${{ steps.version.outputs.VERSION }}
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload scan results
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: trivy-results.sarif

    - name: Generate changelog
      run: |
        gem install github_changelog_generator
        github_changelog_generator --user ${{ github.repository_owner }} --project vscode-docs --token ${{ secrets.GITHUB_TOKEN }}

    - name: Commit & push changelog
      run: |
        git config user.name "github-actions"
        git config user.email "actions@github.com"
        git add CHANGELOG.md
        git commit -m "chore: update changelog [skip ci]" || echo "No changes"
        git push

    - name: Send Telegram notification
      if: success()
      env:
        TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      run: |
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
          -d chat_id="${TELEGRAM_CHAT_ID}" \

          {
  // ...
  "build": { "dockerfile": "Dockerfile" },
  // ...
}
ARG VARIANT="16"
FROM mcr.microsoft.com/devcontainers/javascript-node:1-${VARIANT}

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends bundler

# [Optional] Uncomment if you want to install an additional version
#  of node using nvm
# ARG EXTRA_NODE_VERSION=18
# RUN su node -c "source /usr/local/share/nvm/nvm.sh \
#    && nvm install ${EXTRA_NODE_VERSION}"

COPY ./script-in-your-repo.sh /tmp/scripts/script-in-codespace.sh
RUN apt-get update && bash /tmp/scripts/script-in-codespace.sh
build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile
        push: true
        tags: user/app:latest
// fetch-commit.js
// Requires: npm install node-fetch
import fetch from 'node-fetch';
import fs from 'fs';

const OWNER = 'Thenomad123';
const REPO  = 'vscode-docs';
const SHA   = 'efba259b9f3300b14b196c38efde6559c7521068';
const TOKEN = process.env.GH_TOKEN;

async function getCommit() {
  const url = `https://api.github.com/repos/${OWNER}/${REPO}/commits/${SHA}`;
  const resp = await fetch(url, {
    headers: { 'Authorization': `token ${TOKEN}` }
  });
  if (!resp.ok) throw new Error(`GitHub API error: ${resp.status}`);
  const data = await resp.json();
  fs.writeFileSync(`commit-${SHA}.json`, JSON.stringify(data, null, 2));
  console.log(`Saved commit-${SHA}.json`);
}

getCommit().catch(err => console.error(err));
# .github/workflows/docs-ci.yml
name: Docs CI & Deploy
on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint Markdown
        uses: markdownlint/markdownlint-action@v1
      - name: Link Checker
        run: npx markdown-link-check -q **/*.md

  deploy:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docs
        run: npm ci && npm run build:docs
      - name: Deploy to Netlify
        uses: netlify/actions@v3
        with:
          publish-dir: ./build/docs
          production-deploy: true
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_TOKEN }}
# commit_stats.py
from git import Repo
import json

repo = Repo('.')
commits = list(repo.iter_commits('main', max_count=500))
stats = {'total_commits': len(commits), 'authors': {} }
for c in commits:
    name = c.author.name
    stats['authors'].setdefault(name, 0)
    stats['authors'][name] += 1

with open('commit-stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
print('Commit statistics written to commit-stats.json')

# netlify.toml
enable = true

[build]
  publish = "build/docs"
  command = "npm run build:docs"

[context.production.environment]
  NODE_ENV = "production"

[headers]
  # Cache assets for 1 year
t "/*.js"
    Cache-Control = "public, max-age=31536000, immutable"

  "/*.css"
    Cache-Control = "public, max-age=31536000, immutable"


> **⚠ Uwaga bezpieczeństwa**  
> Ten przewodnik instaluje rozszerzenie z uprawnieniami administratora. Upewnij się, że masz zaufane źródło i wykonujesz instrukcje w izolowanym środowisku testowym.

// plugins/docusaurus-plugin-live-diff/index.js
module.exports = function liveDiffPlugin(context, options) {
  return {
    name: 'live-diff-plugin',
    async contentLoaded({ content, actions }) {
      const { setGlobalData } = actions;
      // Fetch diff JSON generated by CI
      const diff = await fetch('/diff/latest.json').then(r => r.json());
      setGlobalData({ diff });
    },
    injectHtmlTags() {
      return {
        headTags: [
          { tagName: 'script', innerHTML: `window.LIVE_DIFF = ${JSON.stringify(this.globalData.diff)}` }
        ],
      };
    }
  };
};

<!-- docs/3d-model.md -->
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
<model-viewer src="/models/extension-arch.glb"
              alt="3D model of extension architecture"
              auto-rotate camera-controls
              ar
              ar-modes="webxr scene-viewer quick-look">
</model-viewer>

# heatmap_changes.py
import json
import numpy as np
import matplotlib.pyplot as plt

with open('file-change-frequency.json') as f:Motorola S-Record (format pliku .s19),
