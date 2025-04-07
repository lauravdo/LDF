import os
import logging
from collector import verzamel_systeeminfo, gebruikers_info, geinstalleerde_software, actieve_processen, netwerk_config, usb_info

# Log configuratie
logging.basicConfig(level=logging.INFO)

def logbestand_legen(bestandsnaam):
    """Leeg het logbestand als het bestaat."""
    if os.path.exists(bestandsnaam):
        os.remove(bestandsnaam)
        logging.info(f"Logbestand {bestandsnaam} is geleegd.")

def schrijf_naar_log(bestandsnaam, titel, data):
    """Schrijf data naar het logbestand."""
    with open(bestandsnaam, "a") as f:
        f.write(f"\n=== {titel} ===\n")
        # Verander de data van een lijst naar een enkele string voordat we het naar het bestand schrijven
        f.write(data + "\n")

def main():
    """Hoofd functie die systeeminformatie verzamelt en naar een logbestand schrijft."""
    
    logbestand = "output_log.txt"
    
    # Leeg het logbestand bij elke draai
    logbestand_legen(logbestand)
    
    # Verzamel informatie
    systeeminfo = verzamel_systeeminfo()
    gebruikersinfo = gebruikers_info()
    software_info = geinstalleerde_software()
    actieve_processen_info = actieve_processen()
    netwerk_info = netwerk_config()
    usb_info_data = usb_info()

    # Schrijf de verzamelde informatie naar het logbestand
    schrijf_naar_log(logbestand, "Systeeminformatie", systeeminfo)
    schrijf_naar_log(logbestand, "Gebruikersinformatie", gebruikersinfo)
    schrijf_naar_log(logbestand, "Geïnstalleerde Software", software_info)
    schrijf_naar_log(logbestand, "Actieve Processen", actieve_processen_info)
    schrijf_naar_log(logbestand, "Netwerkconfiguratie", netwerk_info)
    schrijf_naar_log(logbestand, "USB-informatie", usb_info_data)

    logging.info("Alle informatie is verzameld en opgeslagen in output_log.txt")

if __name__ == "__main__":
    main()