

# 3rd party - try embedded first (for QGIS), fallback to normal import (for CLI)
try:
    from .external import xlsxwriter
except ImportError:
    import xlsxwriter

# import tactis_utils
# Requiert Quickinteg
import logging
import sqlite3
from pathlib import Path

from . import processing_logging
from .excel_shortcut import read_excel_sheet_to_tab
from .spatialiteio import extract_table_to_file

module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)


def log(message, logLevel="info"):
    processing_logging.log(str(message), module_logger, logLevel)


nombre_iteration = 15
param_cb_id = "cb_codeext"
param_bp_id = "bp_codeext"
param_lg_cable = "cb_lgreel"
param_ti_id = "ti_etiquet"
param_st_id = "st_code"  # Site technique en V2 ou Local Technique en V3. Valeurs possible :st_code, st_codeext, st_nom, lc_code, lc_codeext, lc_etiquet
grace_version = 2
ropt_prefixe_di = "v_ropt_full_di_"
ropt_prefixe_tr = "v_ropt_full_tr_"
mode = "table"  # autre choix : view crée des table ou des vues

# db_file = 'C:\\Users\\Valerian\\Desktop\\SICTIAM\\EXE-MS5-LO1-VALBERG\\Tactis\\Integ\\gracethd_v2.0.1.sqlite'
# qfd = QFileDialog()
# db_file = qfd.getOpenFileName(None, 'Sélectionner la base sqlite')[0]


