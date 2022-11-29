from django.conf import settings

IPROX_REGISTRATION_FIELDS = [
    "Verzonden",
    "Status",
    "Referentienummer",
    "Wilt u meer dan 5 sensoren melden?",
    "Vul uw e-mailadres in",
]
IPROX_SENSOR_FIELDS = [
    "Kies soort / type sensor",
    "Locatie sensor",
    "Hebt u een postcode en huisnummer?",
    "Postcode",
    "Huisnummer",
    "Toevoeging",
    "Omschrijving van de locatie van de sensor",
    "In welk gebied bevindt zich de mobiele sensor?",
    "Wat meet de sensor?",
    "Waarvoor meet u dat?",
    "Kies een of meerdere thema's",
    "Worden er persoonsgegevens verwerkt?",
    "Privacyverklaring",
    "Wettelijke grondslag",
    "Wanneer wordt de sensor verwijderd?",
    "Wilt u nog een sensor melden?",
]
IPROX_PERSON_FIELDS = [
    "Naam organisatie/bedrijf",
    "E-mail",
    "Postcode",
    "Huisnummer",
    "Toevoeging",
    "Straatnaam",
    "Plaatsnaam",
    "KVK-nummer",
    "Website",
    "Voornaam",
    "Tussenvoegsel",
    "Achternaam",
    "Telefoonnummer",
]
BULK_PERSON_FIELDS = [
    "Naam organisatie/bedrijf",
    "Postcode",
    "Huisnummer",
    "Toevoeging (niet verplicht)",
    "Straatnaam",
    "Plaatsnaam",
    "E-mail",
    "Telefoonnummer",
    "KVK-nummer (niet verplicht)",
    "Website (niet verplicht)",
    "Voornaam",
    "Tussenvoegsel (niet verplicht)",
    "Achternaam",
]
BULK_SENSOR_FIELDS = [
    "Referentie",
    "Kies soort / type sensor",
    "Latitude",
    "Longitude",
    "In welk gebied bevindt zich de mobiele sensor?",
    "Wat meet de sensor?",
    "Waarvoor meet u dat?",
    "Thema 1",
    "Thema 2 (niet verplicht)",
    "Thema 3 (niet verplicht)",
    "Thema 4 (niet verplicht)",
    "Thema 5 (niet verplicht)",
    "Thema 6 (niet verplicht)",
    "Thema 7 (niet verplicht)",
    "Thema 8 (niet verplicht)",
    "Worden er persoonsgegevens verwerkt?",
    "Wettelijke grondslag",
    "Privacyverklaring",
    "Wanneer wordt de sensor verwijderd?",
    "Opmerking (niet verplicht)",
    "Project",
]
ALL_IPROX_SENSOR_FIELDS = IPROX_SENSOR_FIELDS * settings.IPROX_NUM_SENSORS
ALL_IPROX_SENSOR_FIELDS.pop()  # Last sensor does not have "Wilt u nog een sensor melden?"
IPROX_FIELDS = IPROX_REGISTRATION_FIELDS + IPROX_PERSON_FIELDS + ALL_IPROX_SENSOR_FIELDS

# Between iprox / bulk - we expect the same fields, they are just named differently
assert len(BULK_PERSON_FIELDS) == len(IPROX_PERSON_FIELDS)
