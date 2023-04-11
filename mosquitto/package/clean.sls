# vim: ft=sls

{#-
    Removes the mosquitto containers
    and the corresponding user account and service units.
    Has a depency on `mosquitto.config.clean`_.
    If ``remove_all_data_for_sure`` was set, also removes all data.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_config_clean = tplroot ~ ".config.clean" %}
{%- from tplroot ~ "/map.jinja" import mapdata as mosquitto with context %}

include:
  - {{ sls_config_clean }}

{%- if mosquitto.install.autoupdate_service %}

Podman autoupdate service is disabled for Eclipse Mosquitto:
{%-   if mosquitto.install.rootless %}
  compose.systemd_service_disabled:
    - user: {{ mosquitto.lookup.user.name }}
{%-   else %}
  service.disabled:
{%-   endif %}
    - name: podman-auto-update.timer
{%- endif %}

Eclipse Mosquitto is absent:
  compose.removed:
    - name: {{ mosquitto.lookup.paths.compose }}
    - volumes: {{ mosquitto.install.remove_all_data_for_sure }}
{%- for param in ["project_name", "container_prefix", "pod_prefix", "separator"] %}
{%-   if mosquitto.lookup.compose.get(param) is not none %}
    - {{ param }}: {{ mosquitto.lookup.compose[param] }}
{%-   endif %}
{%- endfor %}
{%- if mosquitto.install.rootless %}
    - user: {{ mosquitto.lookup.user.name }}
{%- endif %}
    - require:
      - sls: {{ sls_config_clean }}

Eclipse Mosquitto compose file is absent:
  file.absent:
    - name: {{ mosquitto.lookup.paths.compose }}
    - require:
      - Eclipse Mosquitto is absent

{%- if mosquitto.install.podman_api %}

Eclipse Mosquitto podman API is unavailable:
  compose.systemd_service_dead:
    - name: podman.socket
    - user: {{ mosquitto.lookup.user.name }}
    - onlyif:
      - fun: user.info
        name: {{ mosquitto.lookup.user.name }}

Eclipse Mosquitto podman API is disabled:
  compose.systemd_service_disabled:
    - name: podman.socket
    - user: {{ mosquitto.lookup.user.name }}
    - onlyif:
      - fun: user.info
        name: {{ mosquitto.lookup.user.name }}
{%- endif %}

Eclipse Mosquitto user session is not initialized at boot:
  compose.lingering_managed:
    - name: {{ mosquitto.lookup.user.name }}
    - enable: false
    - onlyif:
      - fun: user.info
        name: {{ mosquitto.lookup.user.name }}

Eclipse Mosquitto user account is absent:
  user.absent:
    - name: {{ mosquitto.lookup.user.name }}
    - purge: {{ mosquitto.install.remove_all_data_for_sure }}
    - require:
      - Eclipse Mosquitto is absent
    - retry:
        attempts: 5
        interval: 2

{%- if mosquitto.install.remove_all_data_for_sure %}

Eclipse Mosquitto paths are absent:
  file.absent:
    - names:
      - {{ mosquitto.lookup.paths.base }}
    - require:
      - Eclipse Mosquitto is absent
{%- endif %}
