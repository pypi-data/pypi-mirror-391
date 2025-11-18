#! python3  # noqa: E265

################################################################################
# This file is part of quickinteg.

# quickinteg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# quickinteg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with quickinteg.  If not, see <https://www.gnu.org/licenses/>.
################################################################################

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
import os
import sqlite3
import string
import subprocess
import time
import unicodedata
from pathlib import Path

from . import processing_logging

# 3rd party - try embedded first (for QGIS), fallback to normal import (for CLI)
try:
    from .external import xlsxwriter
except ImportError:
    pass

# ############################################################################
# ########## Globals ###############
# ##################################

module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)


# ############################################################################
# ########## Functions #############
# ##################################


def log(message, logLevel="info"):
    processing_logging.log(str(message), module_logger, logLevel)


def spatialite_connect(*args, **kwargs):
    """returns a dbapi2.Connection to a SpatiaLite db
    using the "mod_spatialite" extension (python3)

    WARNING !! it messes up subprocesses on MacOS. Use sqlite3.connect when possible"""
    import sqlite3

    con = sqlite3.connect(*args, **kwargs)
    con.enable_load_extension(True)
    cur = con.cursor()
    libs = [
        # SpatiaLite >= 4.2 and Sqlite >= 3.7.17, should work on all platforms
        ("mod_spatialite", "sqlite3_modspatialite_init"),
        # SpatiaLite >= 4.2 and Sqlite < 3.7.17 (Travis)
        ("mod_spatialite.so", "sqlite3_modspatialite_init"),
        # SpatiaLite < 4.2 (linux)
        ("libspatialite.so", "sqlite3_extension_init"),
    ]
    found = False
    for lib, entry_point in libs:
        try:
            cur.execute(f"select load_extension('{lib}', '{entry_point}')")
        except sqlite3.OperationalError as err:
            if __debug__:
                log(err, "debug")
            continue
        else:
            found = True
            break
    if not found:
        raise RuntimeError("Cannot find any suitable spatialite module")
    cur.close()
    con.enable_load_extension(False)
    return con


def create_spatialite_db(file_name):
    if Path(file_name).exists():
        raise ValueError(f"La base de donnée {file_name} existe déjà")
    else:
        # Trick to create an empty spatialite db with ogr2ogr
        cmd = f'echo \'{{"type": "FeatureCollection","features": []}}\' | ogr2ogr -f SQLite -dsco SPATIALITE=YES "{file_name}" /vsistdin/ -nln _qi_dummy'

        # Run the process and wait for it to complete
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            shell=True,
        )


def table_exists(db_file, tbl_name):
    """
    Return true if table "tbl_name" exists in base "db_file"
    """
    with sqlite3.connect(db_file) as con:
        # Use a normal try/finally block to ensure the cursor is closed.
        try:
            cur = con.cursor()
            # Use parameterized query to prevent SQL injection
            req = "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;"
            cur.execute(req, (tbl_name,))
            res = cur.fetchone()[0]
        finally:
            # Ensure the cursor is closed after use
            cur.close()

    # The connection will be closed automatically due to the 'with' statement.
    return res != 0


def column_exists(db_file, tbl_name, column_name):
    """
    Return true if column "column_name" exists in table "tbl_name"
    """
    if table_exists(db_file, tbl_name):
        with sqlite3.connect(db_file) as con:
            cur = con.cursor()
            req_search_for_column = (
                f"PRAGMA table_info('{tbl_name}');"  # Use parameter substitution for safety
            )
            cur.execute(req_search_for_column)
            results = cur.fetchall()
            columns = [row[1] for row in results]  # second column of PRAGMA INFO is column name
            return column_name in columns

    return False  # If the table does not exist, return False


def add_column(db_file, tbl_name, column_name):
    if table_exists(db_file, tbl_name) and not column_exists(db_file, tbl_name, column_name):
        log(f"Ajout de la colonne {column_name} à la table {tbl_name}", "debug")

        with sqlite3.connect(db_file) as con:
            cur = con.cursor()

            # Execute the ALTER TABLE statement to add the column
            req = f"ALTER TABLE {tbl_name} ADD COLUMN {column_name}"
            cur.execute(req)


