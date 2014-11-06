REPLAY SPEC:

{
    setup: [
        {
            kept: [indices]
            deck: [cards]
            hero: hero_id
        }
    ] # two of these, one for each player
    [actions / aux]
    winner: px
}


keywords:
HERO_POWER [<TARGET>]
ATTACK <SOURCE> <TARGET>
SUMMON <CARD>
CAST <CARD>
AUX <INT>
END_TURN


aux:
supplies additional params for TARGET, PICK and RANDOM
generator of integers (often indices)