# vim: ft=sls

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_config_file = tplroot ~ ".config.file" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}

Eclipse Mosquitto ACL file is absent:
  file.absent:
    - name: {{ mosquitto.lookup.paths.config | path_join("acl") }}

{%- if "mosquitto_go_auth" == mosquitto.container_variant and "sqlite" == mosquitto.goauth_backend %}
{%-   set pw_file = mosquitto.lookup.paths.config | path_join("auth.db") %}
{%- else %}
{%-   set pw_file = mosquitto.lookup.paths.config | path_join("passwd") %}
{%- endif %}

{%-   if mosquitto.users.present %}

Wanted Mosquitto users are absent:
  mosquitto.user_absent:
    - names:
{%-     for user, confs in mosquitto.users.present.items() %}
      - {{ user }}:
{%-       for var, val in confs.items() %}
        - {{ var }}: {{ val }}
{%-       endfor %}
{%-     endfor %}
    - pw_file: {{ pw_file }}
    - goauth: {{ "mosquitto_go_auth" == mosquitto.container_variant }}
{%-   endif %}
