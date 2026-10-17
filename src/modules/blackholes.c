/* Stellarium Web Engine - Copyright (c) 2022 - Stellarium Labs SRL
 *
 * This program is licensed under the terms of the GNU AGPL v3, or
 * alternatively under a commercial licence.
 *
 * The terms of the AGPL v3 license can be found in the main directory of this
 * repository.
 */

#include "swe.h"

/*
 * Module: blackholes
 *
 * Renders known black holes (curated catalogue) as neon accretion-disk
 * markers at fixed ICRF positions, and exposes them to the search engine.
 *
 * The catalogue is a plain JSON array (see skydata/blackholes.json) with
 * entries like:
 *   { "name": "Ton 618", "ra": 187.104, "de": 31.4771, "kind": "SMBH",
 *     "mass": 6.6e10, "dist": 1.04e10, "host": "quasar",
 *     "aliases": ["TON 618"], "year": 1957, "approx": true }
 */

typedef struct blackhole {
    obj_t   obj;
    double  pos[3];         // Unit vector, ICRF.
    char    name[96];
    char    kind[16];       // "SMBH" or "stellar".
    double  mass;           // Solar masses (NaN if unknown).
    double  dist;           // Light years (NaN if unknown).
    char    host[128];
    char    aliases[256];   // '|' separated extra names.
    int     year;
    bool    approx;
} blackhole_t;

typedef struct blackholes {
    obj_t       obj;
    char        *source_url;
    bool        loaded;
    bool        visible;
    double      hints_mag_offset;
} blackholes_t;

static blackholes_t *g_blackholes = NULL;

static int bh_get_info(const obj_t *obj, const observer_t *obs, int info,
                       void *out)
{
    const blackhole_t *bh = (const blackhole_t*)obj;
    double pvo[2][4];
    switch (info) {
    case INFO_PVO:
        vec3_normalize(bh->pos, pvo[0]);
        convert_frame(obs, FRAME_ICRF, FRAME_ICRF, true, pvo[0], pvo[0]);
        pvo[0][3] = 0.0;
        vec4_set(pvo[1], 0, 0, 0, 0);
        memcpy(out, pvo, sizeof(pvo));
        return 0;
    default:
        return 1;
    }
}

static json_value *bh_get_json_data(const obj_t *obj)
{
    const blackhole_t *bh = (const blackhole_t*)obj;
    json_value *ret = json_object_new(0);
    json_value *names = json_array_new(0);
    json_value *types = json_array_new(0);
    json_value *md = json_object_new(0);
    const char *p;

    json_array_push(names, json_string_new(bh->name));
    p = bh->aliases;
    while (p && *p) {
        json_array_push(names, json_string_new(p));
        p += strlen(p) + 1;
    }

    json_array_push(types, json_string_new("Black hole"));

    json_object_push(md, "ra", json_double_new(atan2(bh->pos[1], bh->pos[0]) * DR2D));
    json_object_push(md, "de", json_double_new(asin(bh->pos[2]) * DR2D));
    if (bh->kind[0])
        json_object_push(md, "kind", json_string_new(bh->kind));
    if (!isnan(bh->mass))
        json_object_push(md, "mass", json_double_new(bh->mass));
    if (!isnan(bh->dist))
        json_object_push(md, "dist", json_double_new(bh->dist));
    if (bh->host[0])
        json_object_push(md, "host", json_string_new(bh->host));
    if (bh->year)
        json_object_push(md, "year", json_integer_new(bh->year));
    json_object_push(md, "approx", json_boolean_new(bh->approx));

    json_object_push(ret, "names", names);
    json_object_push(ret, "types", types);
    json_object_push(ret, "model", json_string_new("blackhole"));
    json_object_push(ret, "model_data", md);
    return ret;
}

static void bh_get_designations(
        const obj_t *obj, void *user,
        int (*f)(const obj_t *obj, void *user, const char *cat, const char *str))
{
    const blackhole_t *bh = (const blackhole_t*)obj;
    const char *p = bh->aliases;
    f(obj, user, NULL, bh->name);
    while (p && *p) {
        f(obj, user, NULL, p);
        p += strlen(p) + 1;
    }
}

