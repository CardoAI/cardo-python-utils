# Documentation and API Reference

In order to edit documentation, it is recommended to use the following `mamba`/`conda` environment:

```shell
# create environment named "mkdocs" with dependencies
mamba create -n mkdocs -y -c conda-forge mkdocs-material mkdocstrings-python mike go-yq just sd fd

# autogenerate api reference according to just recipe in justfile
mamba run -n mkdocs just make-api-reference-in-docs

# start development server
mamba run -n mkdocs serve
```

Now you can add/edit markdown files in the `docs/` directory and you need to make sure that these files are referenced in the `nav` section of the `mkdocs.yml` file in order to be able to see them.

> The auto-generation of the API Reference populates the nav section of the `mkdocs.yml` using `yq`

Useful links to get you started with mkdocs to write documentation are:

1. [mkdocs-material](https://squidfunk.github.io/mkdocs-material/)
2. [mkdocs](https://www.mkdocs.org/)

## API Reference auto-generation

It follows the script specified in the [justfile](../justfile). It

- copies the same tree structure of the library
- injects the `:::` directive to the markdown file corresponding to the submodule
- references the markdown files in the `mkdocs.yml`

## Deployment of docs

Running the command `mkdocs build` will statically generate the html files in the `site/` directory. The docs can be served as a docker image with the following Dockerfile (once the docs are built of course)

```Dockerfile
FROM nginx:latest
COPY site /usr/share/nginx/html
```