def generate_sql_ropt_full_v3(n_iteration, prefix_sql_view):
    """génération ropt par récursivité ( paramètre récursift : n_iteration)
    On crée une vue partant des positions attenantes aux tiroirs des SRO
    et on itère à partir de cette vue (de ps1 vers ps2)
    Requête adaptée pour GRACE V3.x"""
    req = ""
    # itération 0 départ à partir des tiroirs
    if n_iteration == 0:
        viewname = prefix_sql_view + "it0"
        # 'it' pour itération
        # Pour l'itération 0 on part des tiroir et on récupère les éléments
        # à partir des positions attenantes au tiroir
        req += f"DROP {mode} IF EXISTS {viewname}; \n"
        req += f"CREATE {mode} {viewname} AS \n"
        req += "SELECT lc_code as it0_lc_code,\n"
        req += "lc_codeext AS it0_lc_codeext, \n"
        req += "lc_etiquet AS it0_lc_etiquet, \n"
        req += "ti_code AS it0_ti_code, \n"
        req += "ti_etiquet AS it0_ti_etiquet, \n"
        req += "ti_codeext AS it0_ti_codeext, \n"
        req += "ps_code AS it0_ps_code, \n"
        req += "ps_numero AS it0_ps_numero, \n"
        req += "ps_type AS it0_ps_type, \n"
        req += "ps_fonct AS it0_ps_fonct, \n"
        req += "ps_preaff AS it0_ps_preaff, \n"
        req += "ps_1 AS it0_ps_1, \n"
        req += "ps_2 AS it0_ps_2, \n"
        req += "cs_num AS it0_cs_num, \n"
        req += "fo_numtub AS it0_fo_numtub, \n"
        req += "fo_nintub AS it0_fo_nintub,  \n"
        req += "cb_code AS it0_cb_code, \n"
        req += "cb_etiquet AS it0_cb_etiquet, \n"
        req += "cb_codeext AS it0_cb_codeext, \n"
        req += "cb_capafo AS it0_capafo,  \n"
        req += "cb_typelog AS it0_cb_typelog, \n"
        req += "cb_lgreel AS it0_cb_lgreel, \n"
        req += "cl_long AS it0_cl_long \n"
        req += "FROM t_position \n"
        req += "LEFT JOIN t_tiroir ON ti_code = ps_ti_code \n"
        req += "LEFT JOIN t_cassette ON cs_code = ps_cs_code \n"  # ajout spécifique CG57
        req += "LEFT JOIN t_fibre ON ps_2 = fo_code \n"
        req += "LEFT JOIN t_cable on cb_code = fo_cb_code \n"
        req += "LEFT JOIN t_cableline on cb_code = cl_cb_code \n"
        req += "LEFT JOIN t_baie on ba_code = ti_ba_code \n"
        req += "LEFT JOIN t_local on lc_code = ba_lc_code \n"
        req += "LEFT JOIN t_site on st_code = lc_st_code \n"
        req += "WHERE it0_ti_code NOT NULL\n"
        req += "ORDER BY it0_ti_code ASC, cs_num, it0_ps_numero ASC; \n\n"  # ajout spécifique CG57 (cs_num)
    # si n supérieur à 0, construction de l'itération à partir de la vue n-1
    elif n_iteration > 0:
        # calcul  du nom de la vue à calculer
        viewname = prefix_sql_view + "it%s" % (str(n_iteration))
        # calcul du nom de la vue parente n-1
        parent_view = prefix_sql_view + "it%s" % (str(n_iteration - 1))

        # On construit la requête pour la vue n-1
        req = generate_sql_ropt_full_v3(n_iteration - 1, prefix_sql_view)
        # On construit la requête pour la vue n :
        # On fait un LEFT JOIN à partir des positions attenantes en partant de la vue n-1 (FROM)
        req += f"DROP {mode} IF EXISTS {viewname}; \n"
        req += f"CREATE {mode} {viewname} AS \n"
        # On récupère toutes les colonnes de la vue n-1
        req += "SELECT %s.*, \n" % (parent_view)
        # On récupère les colonnes de la vue n
        req += "bp_code AS it%s_bp_code, \n" % (str(n_iteration))
        req += "bp_etiquet AS it%s_bp_etiquet, \n" % (str(n_iteration))
        req += "bp_codeext AS it%s_bp_codeext, \n" % (str(n_iteration))
        req += "ti_code AS it%s_ti_code, \n" % (str(n_iteration))
        req += "ti_etiquet AS it%s_ti_etiquet, \n" % (str(n_iteration))
        req += "ti_codeext AS it%s_ti_codeext, \n" % (str(n_iteration))
        req += "ps_code AS it%s_ps_code, \n" % (str(n_iteration))
        req += "ps_numero AS it%s_ps_numero, \n" % (str(n_iteration))
        req += "ps_type AS it%s_ps_type, \n" % (str(n_iteration))
        req += "ps_fonct AS it%s_ps_fonct, \n" % (str(n_iteration))
        req += "ps_preaff AS it%s_ps_preaff, \n" % (str(n_iteration))
        req += "ps_1 AS it%s_ps_1, \n" % (str(n_iteration))
        req += "ps_2 AS it%s_ps_2, \n" % (str(n_iteration))
        req += "cs_num AS it%s_cs_num, \n" % (str(n_iteration))
        req += "fo_numtub AS it%s_fo_numtub, \n" % (str(n_iteration))
        req += "fo_nintub AS it%s_fo_nintub,  \n" % (str(n_iteration))
        req += "cb_code AS it%s_cb_code, \n" % (str(n_iteration))
        req += "cb_etiquet AS it%s_cb_etiquet, \n" % (str(n_iteration))
        req += "cb_codeext AS it%s_cb_codeext, \n" % (str(n_iteration))
        req += "cb_capafo AS it%s_capafo,  \n" % (str(n_iteration))
        req += "cb_typelog AS it%s_cb_typelog, \n" % (str(n_iteration))
        req += "cb_lgreel AS it%s_cb_lgreel, \n" % (str(n_iteration))
        req += "cl_long AS it%s_cl_long \n" % (str(n_iteration))
        req += "FROM %s \n" % (parent_view)
        req += "LEFT JOIN t_position ON ps_1 = it%s_ps_2 \n" % (str(n_iteration - 1))
        req += "LEFT JOIN t_cassette ON cs_code = t_position.ps_cs_code \n"
        req += "LEFT JOIN t_ebp ON bp_code = cs_bp_code \n"
        req += "LEFT JOIN t_tiroir ON ti_code = t_position.ps_ti_code \n"
        req += "LEFT JOIN t_fibre ON ps_2 = fo_code \n"
        req += "LEFT JOIN t_cable on cb_code = fo_cb_code\n"
        req += "LEFT JOIN t_cableline on cb_code = cl_cb_code; \n\n"

    # log(req)
    return req


