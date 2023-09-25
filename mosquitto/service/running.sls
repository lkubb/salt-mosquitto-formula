# vim: ft=sls

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_config_file = tplroot ~ ".config.file" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}

include:
  - {{ sls_config_file }}

Eclipse Mosquitto service is enabled:
  compose.enabled:
    - name: {{ mosquitto.lookup.paths.compose }}
{%- for param in ["project_name", "container_prefix", "pod_prefix", "separator"] %}
{%-   if mosquitto.lookup.compose.get(param) is not none %}
    - {{ param }}: {{ mosquitto.lookup.compose[param] }}
{%-   endif %}
{%- endfor %}
    - require:
      - Eclipse Mosquitto is installed
{%- if mosquitto.install.rootless %}
    - user: {{ mosquitto.lookup.user.name }}
{%- endif %}

Eclipse Mosquitto service is running:
  compose.running:
    - name: {{ mosquitto.lookup.paths.compose }}
{%- for param in ["project_name", "container_prefix", "pod_prefix", "separator"] %}
{%-   if mosquitto.lookup.compose.get(param) is not none %}
    - {{ param }}: {{ mosquitto.lookup.compose[param] }}
{%-   endif %}
{%- endfor %}
{%- if mosquitto.install.rootless %}
    - user: {{ mosquitto.lookup.user.name }}
{%- endif %}
    - watch:
      - Eclipse Mosquitto is installed
      - sls: {{ sls_config_file }}
