.. _games.eldenring:

Elden Ring
==========

.. automodule:: soulsgym.games.eldenring

Game settings
-------------

- Elden Ring uses the key mapping in ``soulsgym/core/data/eldenring/keys.yaml``. Set these key
  bindings in System > Keyboard/Mouse Settings > Key Bindings:

  .. list-table::
     :widths: 60 30
     :header-rows: 1

     * - Action
       - Keyboard
     * - Move Forwards / Backwards / Left / Right
       - W / S / A / D
     * - Backstep, Dodge Roll, Dash
       - Space
     * - Move Camera / Change Target (Up / Down / Left / Right)
       - J / K / O / P
     * - Reset Camera, Lock-On/Remove Target
       - Q
     * - Attack (RH & Two-Handed Armament)
       - L
     * - Strong Attack (RH & 2H Armament)
       - Y
     * - Skill
       - M
     * - Use Item
       - R
     * - Event Action (Examine, Open, etc.)
       - E

  SoulsGym only sends keyboard keys, so the attacks need a keyboard binding in addition to the
  mouse. Remove these keys from all other actions (for example Jump or Map), otherwise an action
  can trigger a second one or open a menu.

- The game has to run in offline mode without Easy Anti-Cheat. SoulsGym cannot attach to the game
  process while Easy Anti-Cheat is active. Exclusively use a dedicated save game with SoulsGym, as
  described in the ban protection section of :ref:`setup`.