def generate_sql_ropt_full_v2(n_iteration, prefix_sql_view):
    """génération ropt par récursivité ( paramètre récursift : n_iteration)
    On crée une vue partant des positions attenantes aux tiroirs des SRO
    et on itère à partir de cette vue (de ps1 vers ps2)
    Requête adaptée pour GRACE V32x
    """
    req = ""
    # itération 0 départ à partir des tiroirs
    if n_iteration == 0:
        viewname = prefix_sql_view + "it0"
        # 'it' pour itération
        # Pour l'itération 0 on part des tiroir et on récupère les éléments
        # à partir des positions attenantes au tiroir
        req += f"DROP {mode} IF EXISTS {viewname}; \n"
        req += f"CREATE {mode} {viewname} AS \n"
        req += "SELECT st_code as it0_st_code,\n"
        req += "st_codeext AS it0_st_codeext, \n"
        req += "st_nom AS it0_st_nom, \n"
        req += "ti_code AS it0_ti_code, \n"
        req += "ti_etiquet AS it0_ti_etiquet, \n"
        req += "ti_codeext AS it0_ti_codeext, \n"
        req += "ps_code AS it0_ps_code, \n"
        req += "ps_numero AS it0_ps_numero, \n"
        req += "ps_type AS it0_ps_type, \n"
        req += "ps_fonct AS it0_ps_fonct, \n"
        req += "ps_preaff AS it0_ps_preaff, \n"
        req += "ps_1 AS it0_ps_1, \n"
        req += "ps_2 AS it0_ps_2, \n"
        req += "cs_num AS it0_cs_num, \n"
        req += "fo_numtub AS it0_fo_numtub, \n"
        req += "fo_nintub AS it0_fo_nintub,  \n"
        req += "cb_code AS it0_cb_code, \n"
        req += "cb_etiquet AS it0_cb_etiquet, \n"
        req += "cb_codeext AS it0_cb_codeext, \n"
        req += "cb_capafo AS it0_capafo,  \n"
        req += "cb_typelog AS it0_cb_typelog, \n"
        req += "cb_lgreel AS it0_cb_lgreel, \n"
        req += "cl_long AS it0_cl_long \n"
        req += "FROM t_position \n"
        req += "LEFT JOIN t_tiroir ON ti_code = ps_ti_code \n"
        req += "LEFT JOIN t_cassette ON cs_code = ps_cs_code \n"  # ajout spécifique CG57
        req += "LEFT JOIN t_fibre ON ps_2 = fo_code \n"
        req += "LEFT JOIN t_cable on cb_code = fo_cb_code \n"
        req += "LEFT JOIN t_cableline on cb_code = cl_cb_code \n"
        req += "LEFT JOIN t_baie on ba_code = ti_ba_code \n"
        req += "LEFT JOIN t_ltech on lt_code = ba_lt_code \n"
        req += "LEFT JOIN t_sitetech on st_code = lt_st_code \n"
        req += "WHERE it0_ti_code NOT NULL\n"
        req += "ORDER BY it0_ti_code ASC, cs_num, it0_ps_numero ASC; \n\n"  # ajout spécifique CG57 (cs_num)
    # si n supérieur à 0, construction de l'itération à partir de la vue n-1
    elif n_iteration > 0:
        # calcul  du nom de la vue à calculer
        viewname = prefix_sql_view + "it%s" % (str(n_iteration))
        # calcul du nom de la vue parente n-1
        parent_view = prefix_sql_view + "it%s" % (str(n_iteration - 1))

        # On construit la requête pour la vue n-1
        req = generate_sql_ropt_full_v2(n_iteration - 1, prefix_sql_view)
        # On construit la requête pour la vue n :
        # On fait un LEFT JOIN à partir des positions attenantes en partant de la vue n-1 (FROM)
        req += f"DROP {mode} IF EXISTS {viewname}; \n"
        req += f"CREATE {mode} {viewname} AS \n"
        # On récupère toutes les colonnes de la vue n-1
        req += "SELECT %s.*, \n" % (parent_view)
        # On récupère les colonnes de la vue n
        req += "bp_code AS it%s_bp_code, \n" % (str(n_iteration))
        req += "bp_etiquet AS it%s_bp_etiquet, \n" % (str(n_iteration))
        req += "bp_codeext AS it%s_bp_codeext, \n" % (str(n_iteration))
        req += "ti_code AS it%s_ti_code, \n" % (str(n_iteration))
        req += "ti_etiquet AS it%s_ti_etiquet, \n" % (str(n_iteration))
        req += "ti_codeext AS it%s_ti_codeext, \n" % (str(n_iteration))
        req += "ps_code AS it%s_ps_code, \n" % (str(n_iteration))
        req += "ps_numero AS it%s_ps_numero, \n" % (str(n_iteration))
        req += "ps_type AS it%s_ps_type, \n" % (str(n_iteration))
        req += "ps_fonct AS it%s_ps_fonct, \n" % (str(n_iteration))
        req += "ps_preaff AS it%s_ps_preaff, \n" % (str(n_iteration))
        req += "ps_1 AS it%s_ps_1, \n" % (str(n_iteration))
        req += "ps_2 AS it%s_ps_2, \n" % (str(n_iteration))
        req += "cs_num AS it%s_cs_num, \n" % (str(n_iteration))
        req += "fo_numtub AS it%s_fo_numtub, \n" % (str(n_iteration))
        req += "fo_nintub AS it%s_fo_nintub,  \n" % (str(n_iteration))
        req += "cb_code AS it%s_cb_code, \n" % (str(n_iteration))
        req += "cb_etiquet AS it%s_cb_etiquet, \n" % (str(n_iteration))
        req += "cb_codeext AS it%s_cb_codeext, \n" % (str(n_iteration))
        req += "cb_capafo AS it%s_capafo,  \n" % (str(n_iteration))
        req += "cb_typelog AS it%s_cb_typelog, \n" % (str(n_iteration))
        req += "cb_lgreel AS it%s_cb_lgreel, \n" % (str(n_iteration))
        req += "cl_long AS it%s_cl_long \n" % (str(n_iteration))
        req += "FROM %s \n" % (parent_view)
        req += "LEFT JOIN t_position ON ps_1 = it%s_ps_2 \n" % (str(n_iteration - 1))
        req += "LEFT JOIN t_cassette ON cs_code = t_position.ps_cs_code \n"
        req += "LEFT JOIN t_ebp ON bp_code = cs_bp_code \n"
        req += "LEFT JOIN t_tiroir ON ti_code = t_position.ps_ti_code \n"
        req += "LEFT JOIN t_fibre ON ps_2 = fo_code \n"
        req += "LEFT JOIN t_cable on cb_code = fo_cb_code\n"
        req += "LEFT JOIN t_cableline on cb_code = cl_cb_code; \n\n"

    # log(req)
    return req


