FROM python:alpine AS base
# export PATH="$PATH:$HOME/.local/bin"
# `HF_HUB_ENABLE_HF_TRANSFER` is deprecated, replaced by XET
#ENV HF_HUB_ENABLE_HF_TRANSFER=1
# `hf-xet` is dynamically linked against glibc so doesn't work in Alpine.
ARG UID=1000
ARG GID=1000
ARG USER=bdawg
RUN <<-EOF
    set -eux
    apk add bat fd file jq ripgrep tree vim xh uv
    adduser -D -u $UID -g $GID $USER
EOF
USER $USER
ENV PATH="/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/$USER/.local/bin"


FROM base AS build
ARG UID=1000
ARG GID=1000
COPY --link --chown=$UID:$GID . /facehugger
WORKDIR /facehugger
RUN <<-EOF
    set -eux
    ls -la
    uv tool install .
    echo $PATH
    # test installation is working
    #python -c "from huggingface_hub import model_info; print(model_info('gpt2'))"
    # equivalent `hf` command of the python code above
    #hf models info gpt2 | jq keys
    #hf version
    #hf env
    type facehugger
    facehugger --version
    facehugger --help
EOF

# This stage will normall be skipped
# Can explicitly target it with `docker build -t berne/facehugger --target check .`
FROM base AS check
ARG UID=1000
ARG GID=1000
COPY --link --chown=$UID:$GID . /facehugger
WORKDIR /facehugger
RUN <<-EOF
    set -eux
    # need a venv before `uv pip install .`
    uv venv
    # Will install dependencies, needed for type checking by `ty`
    uv pip install .
    # uvx will use isolated venv, not this projects venv
    uvx ruff format --check --exit-non-zero-on-format
    uvx ruff check
    # uv will enter the venv
    uv run ty check --error-on-warning
    # activate venv so `facehugger` is in the path
    . .venv/bin/activate
    type facehugger
    facehugger --version
    facehugger --help
EOF

FROM base AS image-test
COPY --link --from=build /home/bdawg/.local/share/uv/tools/facehugger /home/bdawg/.local/share/uv/tools/facehugger
# No `--link` so symlinks are copied
COPY --link --from=build /home/bdawg/.local/bin /home/bdawg/.local/bin
ENTRYPOINT ["facehugger"]
CMD ["--help"]
RUN <<-EOF
    set -eux
    facehugger --version
    facehugger --help
EOF

# final image
FROM base
COPY --link --from=build /home/bdawg/.local/share/uv/tools/facehugger /home/bdawg/.local/share/uv/tools/facehugger
# No `--link` so symlinks are copied
COPY --link --from=build /home/bdawg/.local/bin /home/bdawg/.local/bin
ENTRYPOINT ["facehugger"]
CMD ["--help"]
