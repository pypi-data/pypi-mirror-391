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
# ########## Imports ###############
# ##################################
# standard library
import ast
import configparser
import logging
import os
from pathlib import Path

# package
from . import mcd_check, processing_logging, spatialiteio

# ############################################################################
# ########## Globals ###############
# ##################################

module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)


# ############################################################################
# ########## Functions #############
# ##################################


def log(message: str, logLevel="info"):
    processing_logging.log(str(message), module_logger, logLevel)


def parse_config_file(config_file_path: str) -> dict:
    raw_config = configparser.ConfigParser()
    raw_config.read(config_file_path)

    config = dict()
    l_params = ["table_def", "mcd_check", "sql", "export_table"]
    log("Lecture du fichier de configuration %s" % (config_file_path))
    for param in l_params:
        try:
            config[param] = ast.literal_eval(raw_config["template"][param])
            log("%s: %s" % (param, config[param]))
        except KeyError:
            log("Pas de valeur %s dans la config" % (param))
        except ValueError:  # si pas de syntaxe python (ex, guillements pour string)
            config[param] = raw_config["template"][param]
        except SyntaxError:  # si pas de syntaxe python (ex, guillements pour string)
            config[param] = raw_config["template"][param]

    log("Configuration : \n%s" % (config))
    return config


def create_template_from_cfg(config_file_path):
    config = parse_config_file(config_file_path)
    os.chdir(Path(config_file_path).parent)

    sql_tables_def_folder = config["table_def"]

    base_spl_filename = Path(sql_tables_def_folder).name
    base_spl_path = Path(base_spl_filename + ".sqlite")
    # On crée une base sqlite3 avec extension spatialite
    if base_spl_path.exists():
        raise ValueError("Le fichier %s existe déjà" % (base_spl_path))
    else:
        spatialiteio.create_spatialite_db(base_spl_path)

    # On exécute les différents scripts SQL sur la base spatialite

    # MCD CHECK
    spatialiteio.execute_file_to_spl(sql_tables_def_folder, base_spl_path)

    # Configuration de contrôle
    if "mcd_check" in set(config.keys()):
        catalog_file = str(Path(config["mcd_check"]["catalogue"]))
        config_file = str(Path(config["mcd_check"]["config"]))
        sql_code = mcd_check.translate_config_to_sql(catalog_file, config_file)
        spatialiteio.execute_query_to_spl(sql_code, base_spl_path)

    # SQL
    if "sql" in set(config.keys()):
        for sql in config["sql"]:
            spatialiteio.execute_file_to_spl(str(Path(sql)), base_spl_path)

    if "export_table" in set(config.keys()):
        spatialiteio.check_preset_tables(base_spl_path, config["export_table"])