def get_srs(db_file, tbl_name):
    """
    Return CRS of the table
    """
    with sqlite3.connect(db_file) as con:
        cur = con.cursor()
        log(f"Vérification du SRS de la table {tbl_name} dans la base", "debug")
        req = f"SELECT srid FROM geometry_columns WHERE f_table_name = '{tbl_name}';"
        cur.execute(req)
        out_sql = cur.fetchone()

    if out_sql is None:
        log("La table n'a pas de géometrie dans spatialite.", "debug")
        return None
    else:
        srid = out_sql[0]
        return f"EPSG:{srid}"


def geom_type(db_file, tbl_name):
    """
    Return geom type in text. Returns None in no geometry
    Spatialites geoms :
    1 = POINT
    2 = LINESTRING
    3 = POLYGON
    4 = MULTIPOINT
    5 = MULTILINESTRING
    6 = MULTIPOLYGON
    7 = GEOMETRYCOLLECTION
    """
    with sqlite3.connect(db_file) as con:  # Use context manager for the connection
        cur = con.cursor()  # Cursor managed by connection's context manager
        log(f"Vérification de la géometrie de la table {tbl_name} dans la base", "debug")

        # Using string formatting here because SQLite does not support parameter
        # substitution for table names. Ensure that 'tbl_name' is safe to include.
        req = f"SELECT geometry_type FROM geometry_columns WHERE f_table_name = '{tbl_name}';"
        cur.execute(req)
        out_sql = cur.fetchone()

    if out_sql is None:
        log("La table n'a pas de géometrie dans spatialite.", "debug")
        return None
    else:
        dict_geoms = {
            1: "POINT",
            2: "LINESTRING",
            3: "POLYGON",
            4: "MULTIPOINT",
            5: "MULTILINESTRING",
            6: "MULTIPOLYGON",
            7: "GEOMETRYCOLLECTION",
        }
        geom_num = out_sql[0]
        try:
            return dict_geoms[geom_num]
        except IndexError:
            raise ValueError("Undefined geometry (%s)" % (geom_num))


def import_file_to_spl(ogr_target, shp_csv_file, tbl_name, options="", prefix=None):
    """
    Import un fichier shp ou csv vers une base spatialite avec ogr2ogr.
    Le nom de la table sera le nom du fichier en minuscule sans l'extension

        option : ajouter des options à la commande ogr2ogr
            (par exemple -skipfailures)
        prefix : si différent de '', ajoutera une colonne "import_prefix" à la
            table. Chaque enregistrement prendra la valeur donnée en paramètre.
    """
    log(
        "# Import du fichier %s dans la table %s de la bdd %s"
        % (shp_csv_file, tbl_name, ogr_target)
    )

    file_type = os.path.splitext(os.path.basename(shp_csv_file))[1]
    if file_type not in (".csv", ".shp"):
        raise ValueError("Le type de fichier %s n'est pas supporté" % (file_type))

    # Construction de la commande ogr2ogr
    # On commence par les options passées en paramètre
    ogr_options = options

    if file_type == ".shp":
        # ajout d'une option OGR
        ogr_options += " -dim XY"
        if not table_exists(ogr_target, tbl_name):
            log(
                "La table " + tbl_name + " n'existe pas. Elle sera créée par org2ogr",
                logLevel="debug",
            )
            # On ajoute l'option pour une geometrie multi et on donne le nom "geom" pour la
            # colonne de géometrie (sinon nom arbitraire OGR moche)
            # ajout d'une option OGR
            ogr_options += " -nlt PROMOTE_TO_MULTI  -lco GEOMETRY_NAME=geom"
        # Sinon la table existe, on vérifie sa geometry pour les parametrès d'import OGR
        else:
            log(
                "La table %s existe déjà. Les données seront ajoutées" % (tbl_name),
                logLevel="debug",
            )
            geom_type_ = geom_type(ogr_target, tbl_name)
            if geom_type_ in ("POINT", "LINESTRING", "POLYGON"):
                pass
            elif geom_type_ in ("MULTIPOINT", "MULTILINESTRING", "MULTIPOLYGON"):
                # ajout d'une option OGR
                log(
                    "La table de destination à une géometrie multi. "
                    "Ajout du paramètre PROMOTE_TO_MULTI",
                    logLevel="debug",
                )
                ogr_options += " -nlt PROMOTE_TO_MULTI"
            ogr_options += ' -t_srs "%s"' % (get_srs(ogr_target, tbl_name))
            # Other option is :
            # ogr_options += ' -nlt %s' %(geom_type_)
            # but this option will create invalid geoms without warning
    elif file_type == ".csv":
        # ajout d'une option OGR
        ogr_options += " -oo EMPTY_STRING_AS_NULL=YES"

    if prefix is not None and prefix != "":
        if table_exists(ogr_target, tbl_name) and not column_exists(
            ogr_target, tbl_name, "import_prefix"
        ):
            add_column(ogr_target, tbl_name, "import_prefix")

        # S'il y a un préfixe on ajoute une option -sql pour ajouter une colonne
        shp_name_without_extension = os.path.splitext(os.path.basename(shp_csv_file))[0]
        # ajout d'une option OGR
        ogr_options += " -sql  \"SELECT *, '%s' AS import_prefix FROM %s\"" % (
            prefix,
            shp_name_without_extension,
        )
        # Avec l'ajout de cette option, la requête plante si le nom du shp contient des charactères spéciaux
        # On gère alors le cas proprement avec une exception
        # Liste des charactères interdits (underscore _ autorisé)
        invalidChars = set(string.punctuation.replace("_", ""))
        if any(char in invalidChars for char in shp_name_without_extension):
            raise ValueError(
                "Impossible d'ajouter un préfixe d'import si les "
                "noms de shp contiennent des caractères spéciaux. "
                "Essayer en renommant les shapes à importer."
            )
    # On assemble la commande d'appel à OGR2OGR
    cmd = f'ogr2ogr -f sqlite "{ogr_target}" "{shp_csv_file}" -nln {tbl_name} -append {ogr_options}'
    cmd_skipfailures = f'ogr2ogr -f sqlite "{ogr_target}" "{shp_csv_file}" -nln {tbl_name} -append {ogr_options} -skipfailures'
    log("OGR2OGR : %s" % (cmd), logLevel="debug")
    # Si Erreur ogr, on ressaie avec skipfailures
    # os.system(f'{cmd} || {{ echo "toto"; {cmd_skipfailures}; }}')

    # Run the process and wait for it to complete
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        shell=True,
    )
    # Access the stdout and stderr
    stdout_output = result.stdout
    stderr_output = result.stderr

    # Get the exit status
    exit_status = result.returncode
    if stderr_output:
        log(stderr_output, logLevel="warning")
    if exit_status != 0:
        log(
            "L'import ogr2ogr a échoué. Nouvelle tentative avec -skipfailures. Une partie des donnée sera ignorée.",
            logLevel="warning",
        )
        result = subprocess.run(
            cmd_skipfailures,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            shell=True,
        )


