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
import math

# package
from . import processing_logging
from .excel_shortcut import read_all_sheet_to_dict

# ############################################################################
# ########## Globals ###############
# ##################################
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)


catalogue_config = {
    "id_test_col": "id_test",
    "description_col": "description",
    "classe_col": "classe",
    "attribut_col": "attribut",
    "xx_code_col": "xx_code",
    "param1_col": "param1",
    "param2_col": "param2",
    "param3_col": "param3",
    "requ_princ_col": "requ_princ",
    "condition_col": "condition",
    "detail_erreur_col": "detail_erreur",
}
config_controle_config = {
    "id_test_col": "id_test",
    "config_col": "config",
    "param1_col": "param1",
    "param2_col": "param2",
    "param3_col": "param3",
}


# ############################################################################
# ########## Functions #############
# ##################################
def log(message, logLevel="info"):
    processing_logging.log(message, module_logger, logLevel)


# Création de l'objet controle, et de toutes ses fonctions associées
class Controle:
    """Un point de contrôle est défini par :
    * Un identifiant
    * Une description
    * Une requête SQL principale
    * Une condition d'erreur dans cette requête
    * La classe (table) sur laquelle porte l'erreur
    * L'attribut sur lequel porte l'erreur (dans la table / classe)
    * 0 à 3 paramètres
    * L'expression (SQL) du détail de l'erreur.
    """

    # ########################################################################
    # ### Methods ###############
    # ###########################

    def make_view_ctrl(list_controles_sql, view_name="v_ctrl_all_source"):
        """L'attribut  "list_controles_sql" est une liste de codes sql de points
        de controle (sortie de Controle.get_sql()).
        La fonction ajoute en en-têtes :
        DROP VIEW IF EXISTS {view_name};
        CREATE VIEW {view_name} AS
        et termine par un ;"""
        # Il y a une limite intrasèque à SQLITE sur le nombre d'UNION max dans une requête (500 max).
        # On tronçonne donc la vue 'v_ctrl_all_source' en plusieurs vues intermédiaires et on refait un UNION ensuite
        nb_controles = len(list_controles_sql)
        view_name_from_param = view_name
        if nb_controles <= 400:
            sql_code = '\nDROP VIEW IF EXISTS "%s";\n' % (view_name)
            sql_code += 'CREATE VIEW "%s" AS' % (view_name)
            for i, controle_sql in enumerate(list_controles_sql):
                if i == 0:
                    sql_code += "\n\t%s" % (controle_sql)
                else:
                    sql_code += " UNION \n\t%s" % (controle_sql)
            sql_code += ";"
            return sql_code
        else:
            # sql_code comprend le code complet de la requête (liste des vues intermédiares + UNION final des vues intermédiaires)
            sql_code = ""
            # last_union comprend le UNION final des vues intermédiaires. On l'initialise ici et on le complète à chaque itération
            # de la boucle for.
            last_union = '\n\nDROP VIEW IF EXISTS "%s";\n' % (view_name)
            last_union += 'CREATE VIEW "%s" AS' % (view_name)
            # On crée une vue intermédiaire pour chaque tronçons de 400 requêtes
            # math.ceil --> arrondi entier supérieur
            # par ex : si 800 requêtes on aura range(2). Pour 801 requêtes on aura range(3)
            for i in range(math.ceil(nb_controles / 400)):
                # On appelle Controle.make_view_ctrl sur une sous partie de la liste des requetes
                extract_list_controles = list_controles_sql[
                    i * 400 : min(len(list_controles_sql), ((i + 1) * 400))
                ]
                intermediate_view_name = view_name_from_param + str(i)
                sql_code += Controle.make_view_ctrl(
                    extract_list_controles, view_name=intermediate_view_name
                )
                # On alimente last_union
                if i == 0:
                    last_union += "\n\tSELECT * FROM %s" % (intermediate_view_name)
                else:
                    last_union += " UNION \n\tSELECT * FROM %s" % (intermediate_view_name)
            last_union += ";"
            sql_code += last_union
            return sql_code

    # ########################################################################
    # #### Constructor  ####
    # ######################

    def __init__(
        self,
        ctrl_id,
        ctrl_description,
        ctrl_classe,
        ctrl_attr,
        ctrl_xxcode,
        ctrl_desc_param1,
        ctrl_desc_param2,
        ctrl_desc_param3,
        ctrl_reqprinc,
        ctrl_condition,
        ctrl_detail_erreur,
        ctrl_nbparam,
    ):
        # Déclaration des variables
        self.id = ctrl_id
        self.description = ctrl_description
        self.classe = ctrl_classe
        self.attr = ctrl_attr
        self.xxcode = ctrl_xxcode
        self.description_param1 = ctrl_desc_param1
        self.description_param2 = ctrl_desc_param2
        self.description_param3 = ctrl_desc_param3
        self.reqprinc = ctrl_reqprinc
        self.condition = ctrl_condition
        self.nbparam = ctrl_nbparam  # Pour controle de cohérence
        self.detail_erreur = ctrl_detail_erreur

    # #############################
    # ##  Methodes d'instance  ####
    # #############################

    # Extraction des différentes variables de la classe Contrôle
    def get_id(self):
        return self.id

    def get_description(self):
        return self.description

    def get_classe(self):
        return self.classe

    def get_attr(self):
        return self.attr

    def get_xxcode(self):
        return self.xxcode

    def get_description_param1(self):
        return self.description_param1

    def get_description_param2(self):
        return self.description_param2

    def get_description_param3(self):
        return self.description_param3

    def get_reqprinc(self):
        return self.reqprinc

    def get_condition(self):
        return self.condition

    def get_nbparam(self):
        return self.nbparam

    def get_detail_erreur(self):
        return self.detail_erreur

    def check_param_compatibility(self, param1, param2, param3):
        """Fonction de contrôle des paramètres"""
        nb_erreur = 0
        if (self.description_param1) is not None and (param1 is None):
            nb_erreur = nb_erreur + 1
        if (self.description_param2) is not None and (param2 is None):
            nb_erreur = nb_erreur + 1
        if (self.description_param3) is not None and (param3 is None):
            nb_erreur = nb_erreur + 1
        return nb_erreur

    def insert_param_in_sql(self, requete_sql, param1, param2, param3):
        """
        Les paramètres sont renseignées de la sorte dans le point de contrôle:
        ex : self.description_param1 = 'param1:default=8' (issus de la lecture du
        catalogue de contrôle xlsx)
        La fonction insert_param_in_sql remplace ces chaines de caractère par les
        valeurs réelles des paramètres param1, param2, param3, (issus de la lecture
        de la configuration de contrôle xlsx).
        """
        requete_with_param = requete_sql
        if (self.description_param1) is not None and (param1 is not None):
            requete_with_param = requete_with_param.replace(self.description_param1, param1)
        if (self.description_param2) is not None and (param2 is not None):
            requete_with_param = requete_with_param.replace(self.description_param2, param2)
        if (self.description_param3) is not None and (param3 is not None):
            requete_with_param = requete_with_param.replace(self.description_param3, param3)
        return requete_with_param

    def get_entete(self, param1=None, param2=None, param3=None):
        """Fonction d'écriture de l'entete"""
        # Assemblage de l'entête
        sql_entete = (
            "SELECT '"
            + self.id
            + "' AS ID_Test, \""
            + self.description
            + "\" AS Description, '"
            + self.classe
            + "' AS Classe, '"
            + self.attr
            + "' AS Attribut, "
            + self.xxcode
            + " AS xx_code"
        )
        return self.insert_param_in_sql(sql_entete, param1, param2, param3)

    def get_sql(self, param1, param2, param3, version_sql="v3"):
        """Fonction d'écriture des requetes sql 1 et 2"""
        if self.check_param_compatibility(param1, param2, param3) > 0:
            print("ERREUR !!! Il y a un probleme dans les parametres du fichier de configuration")
        else:
            if version_sql == "v1":
                sql_requete_controle = (
                    self.get_entete(param1, param2, param3)
                    + " FROM ("
                    + self.reqprinc
                    + ") AS tb_ctrl WHERE "
                    + self.condition
                )
            elif version_sql == "v2":
                sql_requete_controle = (
                    self.get_entete(param1, param2, param3)
                    + " , "
                    + self.condition
                    + " AS Is_Error FROM ("
                    + self.reqprinc
                    + ") AS tb_ctrl"
                )
            elif version_sql == "v3":
                # print(self.id)
                # print(self.detail_erreur)
                # print(type(self.detail_erreur))
                sql_requete_controle = (
                    self.get_entete(param1, param2, param3)
                    + " , "
                    + str(self.detail_erreur)
                    + " AS DETAIL_ERREUR "
                    + " FROM ("
                    + self.reqprinc
                    + ") AS tb_ctrl WHERE "
                    + self.condition
                )
            return self.insert_param_in_sql(sql_requete_controle, param1, param2, param3)


