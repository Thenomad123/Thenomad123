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
          -d text="✅ Nowa wersja obrazu \`${{ steps.version.outputs.VERSION }}\` została zbudowana i opublikowana do GHCR. Sprawdź changelog w repozytorium."