# -*- coding: utf-8 -*-
# vim: ft=sls

{%- set tplroot = tpldir.split('/')[0] %}
{%- set sls_config_file = tplroot ~ '.config.file' %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}
{%- from tplroot ~ "/libtofs.jinja" import files_switch with context %}

include:
  - {{ sls_config_file }}

{%- if "mosquitto_go_auth" == mosquitto.container_variant %}
{%-   set pw_file = mosquitto.lookup.paths.config | path_join("auth.db") %}

Mosquitto go auth users table exists:
  sqlite3.table_present:
    - name: users
    - db: {{ pw_file }}
    - schema:
      - id INTEGER PRIMARY KEY
      - username varchar(100) not null
      - password_hash varchar(200) not null
      - is_admin integer not null
    - require:
      - sls: {{ sls_config_file }}
{%- else %}
{%-   set pw_file = mosquitto.lookup.paths.config | path_join("passwd") %}
{%- endif %}

Mosquitto password file exists with correct permissions:
  file.managed:
    - name: {{ pw_file }}
    - replace: false
    - user: root
    - group: {{ mosquitto.lookup.user.name }}
    - mode: '0640'
    - require:
      - sls: {{ sls_config_file }}

{%- if mosquitto.users.present %}

Wanted Mosquitto users are present:
  mosquitto.user_present:
    - names:
{%-     for user, confs in mosquitto.users.present.items() %}
      - {{ user }}:
{%-       for var, val in confs.items() %}
        - {{ var }}: {{ val }}
{%-       endfor %}
{%-     endfor %}
    - pw_file: {{ pw_file }}
    - goauth: {{ "mosquitto_go_auth" == mosquitto.container_variant }}
    - require:
      - Mosquitto password file exists with correct permissions
    - watch_in:
      - Eclipse Mosquitto is installed
{%- endif %}

{%- if mosquitto.users.absent %}

Unwanted Mosquitto users are absent:
  mosquitto.user_absent:
    - names: {{ mosquitto.users.absent | json }}
    - pw_file: {{ pw_file }}
    - goauth: {{ "mosquitto_go_auth" == mosquitto.container_variant }}
    - require:
      - Mosquitto password file exists with correct permissions
    - watch_in:
      - Eclipse Mosquitto is installed
{%- endif %}
