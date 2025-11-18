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


import argparse
import logging
from pathlib import Path

from . import cfg_reader, processing_logging, rop_grace, spatialiteio


def quickinteg_create():
    """Permet de créer un alias CLI pour appeler cfg_reader.create_template_from_cfg.
    Alias : qi-create
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="Chemin vers le fichier de configuration de template")
    args = parser.parse_args()
    processing_logging.add_console_handler(logging.getLogger(""))
    cfg_reader.create_template_from_cfg(args.config_file)


def quickinteg_delete():
    """Alias CLI pour faire un delete à partir du import_prefix"""
    parser = argparse.ArgumentParser()
    parser.add_argument("db", help="Base spatialite dans laquelle supprimer les lignes")
    parser.add_argument("import_prefix", help="Valeur de l'import prefix")
    args = parser.parse_args()
    processing_logging.add_console_handler(logging.getLogger(""))
    spatialiteio.delete_rows(args.db, args.import_prefix)


# TODO : add log to text
def quickinteg_import():
    """Permet de créer un alias CLI pour appeler spatialiteio.import_folder_to_spl et
    spatialiteio.export_preset_tables.
    Alias : qi-import
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Chemin vers le repertoir à intégrer")
    parser.add_argument("-c", "--no-csv", help="Exclure les fichiers CSV", action="store_true")
    parser.add_argument(
        "-d",
        "--destination",
        help="Chemin vers une base de donnée existante (mode APPEND).",
        default=None,
    )
    parser.add_argument(
        "-p",
        "--prefix",
        help="Préfixe d'importation ajouté sur chaque table.",
        default="",
    )
    parser.add_argument("-e", "--export", help="Exporter les vues de contrôle", action="store_true")
    parser.add_argument(
        "-r",
        "--recursive",
        help="Mode récursif (parcours les sous-dossiers).",
        action="store_true",
    )
    args = parser.parse_args()
    processing_logging.add_console_handler(logging.getLogger(""))

    if args.destination:
        log_file = Path(args.destination).parent / "log_integ.txt"
    else:
        log_file = Path(args.source) / "log_integ.txt"
    processing_logging.add_file_handler(logging.getLogger(""), log_file, logging.DEBUG)

    spatialiteio.import_folder_to_spl(
        args.source,
        ogr_target=args.destination,
        prefix=args.prefix,
        include_csv=(not args.no_csv),
        ignore_grace_list=True,
        recursive=args.recursive,
    )
    if args.export:
        spatialiteio.export_preset_tables(args.destination)


def quickinteg_rop():
    """Permet de créer un alias CLI générer les routes optiques.
    Alias : qi-rop
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("db_file", help="Base de donnée Quickinteg")
    parser.add_argument(
        "-v", "--version", help="Version GRACE THD (2 ou 3, 3 par défaut)", default=3
    )
    parser.add_argument(
        "-m",
        "--mode",
        help="Mode to use (table or view, table by default)",
        default="table",
    )
    args = parser.parse_args()
    processing_logging.add_console_handler(logging.getLogger(""))
    if int(args.version) == 3:
        rop_grace.param_st_id = "lc_codeext"
        rop_grace.param_cb_id = "cb_codeext"
        rop_grace.param_bp_id = "bp_codeext"
        rop_grace.param_ti_id = "ti_codeext"
        rop_grace.param_lg_cable = "cb_lgreel"
        rop_grace.grace_version = 3
        rop_grace.mode = args.mode
        rop_grace.generate_ropt_full(args.db_file, n_iteration=15)
    elif int(args.version) == 2:
        rop_grace.param_st_id = "st_codeext"
        rop_grace.param_cb_id = "cb_codeext"
        rop_grace.param_bp_id = "bp_codeext"
        rop_grace.param_ti_id = "ti_codeext"
        rop_grace.param_lg_cable = "cb_lgreel"
        rop_grace.grace_version = 2
        rop_grace.mode = args.mode
        rop_grace.generate_ropt_full(args.db_file, n_iteration=15)
    else:
        raise ValueError("Valeur incorrecte pour -v / --version")


def quickinteg_formatrop():
    """Permet de créer un alias CLI formater les routes optique au format excel.
    Alias : qi-formatrop
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("rop_file", help="Fichier de ROP")
    args = parser.parse_args()
    rop_grace.format_ropt(args.rop_file)