def read_xlsx_catalogue(catalogue_file, column_config=catalogue_config):
    log("Lecture du catalogue de contrôle depuis le fichier %s" % (catalogue_file))
    # Création du dictionnaire de Controle ##
    # On lit dans un premiet temps le fichier excel dans un dict en définissant les colonnes nécessaires à l'instanciation des objets Controle
    # Récupération de la liste des colonnes obligatoires à partir de la configuration
    catalogue_cols = [colonne_name for colonne_name in column_config.values()]

    catalogue_dict = read_all_sheet_to_dict(catalogue_file, catalogue_cols, "id_test")
    # On parcours ensuite le dict pour créer un nouveau dict d'objets Controle
    catalogue_controle = dict()
    for i in catalogue_dict.values():
        nb_param = (
            (i[column_config["param1_col"]] is not None)
            + (i[column_config["param2_col"]] is not None)
            + (i[column_config["param3_col"]] is not None)
        )
        catalogue_controle[i["id_test"]] = Controle(
            i[column_config["id_test_col"]],
            i[column_config["description_col"]],
            i[column_config["classe_col"]],
            i[column_config["attribut_col"]],
            i[column_config["xx_code_col"]],
            i[column_config["param1_col"]],
            i[column_config["param2_col"]],
            i[column_config["param3_col"]],
            i[column_config["requ_princ_col"]],
            i[column_config["condition_col"]],
            i[column_config["detail_erreur_col"]],
            nb_param,
        )
    return catalogue_controle


