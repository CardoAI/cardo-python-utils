default:
  just --list

lib_name := "python_utils"

make-api-reference-in-docs:
  #!/usr/bin/zsh
  # reset destination directory
  rm -r docs/api_reference/{{ lib_name }} || printf ""
  cp -r {{ lib_name }} docs/api_reference/{{ lib_name }}

  # remove files that must not belong to the documentation
  fd -I -td "__pycache__"  docs/api_reference/{{ lib_name }}/ -x rm -r {}
  fd -I -tf __init__.py docs/api_reference/{{ lib_name }} -x rm {}
  # this one deletes README.md files
  fd -I -tf -e md . docs/api_reference/{{ lib_name }} -x rm {}

  # replace file extensions
  fd -tf -e py . docs/api_reference/{{ lib_name }} -x rename '.py' '.md' {}

  # inject module path into the markdown files for generation of API reference
  for file in `fd -tf -e md . docs/api_reference/{{ lib_name }} | xargs`; do \
    module_path=`echo $file | sd 'docs/api_reference/' '::: ' | sd '.md' '' | sd '/' '.'`; \
    echo $module_path > $file; \
  done

  # reset the path of the API reference to null, for the sake of making it work
  # since yq would expect integer indexing and we ll be doing string indexing
  # in the for loop
  # note that if you re doing a different layout of the documentation, you need to
  # change the location of the API Reference to how you set it
  api_reference_key='.nav[1].["API Reference"][0]'
  yq -i "$api_reference_key=null" mkdocs.yml

  # repopulate mkdocs.yml
  for md_file in `fd -tf -e md . docs/api_reference/{{ lib_name }}`; do
    # get keypath
    keypath=.`echo $md_file | sd '(docs/api_reference/|.md)' '' | sd '/' '.'`
    # get corrected filepath
    filepath_value=`echo $md_file | sd 'docs/' ''`
    echo $keypath
    echo $filepath_value
    yq -i "$api_reference_key$keypath = \"$filepath_value\"" mkdocs.yml
    echo
  done;

docs-docker-image := "mkdocs-material"
build-docs-image:
  docker build -t {{docs-docker-image}} -f Dockerfile.docs .
