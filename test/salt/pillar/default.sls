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
      build: false
      build_args: null
      pull: false
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
      uid: 1883
      gid: null
    container_variants:
      mosquitto_go_auth:
        config: /etc/mosquitto
        data: /var/lib/mosquitto
        default_config:
          auth_opt_auth_cache_seconds: 30
          auth_opt_auth_jitter_seconds: 3
          auth_opt_backends: files, sqlite
          auth_opt_cache: true
          auth_opt_cache_reset: true
          auth_opt_cache_type: go-cache
          auth_opt_disable_superuser: true
          auth_opt_files_acl_path: /etc/mosquitto/acl
          auth_opt_files_register: acl
          auth_opt_hasher: pbkdf2
          auth_opt_hasher_algorithm: sha512
          auth_opt_hasher_iterations: 100000
          auth_opt_hasher_keylen: 64
          auth_opt_hasher_salt_encoding: base64
          auth_opt_hasher_salt_size: 16
          auth_opt_log_dest: file
          auth_opt_log_file: /var/log/mosquitto/mosquitto.log
          auth_opt_log_level: info
          auth_opt_sqlite_register: user
          auth_opt_sqlite_source: /etc/mosquitto/auth.db
          auth_opt_sqlite_userquery: SELECT password_hash FROM users WHERE username =
            ? limit 1
          auth_plugin: /mosquitto/go-auth.so
          listener 1883:
            protocol: mqtt
          log_dest: file /var/log/mosquitto/mosquitto.log
          log_type:
            - error
            - warning
            - notice
            - information
          persistence: true
          persistence_location: /var/lib/mosquitto
          persistent_client_expiration: 30d
        image: docker.io/iegomez/mosquitto-go-auth
        log: /var/log/mosquitto
      mosquitto_official:
        config: /mosquitto/config
        data: /mosquitto/data
        default_config:
          acl_file: /mosquitto/config/acl
          listener 1883:
            protocol: mqtt
          log_dest: file /mosquitto/log/mosquitto.log
          log_type:
            - error
            - warning
            - notice
            - information
          password_file: /mosquitto/config/passwd
          persistence: true
          persistence_location: /mosquitto/data
          persistent_client_expiration: 30d
        image: docker.io/library/eclipse-mosquitto
        log: /mosquitto/log
  install:
    rootless: true
    remove_all_data_for_sure: false
  container_variant: mosquitto_official
  acl:
    anonymous: {}
    pattern: {}
    user: {}
  config: {}
  plugin:
    meross: []
  users:
    absent: []
    present: {}

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