def create_tables_ropt(spl_db, n_iteration, prefix_sql_view):
    """Execute le SQL généré par la fonction generate_sql_ropt_full sur la base cible"""
    if grace_version == 2:
        req = generate_sql_ropt_full_v2(n_iteration, prefix_sql_view)
    elif grace_version == 3:
        req = generate_sql_ropt_full_v3(n_iteration, prefix_sql_view)
    else:
        raise ValueError("La version de GRACE doit être 2 ou 3")
    spl_connection = sqlite3.connect(spl_db)
    with spl_connection:
        spl_connection.executescript(req)
    spl_connection.close()


def create_view_ropt_light_sro(
    spl_db,
    sro,
    n_iteration,
    view_ropt_full_name,
    segment="DI",
    cb_id="cb_code",
    bp_id="bp_code",
    ti_id="ti_code",
    lg_cable="cb_lgreel",
    st_id="st_code",
):
    """extraction et renommage des colonnes pour la ropt light, avec sélection sur un SRO"""
    # TODO : trouver une solution propre pour le paramètre view_ropt_full_name, redondant avec n_iteration
    view_name = "ropt_%s_%s" % (sro.replace("-", "_").replace(" ", "_"), segment)
    req = ""
    req += "DROP VIEW IF EXISTS %s; \n" % (view_name)
    req += "CREATE VIEW %s AS \n" % (view_name)
    req += "SELECT it0_%s AS SRO, \n" % (st_id)
    req += "it0_%s AS TIROIR, \n" % (ti_id)
    req += "it0_cs_num AS CS_NUM, \n"
    req += "it0_ps_numero AS PS_NUM, \n"
    # Calcul de la destination
    coalesce_args = ", ".join(
        ["it%s_%s, it%s_%s" % (i, bp_id, i, ti_id) for i in range(n_iteration, 0, -1)]
    )
    req += "COALESCE(%s) AS Destination,\n" % (coalesce_args)
    req += '"" AS void, \n'
    req += "it0_ps_fonct AS FONCT, \n"
    req += "it0_%s AS CABLE, \n" % (cb_id)
    req += "it0_capafo AS CAPA, \n"
    req += "it0_fo_numtub AS TUBE, \n"
    req += "it0_fo_nintub AS FO, \n"
    req += "it0_ps_preaff AS PREAFF, \n"
    req += "it0_%s AS 'LONG', \n\n" % (lg_cable)

    for i in range(1, n_iteration + 1):
        req += "COALESCE (it%s_%s, it%s_%s, '') AS BPE_%s, \n" % (
            str(i),
            bp_id,
            str(i),
            ti_id,
            str(i),
        )
        req += "it%s_ps_fonct AS FONCT_%s, \n" % (str(i), str(i))
        req += "it%s_%s AS CABLE_%s, \n" % (str(i), cb_id, str(i))
        req += "it%s_capafo AS CAPA_%s, \n" % (str(i), str(i))
        req += "it%s_fo_numtub AS TUBE_%s, \n" % (str(i), str(i))
        req += "it%s_fo_nintub AS FO_%s, \n" % (str(i), str(i))
        req += "it%s_ps_preaff AS PREAFF_%s, \n" % (str(i), str(i))
        # pas de virgule sur la dernière itération
        if i == n_iteration:
            req += "it%s_%s AS 'LONG_%s' \n\n" % (str(i), lg_cable, str(i))
        else:
            req += "it%s_%s AS 'LONG_%s', \n\n" % (str(i), lg_cable, str(i))
    req += "FROM %s\n" % (view_ropt_full_name)
    req += "WHERE it0_%s = '%s' AND it0_cb_typelog = '%s'; \n\n\n" % (
        st_id,
        sro,
        segment,
    )
    spl_connection = sqlite3.connect(spl_db)
    with spl_connection:
        spl_connection.executescript(req)
    spl_connection.close()
    return view_name