def import_folder_to_spl(
    folder,
    ogr_target=None,
    prefix=None,
    include_csv=False,
    ignore_grace_list=True,
    recursive=False,
):
    if recursive:
        shp_glob_pattern = "**/*.shp"
        csv_glob_pattern = "**/*.csv"
    else:
        shp_glob_pattern = "*.shp"
        csv_glob_pattern = "*.csv"

    if ogr_target is None:
        log("Aucune base de donnée renseignée. Création d'une nouvelle BDD")
        ogr_target_ = str(Path(folder) / "base.sqlite")
        create_spatialite_db(ogr_target_)
    elif Path(ogr_target).exists():
        # log("Création d'une sauvegarde de la BDD")
        # copyfile(ogr_target, ogr_target + "_backup")
        ogr_target_ = ogr_target
    else:
        raise ValueError("La base de donnée %s n'existe pas" % (ogr_target))

    if include_csv:
        list_files = list(Path(folder).glob(shp_glob_pattern)) + list(
            Path(folder).glob(csv_glob_pattern)
        )
        log("Option CSV activée. Liste des fichier à importer :")
        for i in list_files:
            log(str(i))
    else:
        list_files = list(Path(folder).glob(shp_glob_pattern))
        log("Liste des fichier à importer :")
        for i in list_files:
            log(str(i))

    for file in list_files:
        if ignore_grace_list and file.name.startswith("l_"):
            log(
                f"le fichier {os.path.basename(file)} sera ignoré car il correspond une liste de valeur GRACE THD",
                logLevel="debug",
            )
        else:
            # On prend le nom de fichier, sans l'extension et en minuscule, normalisé
            # sera le nom de la table sqlite
            tbl_name = file.stem.lower()
            tbl_name = (
                unicodedata.normalize("NFD", tbl_name).encode("ascii", "ignore").decode("utf-8")
            )
            # On remplace les espaces par _ dans le nom
            tbl_name = tbl_name.replace(" ", "_")
            if (not prefix) and recursive:
                prefix_ = Path(file).parent.stem
            else:
                prefix_ = prefix
            import_file_to_spl(ogr_target_, file, tbl_name, prefix=prefix_)


