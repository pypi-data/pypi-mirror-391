import random
import math
import enum


class SpellType(enum.Flag):
    DAMAGING = enum.auto()
    HEALING = enum.auto()
    STATS = enum.auto()
    STATUS_EFFECT = enum.auto()


class DamageComponent:
    dice_type_distribution = ([4] * 7) + \
                             ([6] * 12) + \
                             ([8] * 32) + \
                             ([10] * 30) + \
                             ([12] * 12) + \
                             ([20] * 6) + \
                             ([100] * 1)

    all_damage_types = ["da fuoco", "da freddo", "elettrici", "sonici", "necrotici", "magici",
                        "da acido", "divini", "nucleari", "psichici", "fisici", "puri", "da taglio",
                        "da perforazione", "da impatto", "da caduta", "gelato", "onnipotenti", "oscuri",
                        "di luce", "da velocità", "da cactus", "dannosi", "da radiazione",
                        "tuamammici", "da maledizione", "pesanti", "leggeri", "immaginari", "da laser",
                        "da neutrini", "galattici", "cerebrali", "ritardati", "ritardanti", "morali", "materiali",
                        "energetici", "esplosivi", "energetici", "finanziari", "radianti", "sonori", "spaggiaritici",
                        "interiori", "endocrini", "invisibili", "inesistenti", "eccellenti", "bosonici",
                        "gellificanti", "terminali"]

    repeat_distribution = ([1] * 8) + \
                          ([2] * 1) + \
                          ([3] * 1)

    damage_types_distribution = ([1] * 6) + \
                                ([2] * 3) + \
                                ([3] * 1)

    def __init__(self):
        # ENSURE THE SEED IS ALREADY SET WHEN CREATING THIS COMPONENT!!!
        self.dice_number = random.randrange(1, 21)
        self.dice_type = random.sample(self.dice_type_distribution, 1)[0]
        self.constant = random.randrange(math.floor(-self.dice_type / 4), math.ceil(self.dice_type / 4) + 1)
        self.miss_chance = random.randrange(50, 101)
        self.repeat = random.sample(self.repeat_distribution, 1)[0]
        self.damage_types_qty = random.sample(self.damage_types_distribution, 1)[0]
        self.damage_types = random.sample(self.all_damage_types, self.damage_types_qty)

    def __repr__(self):
        return f"<DamageComponent>"

    @property
    def avg(self):
        return (self.dice_number * (self.dice_type + 1) / 2) + self.constant


class HealingComponent:
    dice_type_distribution = ([4] * 12) + \
                             ([6] * 38) + \
                             ([8] * 30) + \
                             ([10] * 12) + \
                             ([12] * 6) + \
                             ([20] * 1) + \
                             ([100] * 1)

    def __init__(self):
        # ENSURE THE SEED IS ALREADY SET WHEN CREATING THIS COMPONENT!!!
        self.dice_number = random.randrange(1, 11)
        self.dice_type = random.sample(self.dice_type_distribution, 1)[0]
        self.constant = random.randrange(math.floor(-self.dice_type / 4), math.ceil(self.dice_type / 4) + 1)

    def __repr__(self):
        return f"<HealingComponent>"

    @property
    def avg(self):
        return (self.dice_number * (self.dice_type + 1) / 2) + self.constant


class StatsComponent:
    all_stats = ["Attacco", "Difesa", "Velocità", "Elusione", "Tenacia", "Rubavita",
                 "Vampirismo", "Forza", "Destrezza", "Costituzione", "Intelligenza",
                 "Saggezza", "Carisma", "Attacco Speciale", "Difesa Speciale",
                 "Eccellenza", "Immaginazione", "Cromosomi", "Timidezza", "Sonno",
                 "Elasticità", "Peso", "Sanità", "Appetito", "Fortuna", "Percezione",
                 "Determinazione", "Chips", "Mult", "Nucleare", "Psiche", "Psicologia",
                 "Garasauto", "Tifoseria", "Gioia", "Visione", "Visibilità", "Fuffa",
                 "Morbidezza", "Magia", "Spettacolo", "Appeal", "Infezione", "Infestazione"
                 "Genere"]

    change_distribution = (["--"] * 16) + \
                          (["-"] * 32) + \
                          (["+"] * 32) + \
                          (["++"] * 16) + \
                          (["×2"] * 2) + \
                          (["×3"] * 1)

    multistat_distribution = ([1] * 16) + \
                             ([2] * 8) + \
                             ([3] * 4) + \
                             ([5] * 2) + \
                             ([8] * 1)

    def __init__(self):
        # ENSURE THE SEED IS ALREADY SET WHEN CREATING THIS COMPONENT!!!
        self.stat_changes = {}
        self.stat_number = random.sample(self.multistat_distribution, 1)[0]
        available_stats = self.all_stats.copy()
        for _ in range(self.stat_number):
            stat = random.sample(available_stats, 1)[0]
            available_stats.remove(stat)
            change = random.sample(self.change_distribution, 1)[0]
            self.stat_changes[stat] = change

    def __repr__(self):
        return f"<StatsComponent>"


class StatusEffectComponent:
    all_status_effects = ["Bruciatura", "Sanguinamento", "Paralisi", "Veleno",
                          "Congelamento", "Iperveleno", "Sonno", "Stordimento",
                          "Rallentamento", "Radicamento", "Rigenerazione", "Morte",
                          "Affaticamento", "Glitch", "Accecamento", "Silenzio",
                          "Esilio", "Invisibilità", "Rapidità", "Splendore",
                          "Visione notturna", "Resistenza al fuoco", "Respirazione subacqua",
                          "Debolezza", "Slimed", "Jarate"]

    def __init__(self):
        # ENSURE THE SEED IS ALREADY SET WHEN CREATING THIS COMPONENT!!!
        self.chance = random.randrange(1, 103)
        self.effect = random.sample(self.all_status_effects, 1)[0]

    def __repr__(self):
        return f"<StatusEffectComponent>"


class Spell:
    version = "3.2"

    damaging_spell_chance = 0.9
    healing_spell_chance = 0.9  # If not a damaging spell
    additional_stats_chance = 0.1  # In addition to the damage/healing
    additional_status_effect_chance = 0.1  # In addition to the rest

    def __init__(self, name: str):
        seed = name.capitalize()
        random.seed(seed)
        # Spell name
        self.name = seed
        # Find the spell type
        self.spell_type = SpellType(0)
        if random.random() < self.damaging_spell_chance:
            self.spell_type |= SpellType.DAMAGING
        elif random.random() < self.healing_spell_chance:
            self.spell_type |= SpellType.HEALING
        if random.random() < self.additional_stats_chance:
            self.spell_type |= SpellType.STATS
        if random.random() < self.additional_status_effect_chance:
            self.spell_type |= SpellType.STATUS_EFFECT
        # Damaging spells
        if self.spell_type & SpellType.DAMAGING:
            self.damage_component = DamageComponent()
        else:
            self.damage_component = None
        # Healing spells
        if self.spell_type & SpellType.HEALING:
            self.healing_component = HealingComponent()
        else:
            self.healing_component = None
        # Stats spells
        if self.spell_type & SpellType.STATS:
            self.stats_component = StatsComponent()
        else:
            self.stats_component = None
        # Status effect spells
        if self.spell_type & SpellType.STATUS_EFFECT:
            self.status_effect_component = StatusEffectComponent()
        else:
            self.status_effect_component = None

    def __repr__(self):
        return f"<Spell {self.name}>"