def format_ropt(file_path, col_fonct=1, col_numtube=4, col_numfo=5, col_long=7, nb_col=8, offset=5):
    """Ajoute le format au fichier excel ropt. xlsxwriter ne peut pas modifier l'existant.
    Donc on lit avec openpyxl, puis on réecrit avec le format avec xlsxwriter
    les index col_fonct, col_numtube ... indiquent la positiond des colonnes correspondantes et commencent à 0
    """
    log(file_path)
    # On lit le fchier excel et récupère une liste[] de header et un tab[][] de data.
    dict_xl = read_excel_sheet_to_tab(file_path)
    header = dict_xl["header"]
    data = dict_xl["data"]

    # ouverture en écriture du fichier excel
    wb = xlsxwriter.Workbook(file_path)
    sheet = wb.add_worksheet()

    # On fige la première ligne et les premières colonnes :
    sheet.freeze_panes(1, offset)

    #   définition des formats
    # Format header
    format_header = wb.add_format()
    format_header.set_bold()
    format_header.set_bg_color("yellow")
    format_header.set_top(3)
    format_header.set_bottom(3)
    format_header.set_left(4)
    format_header.set_right(4)
    format_header.set_align("center")

    # Format fo_color
    # On créer la liste des couleurs FO pour créer la liste de format associés
    format_fo_color = []
    fo_colors = [
        "red",
        "blue",
        "green",
        "yellow",
        "purple",
        "white",
        "orange",
        "gray",
        "brown",
        "black",
        "cyan",
        "pink",
    ]
    for i in range(12):
        format_fo_color.append(wb.add_format())
        format_fo_color[i].set_bg_color(fo_colors[i])
        format_fo_color[i].set_top(3)
        format_fo_color[i].set_bottom(3)
        format_fo_color[i].set_left(4)
        format_fo_color[i].set_right(4)
        format_fo_color[i].set_align("center")
        if (fo_colors[i] == "black") or (fo_colors[i] == "blue"):
            format_fo_color[i].set_font_color("white")

    # Format colonne longueur
    format_long = wb.add_format()
    format_long.set_top(3)
    format_long.set_bottom(3)
    format_long.set_left(4)
    format_long.set_right(4)
    format_long.set_align("center")
    format_long.set_num_format('0 "ml"')
    format_long.set_italic()

    # Format fonction de la position
    # 5 valeurs possible pour les fonction (PA EP PI AT CO)
    format_fonct = {
        "CO": wb.add_format(),
        "EP": wb.add_format(),
        "AT": wb.add_format(),
        "PA": wb.add_format(),
        "PI": wb.add_format(),
        "MA": wb.add_format(),
    }
    format_fonct["PA"].set_top(3)
    format_fonct["PA"].set_bottom(3)
    format_fonct["PA"].set_left(4)
    format_fonct["PA"].set_right(4)
    format_fonct["PA"].set_align("center")
    format_fonct["PA"].set_italic()

    format_fonct["EP"].set_top(3)
    format_fonct["EP"].set_bottom(3)
    format_fonct["EP"].set_left(4)
    format_fonct["EP"].set_right(4)
    format_fonct["EP"].set_align("center")
    format_fonct["EP"].set_bold()

    format_fonct["CO"].set_top(3)
    format_fonct["CO"].set_bottom(3)
    format_fonct["CO"].set_left(4)
    format_fonct["CO"].set_right(4)
    format_fonct["CO"].set_align("center")
    format_fonct["CO"].set_bold()

    format_fonct["AT"].set_top(3)
    format_fonct["AT"].set_bottom(3)
    format_fonct["AT"].set_left(4)
    format_fonct["AT"].set_right(6)  # double line
    format_fonct["AT"].set_align("center")

    format_fonct["MA"].set_top(3)
    format_fonct["MA"].set_bottom(3)
    format_fonct["MA"].set_left(4)
    format_fonct["MA"].set_right(4)
    format_fonct["MA"].set_align("center")

    # Format séparateur d'itération
    format_separator = wb.add_format()
    format_separator.set_top(3)
    format_separator.set_bottom(3)
    format_separator.set_left(2)
    format_separator.set_right(4)
    format_separator.set_align("center")

    # Format défaut
    format_default = wb.add_format()
    format_default.set_top(3)
    format_default.set_bottom(3)
    format_default.set_left(4)
    format_default.set_right(4)
    format_default.set_align("center")

    # Fin définition formats

    # Ecriture du header
    sheet.write_row(0, 0, header, format_header)
    #    log(header)
    # écriture des valeur avec un système de modulo pour gérer les styles
    for rownum, row in enumerate(data, 1):
        for colnum, value in enumerate(row):
            try:
                # on calcul le numéro de colonne dans l'itération (on enlève l'offset et modulo le nombre de colonne par itération)
                colnum_modulo = (colnum - offset) % nb_col

                # Si colonne séparateur
                if (colnum + 1 > offset) and (colnum_modulo == 0):
                    sheet.write(rownum, colnum, value, format_separator)

                elif value:
                    # Si colonne numéro de tube
                    if (colnum + 1 > offset) and (colnum_modulo == col_numtube):
                        # on retrouve le format correspondant à la couleur grace à la valeur de la cellule
                        sheet.write(
                            rownum,
                            colnum,
                            value,
                            format_fo_color[(int(value) - 1) % 12],
                        )
                    # Si colonne numéro de fibre
                    elif (colnum + 1 > offset) and (colnum_modulo == col_numfo):
                        # on retrouve le format correspondant à la couleur grace à la valeur de la cellule
                        sheet.write(
                            rownum,
                            colnum,
                            value,
                            format_fo_color[(int(value) - 1) % 12],
                        )

                    # Si colonne fonct
                    elif (colnum + 1 > offset) and (colnum_modulo == col_fonct):
                        sheet.write(rownum, colnum, value, format_fonct[value])

                    # Si colonne longueur
                    elif (colnum + 1 > offset) and (colnum_modulo == col_long):
                        sheet.write(rownum, colnum, value, format_long)

                    # autres valeurs
                    else:
                        sheet.write(rownum, colnum, value, format_default)
                # Si pas de valeurs
                else:
                    sheet.write(rownum, colnum, value, format_default)
            except:
                sheet.write(rownum, colnum, "ERROR", format_default)
    wb.close()


