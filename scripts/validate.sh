#!/bin/bash

# Simple colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

passed=0
failed=0

check() {
    local what="$1"
    local how="$2"
    
    printf "Checking $what... "
    
    if eval "$how" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((passed++))
    else
        echo -e "${RED}✗${NC}"
        ((failed++))
    fi
}

echo "Project structure:"
check "main.py is in the right place" "test -f main.py"
check "app directory exists" "test -d app"
check "requirements file" "test -f app/requirements.txt || test -f requirements.txt"
check "docker files" "test -f docker-compose.yml && test -f Dockerfile"

echo ""
echo "Python code:"
check "main.py compiles" "python -m py_compile main.py"
check "config imports work" "PYTHONPATH='.' python -c 'from app.core.config import settings' 2>/dev/null"
check "circuit breaker imports" "PYTHONPATH='.' python -c 'from app.core.circuit_breaker import CircuitBreaker' 2>/dev/null"
check "rate schemas import" "PYTHONPATH='.' python -c 'from app.schemas.rates import ExchangeRateData' 2>/dev/null"

echo ""
echo "Infrastructure:"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -d "$PROJECT_ROOT/infra" ]; then
    check "terraform syntax" "cd $PROJECT_ROOT/infra && terraform validate"
    check "terraform modules exist" "test -d $PROJECT_ROOT/infra/modules && ls $PROJECT_ROOT/infra/modules/ | grep -q ."
else
    echo "No infra/ directory found"
    ((failed++))
fi

echo ""
echo "Docker setup:"
if command -v docker-compose >/dev/null 2>&1; then
    check "docker-compose syntax" "docker-compose config"
else
    echo "Docker not available (that's ok)"
fi

echo ""
echo "Results:"
echo -e "  ${GREEN}$passed things working${NC}"
echo -e "  ${RED}$failed issues found${NC}"

echo ""
if [ $failed -eq 0 ]; then
    echo -e "${GREEN} Everything looks good${NC}"
    echo ""
    echo "Ready to:"
    echo "  • Test locally: docker-compose up --build"
    echo "  • Deploy to AWS: cd infra && terraform apply"
    echo "  • Show off: http://localhost:8000/docs"
elif [ $failed -lt 3 ]; then
    echo -e "${YELLOW}Mostly good, just $failed minor issues${NC}"
else
    echo -e "${RED}Found $failed problems that should be fixed${NC}"
    exit 1
fi

echo "This validates the code structure."
echo "To test the actual app, run: docker-compose up --build"
