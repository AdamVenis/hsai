import minions.minion_effects

starter = ['Leper Gnome', 'Leper Gnome',
           'Novice Engineer', 'Novice Engineer',
           'Loot Hoarder', 'Loot Hoarder',
           'River Crocolisk', 'River Crocolisk',
           'Ironfur Grizzly', 'Ironfur Grizzly',
           'Wolfrider', 'Wolfrider',
           'Harvest Golem', 'Harvest Golem',
           'Earthen Ring Farseer', 'Earthen Ring Farseer',
           'Chillwind Yeti', 'Chillwind Yeti',
           'Gnomish Inventor', 'Gnomish Inventor',
           "Sen'jin Shieldmasta", "Sen'jin Shieldmasta",
           'Boulderfist Ogre', 'Boulderfist Ogre']

# one of each minion with effects, without the non-minion effects
effect_testing = minions.minion_effects.minion_effects.keys()
effect_testing.remove('Druid')
effect_testing.remove('Healing Totem')

default_mage = ['Arcane Missiles', 'Arcane Missiles',
                'Arcane Explosion', 'Arcane Explosion',
                'Arcane Intellect', 'Arcane Intellect',
                'Fireball', 'Fireball',
                'Polymorph', 'Polymorph',
                'Murloc Raider', 'Murloc Raider',
                'Bloodfen Raptor', 'Bloodfen Raptor',
                'Novice Engineer', 'Novice Engineer',
                'River Crocolisk', 'River Crocolisk',
                'Raid Leader', 'Raid Leader',
                'Wolfrider', 'Wolfrider',
                'Oasis Snapjaw', 'Oasis Snapjaw',
                "Sen'jin Shieldmasta", "Sen'jin Shieldmasta",
                'Nightblade', 'Nightblade',
                'Boulderfist Ogre', 'Boulderfist Ogre']