def generate_ropt_full(base, n_iteration=15, prefix_sql_view="v_ropt_full_di_"):
    log("Génération de la route optique complète")
    log("Base cible : %s" % (base))
    # Creation des tables ropt complètes
    if grace_version == 2:
        create_tables_ropt(base, n_iteration, prefix_sql_view)
        sro_nro_table = "t_sitetech"
        sro_nro_typelog = "st_typelog"
        # TODO : st_code + param module
    elif grace_version == 3:
        create_tables_ropt(base, n_iteration, prefix_sql_view)
        sro_nro_table = "t_local"
        sro_nro_typelog = "lc_typelog"
    else:
        raise ValueError("La version de GRACE doit être 2 ou 3")

    # On récupère la liste des SRO
    con = sqlite3.connect(base)
    con.row_factory = (
        sqlite3.Row
    )  # permet d'exploiter plus facilement les Row en sortie des requêtes
    cur = con.cursor()
    log("extraction de la liste des SRO et NRO")
    req = "SELECT * FROM %s WHERE %s IN ('SRO', 'SROL', 'NRO');" % (
        sro_nro_table,
        sro_nro_typelog,
    )
    cur.execute(req)
    list_st = cur.fetchall()
    cur.close()
    con.close()
    log("%s SRO et NRO présent dans la base" % (str(len(list_st))))

    # On calcule le nom de la table ROPT complète
    ropt_full_name = prefix_sql_view + "it" + str(nombre_iteration)
    # Pour chaque SRO on crée la vue ropt light et on l'extrait dans un fichier
    for st in list_st:
        st_value = st[param_st_id]
        log("Génération de la vue ropt light pour le Site technique %s" % (st_value))
        if st[sro_nro_typelog] == "SRO" or st[sro_nro_typelog] == "SROL":
            view_ropt_sro = create_view_ropt_light_sro(
                base,
                st_value,
                n_iteration,
                ropt_full_name,
                segment="DI",
                cb_id=param_cb_id,
                bp_id=param_bp_id,
                lg_cable=param_lg_cable,
                ti_id=param_ti_id,
                st_id=param_st_id,
            )
        elif st[sro_nro_typelog] == "NRO":
            view_ropt_sro = create_view_ropt_light_sro(
                base,
                st_value,
                n_iteration,
                ropt_full_name,
                segment="TR",
                cb_id=param_cb_id,
                bp_id=param_bp_id,
                lg_cable=param_lg_cable,
                ti_id=param_ti_id,
                st_id=param_st_id,
            )
        # On crée un dossier pour accueil les fichiers route optique
        csv_ropt_dir = Path(base).parent / "ropt"
        csv_ropt_dir.mkdir(parents=True, exist_ok=True)

        extract_table_to_file(
            base,
            view_ropt_sro,
            dir_name=csv_ropt_dir,
            file_name=view_ropt_sro,
            file_type="xlsx",
        )

        # Mise en forme de la ropt
        format_ropt(Path(csv_ropt_dir) / (view_ropt_sro + ".xlsx"))
