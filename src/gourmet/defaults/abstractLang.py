from typing import Any, Collection, List, Mapping, Optional, Sequence, Tuple


class AbstractLanguage:

    """
    Translator credits
    """
    CREDITS: str

    """
    used to determine some things about how to handle this language
    {'hasAccents':True, 'capitalisedNouns':True,'useFractions':False}
    """
    LANG_PROPERTIES: Mapping[str, bool]

    """
    Gourmet's standard fields and the default categories
    """
    fields: Mapping[str, List[str]]

    """
    List for synonyms  ["preferred word","alternate word","alternate word"]
    TODO: "preferred" semantic inconsistent with UNITS
    """
    SYNONYMS: Collection[List[str]]

    """
    DICTIONARY CONTAINING INGREDIENT KEYS AND NDBNO for the USDA (not used)
    """
    NUTRITIONAL_INFO: Mapping[str, Any]

    """
    Dictionary for ambiguous words. key=ambiguous word, value=list of possible non-ambiguous term
    """
    AMBIGUOUS: Mapping[str, List[str]]

    """
    Triples ITEM, KEY, SHOPPING CATEGORY. These will be defaults.
    They should include whatever foods might be standard for your
    locale, with whatever sensible default categories you can think of
    TODO: Languages actually have lists instead of 3-tuples
    """
    INGREDIENT_DATA: Collection[Tuple[str, str, str]]

    """
    THESE ARE STANDARD UNIT CONVERSIONS.
    ("unit1","unit2"):conversion_factor, where unit1 contains conversion_factor X unit2
    For example: 1 cup has 16 tablespoons.
    """
    CONVERTER_TABLE: Mapping[Tuple[str, str], float]

    """
    DENSITIES of common foods. This allows us to convert between mass and volume.
    """
    DENSITY_TABLE: Mapping[str, float]

    """
    Standard unit names and alternate unit names that might appear.  For
    example: "c." is our standard abbreviation for cup.  "cup","c." or
    "cups" might appear in a recipe we are importing.  Each item of this
    list looks like this:
    ["standard", ["alternate1","alternate2","alternate3",...]]

    The first item should be the preferred abbreviation
    The second item should be the full name of the unit
    e.g. ["c.", ["cup",...]]
    TODO: "preferred" semantic inconsistent with SYNONYMS
    """
    UNITS: Collection[Tuple[str, Collection[str]]]

    """
    Group of units that "follow" each other in magnitude.
    Mapping name of quantity to List of Ranges.
    A range might be open-ended
    TODO: Since dictionaries are now ordered, this could be used as values

    {  'metric mass':[('mg',(1,999)),
                       ('g',(1,999)),
                       ('kg',(1,None))] }
    """
    UNIT_GROUPS: Mapping[str, Sequence[Tuple[str, Tuple[float, Optional[float]]]]]

    """
    This if for units that require an additional
    bit of information -- i.e. to convert between
    volume and mass you need the density of an
    item.  In these cases, the additional factor
    will be provided as an 'item' that is then looked
    up in the dictionary referenced here (i.e. the density_table)
    currently, 'density' is the only keyword used
    The units here need to correspond to the standard unit names defined
    above in UNITS
    { ("pt", "lb"):['density',1], }
    TODO: The value is not actually a dictionary but should be
    TODO: Actual languages use List instead of Tuple
    """
    CROSS_UNIT_TABLE: Mapping[Tuple[str, str], Tuple[str, float]]

    """
    These are some core conversions from mass-to-volume,
    assuming a density of 1 (i.e. the density of water).
    The units here need to correspond to the standard unit names defined
    in UNITS.
    { ("pt", "lb") : 1 }
    """
    VOL_TO_MASS_TABLE: Mapping[Tuple[str, str], float]

    """
    TIME ABBREVIATIONS
    { 'sec':'seconds', }
    """
    TIME_ABBREVIATIONS: Mapping[str, str]

    """
    Guess possible singulars from a plural (for ingredients?)
    TODO: we could also annotate this as Callable without providing a default
    """
    @staticmethod
    def guess_singulars(plural: str) -> Collection[str]:
        raise NotImplementedError()

    """
    Guess possible plurals from a singular (for ingredients?)
    TODO: we could also annotate this as Callable without providing a default
    """
    @staticmethod
    def guess_plurals (singular: str) -> Collection[str]:
        raise NotImplementedError()

    """
    Words to ignore (and, or, other fillers)
    """
    IGNORE: Collection[str]

    """
    Number Names
    TODO: this dictionary seems reversed, the numbers should probably be fractions
    """
    NUMBERS: Mapping[float, Collection[str]]

    """
    plurar forms of amounts and serving sizes
    [ ('box','boxes'), ]
    TODO: This should probably be a mapping
    """
    PLURALS: Collection[Tuple[str, str]]

    """
    The following values are set from outside (defaults.py)
    """
    keydic: Mapping[str, List[str]]
    shopdic: Mapping[str, str]
    unit_group_lookup: Mapping[str, Tuple[str, int]]
    unit_rounding_guide: Mapping[str, float]
