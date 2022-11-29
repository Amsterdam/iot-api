from iot import models
from iot.dateclasses import PersonData


def import_person(person_data: PersonData, action_logger=lambda x: x):
    """
    Import person data parsed from an iprox or bulk registration excel
    file.
    """
    names = [person_data.first_name]

    if person_data.last_name_affix:
        names.append(person_data.last_name_affix)

    names.append(person_data.last_name)

    owner, _ = action_logger(
        models.Person.objects.update_or_create(
            email=person_data.email,
            organisation=person_data.organisation,
            defaults={
                'name': ' '.join(names),
                'telephone': person_data.telephone,
                'website': person_data.website,
            },
        )
    )

    return owner
