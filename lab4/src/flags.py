FLAGS = {
    'ftl50': (-50, 39), 'ftl40': (-40, 39), 'ftl30': (-30, 39), 'ftl20': (-20, 39),
    'ftl10': (-10, 39), 'ft0': (0, 39), 'ftr10': (10, 39), 'ftr20': (20, 39),
    'ftr30': (30, 39), 'ftr40': (40, 39), 'ftr50': (50, 39),
    'fbl50': (-50, -39), 'fbl40': (-40, -39), 'fbl30': (-30, -39), 'fbl20': (-20, -39),
    'fbl10': (-10, -39), 'fb': (0, -39), 'fbr10': (10, -39), 'fbr20': (20, -39),
    'fbr30': (30, -39), 'fbr40': (40, -39), 'fbr50': (50, -39),
    'flt30': (-57.5, 30), 'flt20': (-57.5, 20), 'flt10': (-57.5, 10), 'fl0': (-57.5, 0),
    'flb10': (-57.5, -10), 'flb20': (-57.5, -20), 'flb30': (-57.5, -30),
    'frt30': (57.5, 30), 'frt20': (57.5, 20), 'frt10': (57.5, 10), 'fr0': (57.5, 0),
    'frb10': (57.5, -10), 'frb20': (57.5, -20), 'frb30': (57.5, -30),
    'fglt': (-52.5, 7.01), 'fglb': (-52.5, -7.01), 'gl': (-52.5, 0), 'gr': (52.5, 0),
    'fc': (0, 0),
    'fplt': (-36, 20.15), 'fplc': (-36, 0), 'fplb': (-36, -20.15),
    'fgrt': (52.5, 7.01), 'fgrb': (52.5, -7.01), 'fprt': (36, 20.15), 'fprc': (36, 0), 'fprb': (36, -20.15),
    'flt': (-52.5, 34), 'fct': (0, 34), 'frt': (52.5, 34),
    'flb': (-52.5, -34), 'fcb': (0, -34), 'frb': (52.5, -34),
}


def _name_parts_from_see_obj(ob):
    """Из объекта see (dict с 'p') извлекаем список частей имени: ['b'] или ['f','c'], ['p','teamA',1] и т.д."""
    if not ob or 'p' not in ob or not ob['p']:
        return []
    first = ob['p'][0]
    if isinstance(first, dict) and 'p' in first:
        return first['p']
    return [first]


def obj_name_to_key(name_parts):
    """Ключ для словаря видимых объектов: 'b', 'fc', 'pteamA1' и т.д."""
    return ''.join(str(x).strip('"') for x in name_parts)


def flag_key_from_see(ob):
    """Ключ флага из объекта see, если это известный флаг."""
    key = obj_name_to_key(_name_parts_from_see_obj(ob))
    return key if key in FLAGS else None


def get_visible_objects_from_see(see_res):
    """
    Строит словарь visible_objects из нашего формата see (dict с cmd, p).
    Ключ — obj_name_to_key, значение — {name, dist, dir (angle)}.
    """
    if see_res.get('cmd') != 'see' or len(see_res['p']) < 2:
        return {}
    out = {}
    for i in range(2, len(see_res['p'])):
        ob = see_res['p'][i]
        if not isinstance(ob, dict) or 'p' not in ob or len(ob['p']) < 3:
            continue
        arr = ob['p']
        nums = [x for x in arr if isinstance(x, (int, float))]
        if len(nums) < 2:
            continue
        dist, angle = float(nums[0]), float(nums[1])
        name_parts = _name_parts_from_see_obj(ob)
        if not name_parts:
            continue
        key = obj_name_to_key(name_parts)
        out[key] = {'name': name_parts, 'dist': dist, 'dir': angle}
    return out


def get_visible_flags(see_res):
    """Список {key, dist, angle} для флагов из see (для position_from_three_flags)."""
    objs = get_visible_objects_from_see(see_res)
    return [{'key': k, 'dist': v['dist'], 'angle': v['dir']}
             for k, v in objs.items() if k in FLAGS]
