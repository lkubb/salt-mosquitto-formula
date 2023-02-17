# vim: ft=sls

{#-
    *Meta-state*.

    Undoes everything performed in the ``mosquitto`` meta-state
    in reverse order, i.e. stops the mosquitto services,
    removes their configuration and then removes their containers.
#}

include:
  - .service.clean
  - .auth.clean
  - .config.clean
  - .package.clean