def extract_table_to_file(
    spl_db, view_name, dir_name=None, file_name=None, sheet_name=None, file_type="csv"
):
    log(
        f"Extraction de la vue {view_name} au format {file_type} vers {dir_name}/{file_name}.{file_type}"
    )
    start_time = time.time()
    ogr_mapping = {
        "csv": "-f CSV",
        "xlsx": "-f XLSX",
        "shp": "-f 'ESRI Shapefile'",
        "sqlite": "-f sqlite -dsco SPATIALITE=YES",
    }
    if not dir_name:
        dir_name = Path(spl_db).parent
    if not file_name:
        file_name = view_name
    if not sheet_name:
        sheet_name = view_name

    targetfilepath = str(Path(dir_name) / (file_name + "." + file_type))
    # if target file is the source DB, we do not overwrite to preserve database structure
    # this allow some template tricks
    if (
        Path(spl_db).resolve()  # source db
        == (Path(dir_name) / (file_name + "." + file_type)).resolve()  # target file
    ):
        overwrite_ = "-append"
    else:
        overwrite_ = "-overwrite"

    ogr_command = f'ogr2ogr {ogr_mapping[file_type]} "{targetfilepath}" "{spl_db}" -sql "SELECT * FROM {view_name}" -nln {sheet_name} {overwrite_}'
    log(ogr_command, logLevel="debug")

    # Run the process and wait for it to complete
    result = subprocess.run(
        ogr_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        shell=True,
    )
    # Access the stdout and stderr
    stdout_output = result.stdout
    stderr_output = result.stderr

    # Get the exit status
    if stderr_output:
        log(stderr_output, logLevel="warning")

    end_time = time.time()
    duration = end_time - start_time
    log(f"Elapsed time: {duration:.2f} seconds")


def execute_query_to_spl(sql_query, spl_db):
    con = spatialite_connect(spl_db)
    # on execute le fichier sql en tant que script
    log("Exécution du script sur la base de donnée")
    with con:
        cur = con.cursor()
        cur.executescript(sql_query)
    con.close()


def execute_file_to_spl(filename, spl_db):
    """Exécute le script .sql cible dans la base de donnée spl_db.
    si le fichier est un dossier, execute chaque fichier .sql dans l'ordre alphabétique
    """
    # si le fichier est un fichier .sql
    if Path(filename).suffix == ".sql":
        # on lit le fichier sql
        log("Lecture du fichier %s" % (filename))
        with open(filename) as f:
            sql_script = f.read()
        log("Connexion à la base de donnée %s" % (spl_db))
        con = spatialite_connect(spl_db)
        # on execute le fichier sql en tant que script
        log("Exécution du script sur la base de donnée")
        with con:
            cur = con.cursor()
            cur.executescript(sql_script)
        con.close()
    # si le fichier est un dossier, on liste les fichier *.sql et on execute la fonction
    elif Path(filename).is_dir():
        list_file_sql = [file for file in Path(filename).glob("*.sql")]
        # tri par ordre alphabétique
        list_file_sql.sort()
        log("Le fichier cible est un dossier. Liste des fichiers *.sql trouvés dans ce dossier : ")
        for f in list_file_sql:
            log(f)
        for f in list_file_sql:
            execute_file_to_spl(f, spl_db)
    # sinon on renvoit une erreur
    else:
        raise ValueError("Le fichier cible n'est ni un fichier *.sql ni un dossier")


