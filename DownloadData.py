import urllib2
import datetime
import os.path
import shutil
import traceback
import os
import sys
import sqlite3

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def get_element(element, tag, ret_value):
    if element.find(tag) is None:
        # print("Warning: tag " + tag + " has not been found.")
        return ret_value
    else:
        """Check corrupted tags."""
        value = element.find(tag).text
        if value is None:
            value = ret_value
        return value


def parseXML(path, date, log):
    """Parse XML file into traff.db database

    Keyword arguments:
        path -- path to the XML file
        date -- date of the file
        log -- log handler
    """
    cwd = os.path.abspath(os.path.dirname(sys.argv[0])) + '/'
    inserted_obs = 0

    try:
        """Connect DB"""
        conn_db = sqlite3.connect(cwd + 'data/traff.db')
        c = conn_db.cursor()
        log.write("..... DB opened.\r\n")

        """Parse XML."""
        tree = ET.parse(path)
        t_iter = tree.iter(tag='pm')
        log.write("..... XML parsed.\r\n")

        """Every element contains the information for one unique access."""
        for elem in t_iter:
            """Firstly, get the access code."""
            codigo = get_element(elem, 'codigo', '-1')

            """If no code is found, then the information of this element is useless."""
            if codigo == '-1':
                print("ERROR: 'codigo' could not be found. Nothing inserted for this element.")
                continue

            """After checking the code, the error parameter is checked (N = No error, S = Error)."""
            error = get_element(elem, 'error', 'S')

            if error == 'N':

                descripcion = get_element(elem, 'descripcion', 'N/A').encode("iso-8859-1")
                intensidad = get_element(elem, 'intensidad', "-1")
                ocupacion = get_element(elem, 'ocupacion', "-1")
                carga = get_element(elem, 'carga', "-1")
                nivelServicio = get_element(elem, 'nivelServicio', "-1")
                intensidadSat = get_element(elem, 'intensidadSat', "-1")
                subarea = get_element(elem, 'subarea', "-1")
                if intensidadSat == "-1" and subarea == "-1":
                    velocidad = get_element(elem, 'velocidad', "-1")
                else:
                    velocidad = "-1"

                stm_check_codigo = ("SELECT codigo FROM accesos WHERE codigo = '" + codigo + "';")
                c.execute(stm_check_codigo)
                if c.fetchone() is None:
                    if intensidadSat == -1:
                        stm_insert_access = (
                            "INSERT INTO accesos(codigo,tipo,descripcion,utm_x,utm_y,longitud,latitud) VALUES ('"
                            + codigo + "','INTERURBANO','" + codigo + "',0,0,0,0);")
                    else:
                        stm_insert_access = (
                            "INSERT INTO accesos(codigo,tipo,descripcion,intensidad_sat,subarea,utm_x,utm_y,longitud,latitud) VALUES ('"
                            + codigo + "','URBANO','" + descripcion + "'," + intensidadSat + "," + subarea + ",0,0,0,0);")
                    print(stm_insert_access)
                    log.write("..... New access added with code " + codigo + ".\r\n")
                    c.execute(stm_insert_access)

                if velocidad == -1:
                    sql_stm = (
                        "INSERT INTO observaciones (codigo,fecha,intensidad,ocupacion,carga,nivel_servicio) VALUES ('"
                        + codigo + "','" + date + "'," + intensidad + "," + ocupacion + "," + carga + "," + nivelServicio
                        + ");")
                else:
                    sql_stm = ("INSERT INTO observaciones VALUES ('"
                               + codigo + "','" + date + "'," + intensidad + "," + ocupacion + "," + carga + "," + nivelServicio
                               + "," + velocidad + ");")
                #print(sql_stm)
                c.execute(sql_stm)
                inserted_obs += 1
            else:
                print("Error in " + codigo + " data.")
                #log.write("..... Error in " + codigo + " data.\r\n")

        conn_db.commit()

    except ET.ParseError as parse_error:
        print("ERROR: Error parsing XML file")
        log.write("ERROR: Error parsing XML file\r\n")

    except Exception as e:
        print(
            "ERROR: Codigo: " + codigo + ", Intensidad: " + intensidad + ", Ocupacion: " + ocupacion + ", Carga: " + carga + ", nivelServicio: " + nivelServicio)
        log.write(
            "ERROR: Codigo: " + codigo + ", Intensidad: " + intensidad + ", Ocupacion: " + ocupacion + ", Carga: " + carga + ", nivelServicio: " + nivelServicio + "\r\n")
        #print sql_stm
        #log.write(sql_stm + "\r\n")
        #raise e
        traceback.print_exc()
        log.write(traceback.print_exc() + "\r\n")

    finally:
        #TODO - Incluir numero observaciones anadidas / numero observaciones totales
        print "Total observations inserted: ", inserted_obs
        log.write("... Total observations inserted: " + str(inserted_obs) + "\r\n")
        conn_db.close()


if __name__ == '__main__':

    """Download remote XML file."""
    xml_path = 'http://informo.munimadrid.es/informo/tmadrid/pm.xml'
    remote_file = urllib2.urlopen(xml_path)
    """Get remote XML last modification date."""
    rf_datetime = datetime.datetime(*remote_file.info().getdate('last-modified')[0:6])
    """Check if already exists a file with the same date (which is written in the filename)."""
    local_file_name = rf_datetime.strftime("%Y%m%d_%H%M")
    cwd = os.path.abspath(os.path.dirname(sys.argv[0])) + '/'
    local_file_path = cwd + "data/" + local_file_name + ".xml"

    if not os.path.isfile(local_file_path):
        """If no file is found with that filename, download it."""
        with open(local_file_path, 'w') as local_file:
            shutil.copyfileobj(remote_file, local_file)
            """Open log file."""
            log = open(cwd + 'data/download.log', 'a')
            print("Downloaded file " + local_file_name + ".xml")
            log.write("Downloaded file " + local_file_name + ".xml\r\n")
            local_file.close()
            print("... reading file " + local_file_path + " into database...")
            log.write("... reading file into database...\r\n")
            """Parse new XML file into database."""
            parseXML(local_file_path, rf_datetime.strftime("%Y-%m-%d %H:%M:%S"), log)
            log.write("... FINISHED\r\n")
            log.close()
