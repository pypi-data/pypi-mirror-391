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
from logging.handlers import RotatingFileHandler

from .__about__ import __version__ as version_number

# ############################################################################
# ########## Globals ###############
# ##################################
log_in_qgis_processing = False  # if true, the function will call feedback.pushInfo(str(msg))
log_in_qgis_processing_method = None  # refer the function to call (feedback.pushInfo)

# loggers = dict()


# ############################################################################
# ########## Functions #############
# ##################################
def log(message, logger, level):
    """
    Log message to Logger "logger" but also call Qgis processig logging function
    if log_in_qgis_processing is True
    """
    switcher = {"info": logger.info, "warning": logger.warning, "debug": logger.debug}
    switcher[level](message)
    if log_in_qgis_processing and level in ("info", "warning"):
        log_in_qgis_processing_method(f"[qi_{version_number}] {message}")


def add_console_handler(logger, logLevel=logging.INFO):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logLevel)
    formatter = logging.Formatter("%(levelname)s :: %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def add_file_handler(logger, file, logLevel=logging.DEBUG):
    # création d'un handler qui va rediriger une écriture du log vers
    # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
    file_handler = RotatingFileHandler(file, "a", 1000000, 1)
    file_handler.setLevel(logLevel)
    formatter = logging.Formatter(
        f"%(asctime)s :: %(levelname)s :: qi_{version_number} %(module)s  %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# def init_Logger(console = False, file = False, loggerName = None, logLevel = logging.DEBUG):
#     """
#     Création d'un nouveau logger, ou bien retourne le logger existant si la fonction
#     a déja été appelée.
#     """
#     # création de l'objet logger qui va nous servir à écrire dans les logs
#     global loggers
#     #dealing with root logger for dictionary index
#     logger_index = loggerName if loggerName != None else 'root'
#     if logger_index not in loggers.keys():
#         loggers[logger_index] = logging.getLogger(loggerName)
#         loggers[logger_index].setLevel(logLevel)
#         if file :
#             # création d'un handler qui va rediriger une écriture du log vers
#             # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
#             file_handler = RotatingFileHandler(file, 'a', 1000000, 1)
#             file_handler.setLevel(logLevel)
#             formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
#             file_handler.setFormatter(formatter)
#             loggers[logger_index].addHandler(file_handler)
#         if console:
#             stream_handler = logging.StreamHandler()
#             stream_handler.setLevel(logLevel)
#             formatter = logging.Formatter('%(levelname)s :: %(message)s')
#             stream_handler.setFormatter(formatter)
#             loggers[logger_index].addHandler(stream_handler)
#     try:
#         return(loggers[logger_index])
#     except Exception as e:
#         print(e)
#         print(loggers)
#
# def get_logger(loggerName = None):
#     logger_index = loggerName if loggerName != None else 'root'
#     return loggers[loggerName]
