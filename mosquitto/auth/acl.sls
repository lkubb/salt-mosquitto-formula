# vim: ft=sls

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_config_file = tplroot ~ ".config.file" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}
{%- from tplroot ~ "/libtofsstack.jinja" import files_switch with context %}

include:
  - {{ sls_config_file }}

# The format for vanilla and goauth is the same for file-based backends
Eclipse Mosquitto ACL file is managed:
  file.managed:
    - name: {{ mosquitto.lookup.paths.config | path_join("acl") }}
    - source: {{ files_switch(
                    ["acl", "acl.j2"],
                    config=mosquitto,
                    lookup="Eclipse Mosquitto ACL file is managed",
                 )
              }}
    - template: jinja
    - mode: '0644'
    - dir_mode: '0755'
    - makedirs: true
    - user: {{ mosquitto.lookup.user.name }}
    - group: {{ mosquitto.lookup.user.name }}
    - require:
      - user: {{ mosquitto.lookup.user.name }}
    - watch_in:
      - Eclipse Mosquitto is installed
    - context:
        mosquitto: {{ mosquitto | json }}
