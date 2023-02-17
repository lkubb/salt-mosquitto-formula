# vim: ft=sls

{#-
    *Meta-state*.

    This installs the mosquitto containers,
    manages their configuration and starts their services.
#}

include:
  - .package
  - .config
  - .auth
  - .service
