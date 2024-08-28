FROM python:3.12-slim AS pdm-venv

ENV PDM_CHECK_UPDATE=false
RUN pip install -U pdm

COPY pyproject.toml pdm.lock /
RUN pdm install --check --prod --no-editable

# run stage
FROM python:3.12-slim

ENV PATH="/.venv/bin:$PATH"
ENV PYTHONPATH="/poc"
ENV APP_MODULE="poc.application:app"
ENV APP_LOG="/var/log/poc.log"
ENV PORT=3000

RUN install -m 666 /dev/null ${APP_LOG}

WORKDIR /poc

COPY --from=pdm-venv /.venv/ /.venv
COPY . /poc


ENTRYPOINT [ "/poc/bin/entrypoint.sh" ]
CMD [ "--proxy-headers" ]