def export_preset_tables(spatialite_db, config_table_name=None):
    """
    On récupère le contenu de la table config_table_name
    Cette table doit avoir le format suivant :
       view_name VARCHAR(254),    --> nom de la table ou vue à exporter
       dest_file VARCHAR(254),    --> nom du fichier de destination sans extention
       dest_sheet VARCHAR(254),   --> nom de l'onglet du fichier (si plusieurs fois le même fichier en xlsx)
       dest_folder VARCHAR(254),  --> chemin du sous-dossier d'export (chemin relatif). Doit commencer par "/"
       file_type VARCHAR(254)     --> type (csv, xlsx, shp)
    """

    log("Export des vues calculées")

    # Default table of views to export changed name
    if not config_table_name:
        if table_exists(spatialite_db, "tactis_list_views_to_export"):
            config_table_name = "tactis_list_views_to_export"
        elif table_exists(spatialite_db, "_qi_exports"):
            config_table_name = "_qi_exports"

    with sqlite3.connect(spatialite_db) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        req = "SELECT * FROM %s;" % (config_table_name)
        cur.execute(req)
        rows = cur.fetchall()

    for row in rows:
        # On traite ligne par ligne.
        # Récupération des paramètres
        file_name = row["dest_file"]
        view_name = row["view_name"]
        sheet_name = row["dest_sheet"]
        file_type = row["file_type"]
        # On construit le chemin absolu dans dest_folder
        dest_folder = str(
            Path(spatialite_db).parents[0].joinpath(row["dest_folder"].strip("/").strip("\\"))
        )
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        extract_table_to_file(
            spatialite_db,
            view_name,
            dir_name=dest_folder,
            file_name=file_name,
            sheet_name=sheet_name,
            file_type=file_type,
        )


def check_preset_tables(spatialite_db, config_table_name):
    """
    Appelle les tables/vues définies dans la table "config_table_name" et
    vérifie que leur appel de génère pas une erreur SQL. Fonction à effectuer
    sur un template vide, sinon il y aura un temps de calcul des vues selon
    la quantité de données.

    Rappel structure table "config_table_name"
           view_name VARCHAR(254),    --> nom de la table ou vue à exporter
           dest_file VARCHAR(254),    --> nom du fichier de destination sans extention
           dest_sheet VARCHAR(254),   --> nom de l'onglet du fichier (si plusieurs fois le même fichier en xlsx)
           dest_folder VARCHAR(254),  --> chemin du sous-dossier d'export (chemin relatif). Doit commencer par "/"
           file_type VARCHAR(254)     --> type (csv, xlsx, shp)
    """
    log("Vérification de la validité des tables/vues listées dans la table%s" % (config_table_name))
    con = spatialite_connect(spatialite_db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    req = "SELECT * FROM %s;" % (config_table_name)
    cur.execute(req)
    rows = cur.fetchall()
    # Fermeture de la connexion sql
    cur.close()
    con.close()
    for row in rows:
        view_name = row["view_name"]
        try:
            con = spatialite_connect(spatialite_db)
            cur = con.cursor()
            req = "SELECT * FROM '%s'" % (view_name)
            cur.execute(req)
            cur.close()
            con.close()
            log("%s : OK" % (view_name))
        except Exception as e:
            log("%s : NOK" % (view_name), "warning")
            log(e, "warning")


def delete_rows(db_file, value, table=None, column="import_prefix", condition="CONTIENT"):
    con = spatialite_connect(db_file)
    cur = con.cursor()
    req = " PRAGMA foreign_keys = off; "
    cur.executescript(req)

    if table is None:
        tables = list_tables(db_file, column_name=column)
    else:
        tables = [table]

    log("Suppression des lignes répondant à la condition %s %s %s" % (column, condition, value))
    log("Dans les tables suivantes : %s" % (tables))
    for table_ in tables:
        if condition == "EGAL":
            req_del = " DELETE FROM '%s' WHERE %s = '%s' " % (table_, column, value)
            req_count = " SELECT COUNT(*) FROM '%s' WHERE %s = '%s';" % (
                table_,
                column,
                value,
            )
        elif condition == "CONTIENT":
            req_del = " DELETE FROM '%s' WHERE %s LIKE '%%%s%%' " % (
                table_,
                column,
                value,
            )
            req_count = " SELECT COUNT(*) FROM '%s' WHERE %s LIKE '%%%s%%';" % (
                table_,
                column,
                value,
            )

        cur.execute(req_count)
        n_lines_to_delete = cur.fetchone()[0]
        log("Table %s : %s lignes à supprimer" % (table_, n_lines_to_delete))
        cur.executescript(req_del)

    cur.close()
    con.close()


def list_tables(db_file, column_name=None):
    with sqlite3.connect(db_file) as con:
        cur = con.cursor()
        # 'SpatialIndex', 'ElementaryGeometries', 'KNN' are not queriable without spatialite extension
        req = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('SpatialIndex', 'ElementaryGeometries', 'KNN', 'KNN2');"
        cur.execute(req)
        rows = cur.fetchall()

    if column_name is None:
        tables = [row[0] for row in rows]
    else:
        tables = [row[0] for row in rows if column_exists(db_file, row[0], column_name)]

    return tables