static int bh_render(obj_t *obj, const painter_t *painter_)
{
    const blackhole_t *bh = (const blackhole_t*)obj;
    painter_t painter = *painter_;
    const bool selected = core->selection && obj == core->selection;
    double win_pos[2];
    double m[3][3];
    double R, col[4], disk[4], ring[4], black[4];
    char buf[128];
    int effects = 0;

    if (!g_blackholes || !g_blackholes->visible) return 0;

    // Project the fixed sky position to the screen.
    if (!painter_project(&painter, FRAME_ICRF, bh->pos, true, true, win_pos))
        return 0;

    // Constant on-screen size (independent of zoom).
    R = 10.0;
    if (selected) R += 4.0;

    vec4_set(black, 0.0, 0.0, 0.0, 0.9);
    vec4_set(disk, 1.0, 0.55, 0.15, 0.95);
    vec4_set(ring, 0.55, 0.95, 1.0, 1.0);

    // 1. Accretion disk: a tilted glowing ellipse.
    mat3_set_identity(m);
    mat3_itranslate(m, win_pos[0], win_pos[1]);
    mat3_rz(-0.45, m, m);
    mat3_iscale(m, R * 1.9, R * 0.7, 1.0);
    vec4_emul(painter_->color, disk, painter.color);
    painter.lines.width = 3.0;
    painter.lines.glow = 0.7;
    paint_2d_ellipse(&painter, m, 0, NULL, NULL, NULL);

    // 2. Event horizon: filled dark disc (thick stroked circle).
    mat3_set_identity(m);
    mat3_itranslate(m, win_pos[0], win_pos[1]);
    mat3_iscale(m, R * 0.4, R * 0.4, 1.0);
    vec4_emul(painter_->color, black, painter.color);
    painter.lines.width = R * 0.8;
    painter.lines.glow = 0.0;
    paint_2d_ellipse(&painter, m, 0, NULL, NULL, NULL);

    // 3. Photon ring.
    mat3_set_identity(m);
    mat3_itranslate(m, win_pos[0], win_pos[1]);
    mat3_iscale(m, R * 0.8, R * 0.8, 1.0);
    vec4_emul(painter_->color, ring, painter.color);
    painter.lines.width = 2.0;
    painter.lines.glow = 0.8;
    paint_2d_ellipse(&painter, m, 0, NULL, NULL, NULL);

    // 4. Selection highlight.
    if (selected) {
        mat3_set_identity(m);
        mat3_itranslate(m, win_pos[0], win_pos[1]);
        mat3_iscale(m, R * 1.25, R * 1.25, 1.0);
        vec4_set(painter.color, 1, 1, 1, 1);
        painter.lines.width = 2.0;
        painter.lines.glow = 0.6;
        paint_2d_ellipse(&painter, m, M_PI / 8, NULL, NULL, NULL);
    }

    areas_add_circle(core->areas, win_pos, R * 1.4, obj);

    // Label: only when selected or zoomed in enough to avoid clutter.
    if (bh->name[0] && (selected || core->fov < 45 * DD2R)) {
        effects = TEXT_BOLD | (selected ? 0 : TEXT_FLOAT);
        vec4_set(col, 0.6, 0.98, 1.0, selected ? 1.0 : 0.85);
        snprintf(buf, sizeof(buf), "%s", bh->name);
        labels_add_3d(buf, FRAME_ICRF, bh->pos, true, R * 1.2,
                      FONT_SIZE_BASE - 2, col, 0, 0, effects, -100.0, obj);
    }
    return 0;
}

static obj_klass_t blackhole_klass = {
    .id = "blackhole",
    .size = sizeof(blackhole_t),
    .get_info = bh_get_info,
    .get_json_data = bh_get_json_data,
    .get_designations = bh_get_designations,
    .render = bh_render,
};
OBJ_REGISTER(blackhole_klass)

