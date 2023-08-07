# vim: ft=sls

{#-
    Removes the configuration of the mosquitto containers
    and has a dependency on `mosquitto.service.clean`_.

    This does not lead to the containers/services being rebuilt
    and thus differs from the usual behavior.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_service_clean = tplroot ~ ".service.clean" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}

include:
  - {{ sls_service_clean }}

Eclipse Mosquitto environment files are absent:
  file.absent:
    - names:
      - {{ mosquitto.lookup.paths.config_mosquitto }}
    - require:
      - sls: {{ sls_service_clean }}
