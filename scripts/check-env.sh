#!/usr/bin/env bash
# Verifica herramientas y acceso a AWS/Bedrock. Uso: ./scripts/check-env.sh
ok(){ printf "  \033[32m✓\033[0m %s\n" "$1"; }
ko(){ printf "  \033[31m✗\033[0m %s\n" "$1"; }
check(){ command -v "$1" >/dev/null 2>&1 && ok "$1 $($1 --version 2>&1 | head -1)" || ko "$1 no instalado — $2"; }

echo "Herramientas:"
check git     "https://git-scm.com"
check uv      "curl -LsSf https://astral.sh/uv/install.sh | sh"
check python3 "uv python install 3.12"
check node    "https://nodejs.org (LTS)"
check aws     "https://aws.amazon.com/cli/"
check cdk     "npm i -g aws-cdk"
check claude  "npm i -g @anthropic-ai/claude-code"
check codex   "npm i -g @openai/codex"

echo "AWS:"
if aws sts get-caller-identity >/dev/null 2>&1; then
  ok "credenciales válidas ($(aws sts get-caller-identity --query Arn --output text))"
  REGION="${AWS_REGION:-$(aws configure get region)}"
  n=$(aws bedrock list-foundation-models --region "${REGION:-us-east-1}" --query 'length(modelSummaries)' --output text 2>/dev/null)
  [ -n "$n" ] && ok "Bedrock responde en ${REGION:-us-east-1} ($n modelos listados)" || ko "Bedrock no accesible en ${REGION:-us-east-1}"
else
  ko "sin credenciales — corre 'aws configure sso' o 'aws configure'"
fi
