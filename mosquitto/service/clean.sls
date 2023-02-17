# vim: ft=sls


{#-
    Stops the mosquitto container services
    and disables them at boot time.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}

mosquitto service is dead:
  compose.dead:
    - name: {{ mosquitto.lookup.paths.compose }}
{%- for param in ["project_name", "container_prefix", "pod_prefix", "separator"] %}
{%-   if mosquitto.lookup.compose.get(param) is not none %}
    - {{ param }}: {{ mosquitto.lookup.compose[param] }}
{%-   endif %}
{%- endfor %}
{%- if mosquitto.install.rootless %}
    - user: {{ mosquitto.lookup.user.name }}
{%- endif %}

mosquitto service is disabled:
  compose.disabled:
    - name: {{ mosquitto.lookup.paths.compose }}
{%- for param in ["project_name", "container_prefix", "pod_prefix", "separator"] %}
{%-   if mosquitto.lookup.compose.get(param) is not none %}
    - {{ param }}: {{ mosquitto.lookup.compose[param] }}
{%-   endif %}
{%- endfor %}
{%- if mosquitto.install.rootless %}
    - user: {{ mosquitto.lookup.user.name }}
{%- endif %}
