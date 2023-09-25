# vim: ft=sls

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_package_install = tplroot ~ ".package.install" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}
{%- from tplroot ~ "/libtofsstack.jinja" import files_switch with context %}

include:
  - {{ sls_package_install }}

Eclipse Mosquitto environment files are managed:
  file.managed:
    - names:
      - {{ mosquitto.lookup.paths.config_mosquitto }}:
        - source: {{ files_switch(
                        ["mosquitto.env", "mosquitto.env.j2"],
                        config=mosquitto,
                        lookup="mosquitto environment file is managed",
                        indent_width=10,
                     )
                  }}
    - mode: '0640'
    - user: root
    - group: {{ mosquitto.lookup.user.name }}
    - makedirs: true
    - template: jinja
    - require:
      - user: {{ mosquitto.lookup.user.name }}
    - require_in:
      - Eclipse Mosquitto is installed
    - context:
        mosquitto: {{ mosquitto | json }}

Eclipse Mosquitto configuration is managed:
  file.managed:
    - name: {{ mosquitto.lookup.paths.config | path_join("mosquitto.conf") }}
    - source: {{ files_switch(
                    ["mosquitto.conf", "mosquitto.conf.j2"],
                    config=mosquitto,
                    lookup='Eclipse Mosquitto configuration is managed',
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
    - context:
        mosquitto: {{ mosquitto | json }}