def read_xlsx_config(config_file, column_config=config_controle_config):
    log("Lecture de la configuration de contrôle depuis le fichier %s" % (config_file))
    # Création du dictionnaire de configuration ##
    # Récupération de la liste des colonnes obligatoires à partir de la configuration
    config_cols = [colonne_name for colonne_name in column_config.values()]
    config_dict = read_all_sheet_to_dict(config_file, config_cols, "id_test")
    return config_dict


def translate_config_to_sql(
    catalogue_controle_xlsx,
    config_controle_xlsx,
    catalogue_column_config=catalogue_config,
    config_column_config=config_controle_config,
):
    log(
        "Traduction en SQL de la configuation de contrôle : \n"
        "Catalogue : %s\n"
        "Configuration : %s\n" % (catalogue_controle_xlsx, config_controle_xlsx)
    )
    catalogue = read_xlsx_catalogue(catalogue_controle_xlsx, catalogue_column_config)
    config = read_xlsx_config(config_controle_xlsx, config_column_config)
    # On crée d'abors une liste [] de points de contrôles SQL puis on appelle la foncion Controle.make_view_ctrl pour construire la vue.
    list_controles_sql = []
    for i in config.values():
        # Récupération des valeurs du dict pour une meilleur lisibilité
        controle_configuration = i[
            config_column_config["config_col"]
        ]  # valeur O ou N selon que le test est défini ou non dans la configuration de contrôle
        controle_id = i["id_test"]
        controle_param1 = i[config_column_config["param1_col"]]
        controle_param2 = i[config_column_config["param2_col"]]
        controle_param3 = i[config_column_config["param3_col"]]
        if controle_configuration == "O":
            list_controles_sql.append(
                catalogue[controle_id].get_sql(
                    controle_param1, controle_param2, controle_param3, version_sql="v3"
                )
            )
    # Construction du SQL de la vue dans un fichier
    sql_code = Controle.make_view_ctrl(list_controles_sql)
    return sql_code
