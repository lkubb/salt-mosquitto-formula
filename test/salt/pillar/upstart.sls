# -*- coding: utf-8 -*-
# vim: ft=yaml
---
mosquitto:
  lookup:
    master: template-master
    # Just for testing purposes
    winner: lookup
    added_in_lookup: lookup_value
    compose:
      create_pod: null
      pod_args: null
      project_name: mosquitto
      remove_orphans: true
      service:
        container_prefix: null
        ephemeral: true
        pod_prefix: null
        restart_policy: on-failure
        restart_sec: 2
        separator: null
        stop_timeout: null
    paths:
      base: /opt/containers/mosquitto
      compose: docker-compose.yml
      config_mosquitto: mosquitto.env
      config: config
      data: data
      log: log
    user:
      groups: []
      home: null
      name: mosquitto
      shell: /usr/sbin/nologin
      uid: null
      gid: null
    containers:
      mosquitto:
        image: docker.io/library/eclipse-mosquitto
  install:
    rootless: true
    remove_all_data_for_sure: false
  config:
    listener 1883:
      protocol: mqtt
    log_dest: stdout
    log_type:
      - error
      - warning
      - notice
      - information
    persistence: true
    protocol: mqtt

  tofs:
    # The files_switch key serves as a selector for alternative
    # directories under the formula files directory. See TOFS pattern
    # doc for more info.
    # Note: Any value not evaluated by `config.get` will be used literally.
    # This can be used to set custom paths, as many levels deep as required.
    files_switch:
      - any/path/can/be/used/here
      - id
      - roles
      - osfinger
      - os
      - os_family
    # All aspects of path/file resolution are customisable using the options below.
    # This is unnecessary in most cases; there are sensible defaults.
    # Default path: salt://< path_prefix >/< dirs.files >/< dirs.default >
    #         I.e.: salt://mosquitto/files/default
    # path_prefix: template_alt
    # dirs:
    #   files: files_alt
    #   default: default_alt
    # The entries under `source_files` are prepended to the default source files
    # given for the state
    # source_files:
    #   mosquitto-config-file-file-managed:
    #     - 'example_alt.tmpl'
    #     - 'example_alt.tmpl.jinja'

    # For testing purposes
    source_files:
      Eclipse Mosquitto environment file is managed:
      - mosquitto.env.j2

  # Just for testing purposes
  winner: pillar
  added_in_pillar: pillar_value