static void parse_aliases(const json_value *e, char *out, size_t out_size)
{
    const json_value *aliases = json_get_attr(e, "aliases", json_array);
    size_t ofs = 0;
    int i;
    out[0] = '\0';
    if (!aliases) return;
    for (i = 0; i < aliases->u.array.length; i++) {
        const json_value *v = aliases->u.array.values[i];
        const char *s;
        int len;
        if (v->type != json_string) continue;
        s = v->u.string.ptr;
        len = v->u.string.length;
        if (ofs + len + 2 >= out_size) break;
        memcpy(out + ofs, s, len);
        out[ofs + len] = '\0';
        ofs += len + 1;
    }
    out[ofs] = '\0';
}

static void blackholes_load(blackholes_t *mod, const void *data, int size)
{
    json_value *root;
    int i, nb = 0;

    root = json_parse(data, size);
    if (!root || root->type != json_array) {
        LOG_W("blackholes: cannot parse catalogue");
        if (root) json_value_free(root);
        return;
    }

    for (i = 0; i < root->u.array.length; i++) {
        const json_value *e = root->u.array.values[i];
        const char *name, *kind, *host;
        blackhole_t *bh;
        double ra, de;

        if (e->type != json_object) continue;
        name = json_get_attr_s(e, "name");
        if (!name) continue;

        bh = (blackhole_t*)obj_create("blackhole", NULL);
        snprintf(bh->name, sizeof(bh->name), "%s", name);
        kind = json_get_attr_s(e, "kind");
        if (kind) snprintf(bh->kind, sizeof(bh->kind), "%s", kind);
        host = json_get_attr_s(e, "host");
        if (host) snprintf(bh->host, sizeof(bh->host), "%s", host);
        parse_aliases(e, bh->aliases, sizeof(bh->aliases));
        bh->mass = json_get_attr_f(e, "mass", NAN);
        bh->dist = json_get_attr_f(e, "dist", NAN);
        bh->year = json_get_attr_i(e, "year", 0);
        bh->approx = json_get_attr_b(e, "approx", false);

        ra = json_get_attr_f(e, "ra", 0.0) * DD2R;
        de = json_get_attr_f(e, "de", 0.0) * DD2R;
        vec3_from_sphe(ra, de, bh->pos);

        module_add((obj_t*)mod, (obj_t*)bh);
        obj_release((obj_t*)bh);
        nb++;
    }
    json_value_free(root);
    LOG_I("blackholes: loaded %d entries", nb);
}

static int blackholes_add_data_source(obj_t *obj, const char *url,
                                      const char *key)
{
    blackholes_t *mod = (void*)obj;
    free(mod->source_url);
    mod->source_url = strdup(url);
    mod->loaded = false;
    return 0;
}

static int blackholes_update(obj_t *obj, double dt)
{
    blackholes_t *mod = (void*)obj;
    const void *data;
    int size, code;

    if (mod->loaded || !mod->source_url) return 0;
    data = asset_get_data(mod->source_url, &size, &code);
    if (!data && code < 400) return 0;   // Still loading.
    if (data) blackholes_load(mod, data, size);
    mod->loaded = true;
    return 0;
}

static int blackholes_render(obj_t *obj, const painter_t *painter)
{
    obj_t *child;
    (void)obj;
    DL_FOREACH(obj->children, child)
        obj_render(child, painter);
    return 0;
}

static int blackholes_init(obj_t *obj, json_value *args)
{
    blackholes_t *mod = (void*)obj;
    mod->visible = true;
    mod->hints_mag_offset = 0.0;
    g_blackholes = mod;
    return 0;
}

static obj_klass_t blackholes_klass = {
    .id = "blackholes",
    .size = sizeof(blackholes_t),
    .flags = OBJ_IN_JSON_TREE | OBJ_MODULE | OBJ_LISTABLE,
    .init = blackholes_init,
    .update = blackholes_update,
    .render = blackholes_render,
    .add_data_source = blackholes_add_data_source,
    .render_order = 32,
    .attributes = (attribute_t[]) {
        PROPERTY(visible, TYPE_BOOL, MEMBER(blackholes_t, visible)),
        PROPERTY(hints_mag_offset, TYPE_FLOAT,
                 MEMBER(blackholes_t, hints_mag_offset)),
        {}
    },
};
OBJ_REGISTER(blackholes_klass)
