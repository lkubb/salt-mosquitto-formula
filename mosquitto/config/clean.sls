# -*- coding: utf-8 -*-
# vim: ft=sls

{%- set tplroot = tpldir.split('/')[0] %}
{%- set sls_service_clean = tplroot ~ '.service.clean' %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}

include:
  - {{ sls_service_clean }}

# This does not lead to the containers/services being rebuilt
# and thus differs from the usual behavior
Eclipse Mosquitto environment files are absent:
  file.absent:
    - names:
      - {{ mosquitto.lookup.paths.config_mosquitto }}
    - require:
      - sls: {{ sls_service_clean }}

{%- if mosquitto.users.present %}

Wanted Mosquitto users are absent:
  mosquitto.user_absent:
    - names: {{ mosquitto.users.present | list | json }}
    - pw_file: {{ mosquitto.lookup.paths.config | path_join("passwd") }}
    - onlyif:
      - fun: file.file_exists
        path: {{ mosquitto.lookup.paths.config | path_join("passwd") }}
{%- endif %}
