FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY zk_agent_escrow/ ./zk_agent_escrow/
COPY tests/ ./tests/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["zk-agent-escrow"]
CMD ["verify-escrow"]
