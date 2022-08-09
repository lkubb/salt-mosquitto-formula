# -*- coding: utf-8 -*-
# vim: ft=sls

{%- set tplroot = tpldir.split('/')[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}
{%- from tplroot ~ "/libtofs.jinja" import files_switch with context %}

Eclipse Mosquitto user account is present:
  user.present:
{%- for param, val in mosquitto.lookup.user.items() %}
{%-   if val is not none and param != "groups" %}
    - {{ param }}: {{ val }}
{%-   endif %}
{%- endfor %}
    - usergroup: true
    - createhome: true
    - groups: {{ mosquitto.lookup.user.groups | json }}
    # (on Debian 11) subuid/subgid are only added automatically for non-system users
    - system: false

Eclipse Mosquitto user session is initialized at boot:
  compose.lingering_managed:
    - name: {{ mosquitto.lookup.user.name }}
    - enable: {{ mosquitto.install.rootless }}
    - require:
      - user: {{ mosquitto.lookup.user.name }}

Eclipse Mosquitto paths are present:
  file.directory:
    - names:
      - {{ mosquitto.lookup.paths.base }}
    - user: {{ mosquitto.lookup.user.name }}
    - group: {{ mosquitto.lookup.user.name }}
    - makedirs: true
    - require:
      - user: {{ mosquitto.lookup.user.name }}

Eclipse Mosquitto compose file is managed:
  file.managed:
    - name: {{ mosquitto.lookup.paths.compose }}
    - source: {{ files_switch(['docker-compose.yml', 'docker-compose.yml.j2'],
                              lookup='Eclipse Mosquitto compose file is present'
                 )
              }}
    - mode: '0644'
    - user: root
    - group: {{ mosquitto.lookup.rootgroup }}
    - makedirs: True
    - template: jinja
    - makedirs: true
    - context:
        mosquitto: {{ mosquitto | json }}

Eclipse Mosquitto is installed:
  compose.installed:
    - name: {{ mosquitto.lookup.paths.compose }}
{%- for param, val in mosquitto.lookup.compose.items() %}
{%-   if val is not none and param != "service" %}
    - {{ param }}: {{ val }}
{%-   endif %}
{%- endfor %}
{%- for param, val in mosquitto.lookup.compose.service.items() %}
{%-   if val is not none %}
    - {{ param }}: {{ val }}
{%-   endif %}
{%- endfor %}
    - watch:
      - file: {{ mosquitto.lookup.paths.compose }}
{%- if mosquitto.install.rootless %}
    - user: {{ mosquitto.lookup.user.name }}
    - require:
      - user: {{ mosquitto.lookup.user.name }}
{%- endif %}
