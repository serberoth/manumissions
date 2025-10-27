import csv
import datetime
import logging
import re
from django.core.management.base import BaseCommand
from django.db.models import Count, Max

from catalog.models import * 

LOGGER = logging.getLogger("ReloadCSVCommand")

class Enslaved(object):
    def __init__(self, name, listed_age, freed_age, gender):
        self.name = name
        self.listed_age = listed_age
        self.freed_age = freed_age
        self.gender = gender

class Slaveholder(object):
    def __init__(self, name_transcribed, name_unabbreviated, gender):
        self.name_transcribed = name_transcribed
        self.name_unabbreviated = name_unabbreviated
        self.gender = gender

class Witness(object):
    def __init__(self, name_transcribed, name_unabbreviated):
        self.name_transcribed = name_transcribed
        self.name_unabbreviated = name_unabbreviated

class MeetingClert(object):
    def __init__(self, name_transcribed, name_unabbreviated):
        self.name_transcribed = name_transcribed
        self.name_unabbreviated = name_unabbreviated

class DataRow(object):
    VALID_GENDERS = [ 'male', 'female', '' ]

    def __init__(self, row_num, dict):
        # This function splits the provided line item by the provided separator value (defaulted to `,`)
        # and strips each value of any preceeding or trailing whitespace then returns the list of those
        # values, if there is only one item in the line item then a list containing the entire line item
        # is returned.
        def split_or_pad(row_num, names, line_item, separator = ','):
            if '' == line_item.strip():
                LOGGER.debug(f'{row_num} :: Padding data item {len(names)} times')
                return [ '' ] * len(names)
            return [ s.strip() for s in line_item.split(separator) ]
        
        # This function builds a list of ages from the provided line item.  The list can either be a comma separated list
        # or a ranged list separated by semi-colons.  Each range must match to a set of names listed in the provided names
        # list and they must be in the provided order.  The function does not verify for overlapping ranges or ranged provided
        # in reverse order (i.e. 1-5;3-8 or 4-2;6-8).  Iff a range is provided then it must be in the form `<name>-<name> - <age>`
        # with the whitespace padding as optional for ease of data entry.
        def build_age_list(row_num, names, line_item):
            if not (';' in line_item):
                return split_or_pad(row_num, names, line_item)

            # Peter-Milly - all over 21;   James-Hannah - all under 21
            ranges = [ s.strip() for s in line_item.split(';') ]
            ages = [ '' ] * len(names)
            for item in ranges:
                _, start, end, age, _ = re.split(r'^(\w+)\s*\-\s*(\w+)\s*\-\s*(.+)$', item)
                age = age.replace('all', '').strip()
                LOGGER.debug(f'Start: `{start}` End: `{end}` Age: `{age}`')
                in_range = False
                for idx, name in enumerate(names):
                    if name == start:
                        in_range = True
                    if in_range:
                        LOGGER.debug(f'{name} is in range {names}')
                        ages[idx] = age
                    if name == end:
                        in_range = False
            return ages
        
        # Resolve the gender values in the provided line item, the line item can contain a few different values which indicate
        # to this function for how to expand said values.  Iff the provided line_item matches the following values exactly then
        # perform the following:
        # `males`: return a list of values containing `male` one for each name
        # `females`: return a list of values containing `female` one for each name
        # otherwise split the line_item by `,` strip any whitespace from the values and then ensure that each item is one of the
        # values in the VALID_GENDERS list, currently defined as either `male`, `female`, or '' for unknown other values can be
        # added to the list as demand requires.
        def resolve_genders(row_num, names, line_item):
            match line_item.strip():
                case 'males':
                    LOGGER.debug(f'{row_num} :: Asserting all names are male')
                    return [ 'male' ] * len(names)
                case 'females':
                    LOGGER.debug(f'{row_num} :: Asserting all names are female')
                    return [ 'female' ] * len(names)
                case _:
                    vals = [ val.lower() for val in split_or_pad(row_num, names, line_item) ]
                    count = 0
                    for val in DataRow.VALID_GENDERS:
                        count += vals.count(val)
                    assert count == len(vals), f'{row_num} :: Invalid gender listing in line item {line_item} for names {names}'
                    return vals
        
        def build_name_list(row_num, names, line_item):
            if re.match(r'^(\w+\s+\w+)(,\s*\w+\s+\w+)+', line_item):
                names = [ s.strip() for s in line_item.split(',') ]
                return [ ", ".join(reversed(s.split(' '))) for s in names ]
            if names == None:
                if ' and ' in line_item:
                    return [ s.strip() for s in line_item.split('and') ]
                return [ s.strip() for s in line_item.split(';') ]
            if ' and ' in line_item:
                return split_or_pad(row_num, names, line_item, 'and')
            return split_or_pad(row_num, names, line_item, ';')

        '''
        CSV Data Columns: (Total Manumission Metadata QMP+Blackwater.xlsx)
        Page Number,
        Image Name (HC10-10002_XXX),
        Date (YYYY-MM-DD),
        Name of Enslaved Person (Transcribe what is listed),
        Age listed for Enslaved Person,
        Freed Age,
        Assumed Gender of Enslaved Person,
        Monthly Meeting,
        "Place (Township, County, etc)",
        "Transcribed - Name of Slaveholder (Last name, First name)",
        "Unabbreviated - Name of Slaveholder (Last name, First name)",
        Gender of Slaveholder,
        "Transcribed - Witnesses (Last name, First name)",
        "Unabbreviated - Witnesses (ex: ""Sealed and delivered in the Presence of..."") (Last name, First name)",
        "Transcribed - Monthly Meeting Clerk (Last Name, First Name)",
        "Unabbreviated - Clerk (Last name, First name)",
        Notes,
        Call Number,
        '''
        self.row_num = row_num
        self.page_number = dict['Page Number'].strip()
        self.image_name = dict['Image Name (HC10-10002_XXX)'].strip()
        # NOTE: Row 339 has no date value
        self.date = dict['Date (YYYY-MM-DD)'].strip()

        self.manumission_title = f'Manumission of {dict['Name of Enslaved Person (Transcribe what is listed)']}, {self.date}'

        # NOTE: [MITIGATED - removed `&`] Row 58 has a comma separated list of names including a stray &
        # NOTE: [MITIGATED - def build_age_list(...)] Row 58 the listed ages are associated with a range of names, plus are non-numeric in nature
        # NOTE: [MITIGATED - duplicated gender value] Row 123 has 3 names, a blank on ages, and only one gender associated to all names
        # NOTE: [MITIGATED - This is accepted by the model ] Row 164, 275 has a floating point age for one of the listed people
        # NOTE: Row 201 has no names listed???
        # NOTE: [MITIGATED - added in missing `,`] Row 121 has `Sela, Dinah, James, Thomas Ishmael, London` for `Name of Enslaved Person`
        # This is potentially a comma separated list of names
        self.enslaved_name = [ s.strip() for s in dict['Name of Enslaved Person (Transcribe what is listed)'].split(',') ]
        # This is potentially a comma separated list of ages
        self.listed_age = build_age_list(row_num, self.enslaved_name, dict['Age listed for Enslaved Person'])
        # This is potentially a comma separated list of ages
        self.freed_age = split_or_pad(row_num, self.enslaved_name, dict['Freed Age'])
        # NOTE: [MITIGATED - def resolve_genders(...)] Row 106 has two names with the word `males` in this column which indicates that both are male
        # NOTE: [MITIGATED - normalized value to `male`] Row 302 has a gender of `1 male`
        # NOTE: [MITIGATED - normalized value to `female`] Row 88 has a gender of `femaie`
        # NOTE: Row 164 has 6 genders listed but 7 names
        # NOTE: [MITIGATED - normalized value to `females`] Row 181 has a gender value of `female` and 3 `name of enslaved person` names
        # NOTE: Row 216 has 2 genders listed but 6 names
        # NOTE: [MITIGATED - normalized value to `females`] Row 271 has a gender value of `female` and 2 `name of enslaved person` names
        # This is potentially a comma separated list of genders
        self.enslaved_gender = resolve_genders(row_num, self.enslaved_name, dict['Assumed Gender of Enslaved Person'])

        LOGGER.debug(f'{row_num} :: {self.enslaved_name} == {self.listed_age} == {self.freed_age} {self.enslaved_gender}')
        assert len(self.enslaved_name) == len(self.listed_age) == len(self.freed_age) == len(self.enslaved_gender), f'{row_num} :: {self.enslaved_name} == {self.listed_age} == {self.freed_age} == {self.enslaved_gender}'
        self.enslaved = map(lambda name, listed_age, freed_age, gender: Enslaved(name, listed_age, freed_age, gender), self.enslaved_name, self.listed_age, self.freed_age, self.enslaved_gender)



        self.monthly_meeting = dict['Monthly Meeting'].strip()
        self.place = dict['Place (Township, County, etc)'].strip()



        # NOTE: [MITIGATED - added missing comma] Row 10 contained `Walmsley, Susannah; Walmsley, Thomas; Walmsley William` for `Name of Slaveholder` missing comma between last and first
        # NOTE: [MITIGATED - name formatted to match appearance in row 277] Row 278, 280, 281, 282 contains `Abijah Dawes` in the "Unabbreviated - Name of Slaveholder" and "Transcribed - Name of Slaveholder" columns
        # NOTE: This is potentially a semi-colon separated list of names (last, first)
        self.slaveholder_name_unabbreviated = [ s.strip() for s in dict['Unabbreviated - Name of Slaveholder (Last name, First name)'].split(';') ]
        # NOTE: This is potentially a semi-colon separated list of names (last, first)
        self.slaveholder_name_transcribed = split_or_pad(row_num, self.slaveholder_name_unabbreviated, dict['Transcribed - Name of Slaveholder (Last name, First name)'], ';')
        # NOTE: [MITIGATED - def resolve_genders(...)] Row 268 has a single entry for gender of `males` indicating all named are male
        # This is potentially a comma separated list of genders
        self.slaveholder_gender = resolve_genders(row_num, self.slaveholder_name_unabbreviated, dict['Gender of Slaveholder'])

        LOGGER.debug(f'{row_num} :: {self.slaveholder_name_transcribed} == {self.slaveholder_name_unabbreviated} == {self.slaveholder_gender}')
        assert len(self.slaveholder_name_transcribed) == len(self.slaveholder_name_unabbreviated) == len(self.slaveholder_gender), f'{row_num} :: {self.slaveholder_name_transcribed} == {self.slaveholder_name_unabbreviated} == {self.slaveholder_gender}'
        self.slaveholder = map(lambda name_transcribed, name_unabbreviated, gender: Slaveholder(name_transcribed, name_unabbreviated, gender), self.slaveholder_name_transcribed, self.slaveholder_name_unabbreviated, self.slaveholder_gender)



        # NOTE: Row 3 contains `Townsend, John; Bolton, Isaac, Pemberton,` for Unabbreviated - Witnesses and Transcribed - Witnesses failing to match established patterns
        # NOTE: [MITIGATED - build_name_list adjusted to handle and case] Row 28 contains `Pretlow, John and Ricks, Thomas` for `Unabbreviated - Witnesses`
        # NOTE: [MITIGATED - build_name_list adjusted to handle and case] Row 28 contains `Pretlow, John and Richs, Thos` for `Transcribed - Witnesses`
        # NOTE: [MITIGATED - replaced `,` with `;` to match unabbreviated column] Row 51 contains "Bailey, Joseph, Cornwell, John, Jones, Sam" in the "Transcribed - Witnesses (Last name, First name)" column
        # NOTE: [MITIGATED - updated to match header format (<last>, <first>)] Row 88 contains "Ezekiel Cleaver, Joshua Morris" in the "Unabbreviated - Witnesses..." column
        # NOTE: [MITIGATED - updated to match header format (<last>, <first>)] Row 161 contains "Thomas Say" in the "Unabbreviated - Witnesses..." column
        # NOTE: [MITIGATED - replaced `,` with `;` and removed extra comma before `Jr`] Row 215 contains `Richardson, Joseph, Richardson, Joseph, Jr.` using a comma instead of the `;` delimiter
        # NOTE: [MITIGATED - deleted comma before Jr.] Row 303 contains "Morris, William, Jr.; Carson, John" in the "Unabbreviated - Witnesses..." column
        # NOTE: This is potentially a semi-colon separated list of names (last, first)
        self.witness_unabbreviated = build_name_list(row_num, None, dict['Unabbreviated - Witnesses (ex: "Sealed and delivered in the Presence of...") (Last name, First name)'])
        # NOTE: This is potentially a semi-colon separated list of names (last, first)
        self.witness_transcribed = build_name_list(row_num, self.witness_unabbreviated, dict['Transcribed - Witnesses (Last name, First name)'])
        LOGGER.debug(f'{row_num} :: {self.witness_transcribed} == {self.witness_unabbreviated}')
        assert len(self.witness_transcribed) == len(self.witness_unabbreviated), f'{row_num} :: {self.witness_transcribed} == {self.witness_unabbreviated}'
        self.witness = map(lambda name_transcribed, name_unabbreviated: Witness(name_transcribed, name_unabbreviated), self.witness_transcribed, self.witness_unabbreviated)



        self.meeting_clerk_transcribed = dict['Transcribed - Monthly Meeting Clerk (Last Name, First Name)'].strip()
        self.meeting_clerk_unabbreviated = dict['Unabbreviated - Clerk (Last name, First name)'].strip()
        self.meeting_clerk = MeetingClert(self.meeting_clerk_transcribed, self.meeting_clerk_unabbreviated)



        self.notes = dict['Notes']
        self._call_number = dict['Call Number']

    @staticmethod
    def load_rows(data):
        reader = csv.DictReader(data)
        row_num = 2
        rows = []
        for row in reader:
            LOGGER.info(f'@@@ ROW#{row_num} => {row}')
            # FIXME: Skip these two problematic rows.... see the notes above
            if row_num == 164 or row_num == 216:
                print(f'{row_num} :: PROBLEMATIC ROW - SKIPPING')
                row_num += 1
                continue
            rows.append(DataRow(row_num, row))
            row_num += 1
        return rows



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_path', nargs='+', type=str)

    def handle(self, *args, **options):
        data_rows : list[DataRow] = []
        with open(options['csv_path'][0]) as data:
            data_rows = DataRow.load_rows(data)

        print('================================================================================')
        print('WITNESS LIST')
        for row in data_rows:
            # Get or create the witness person from the data in the row
            for witness in row.witness:
                if witness.name_unabbreviated == '':
                    continue
                print(f'{row.row_num} :: WITNESS `{witness.name_unabbreviated}`')
                last_name, first_name = [ s.strip() for s in witness.name_unabbreviated.split(',') ]
                print(f'{row.row_num} :: WITNESS [ LastName: "{last_name}" FirstName: "{first_name}" ]')
                person, _ = Person.objects.get_or_create(first_name = first_name, last_name = last_name)
                role, _ = Role.objects.get_or_create(name = 'Witness')
                person.role.add(role)
        print('')
        print('')
        print('')

        for row in data_rows:
            page_number, _  = Page_Number.objects.get_or_create(page_number = row.page_number)
            image_name, _   = Image_name.objects.get_or_create(image_name = row.image_name)

            date_of_manumission_signing = None
            if row.date != '':
                date = row.date.split('-')
                date_of_manumission_signing = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
            monthly_meeting, _ =    Monthly_Meeting.objects.get_or_create(monthly_meeting = row.monthly_meeting)
            place_freed, _ =        Place_Freed.objects.get_or_create(place_freed = row.place)

            # Get or create the base Manumission object to which each other item will be associated
            manumission, _ = Manumission.objects.get_or_create(
                title           = row.manumission_title,
                date_of_manumission_signing = date_of_manumission_signing,
                image_name      = image_name,
                page_number     = page_number,
                monthly_meeting = monthly_meeting
            )
            print('================================================================================')
            print(f'{row.row_num} :: MANUMISSION [ Title: "{row.manumission_title}" Date: {date_of_manumission_signing} ImageName: {image_name} PageNumber: {page_number} MonthlyMeeting: {monthly_meeting} ]')

            # Get or create each of the enslaved people from the data in the row
            for enslaved_person in row.enslaved:
                gender, _ = Gender.objects.get_or_create(gender = enslaved_person.gender)
                age_freed, _ = Age_Freed.objects.get_or_create(age_freed = enslaved_person.freed_age)
                age_listed, _ = Age_Listed.objects.get_or_create(age_listed = enslaved_person.listed_age)
                print(f'{row.row_num} :: SLAVE [ Name: "{enslaved_person.name}" Gender: {enslaved_person.gender} FreedAge: {enslaved_person.freed_age} ListedAge: {enslaved_person.listed_age} PlaceFreed: "{row.place}" ]')
                person, _ = Person.objects.get_or_create(
                    first_name = enslaved_person.name,
                    gender = gender,
                    age_freed = age_freed,
                    age_listed = age_listed,
                    year_manumitted = row.date,
                    place_freed = place_freed,
                )
                role, _ = Role.objects.get_or_create(name = 'Enslaved Person')
                person.role.add(role)
                manumission.person.add(person)

            # Get or create each of the slaveholders from the data in the row
            for slaveholder in row.slaveholder:
                # if slaveholder.name_unabbreviated == '':
                #     continue
                last_name, first_name = '', slaveholder.name_unabbreviated
                if ',' in slaveholder.name_unabbreviated:
                    last_name, first_name = [ s.strip() for s in slaveholder.name_unabbreviated.split(',') ]
                abbrev_first_name, abbrev_last_name = '', ''
                if slaveholder.name_transcribed != '':
                    abbrev_last_name, abbrev_first_name = [ s.strip() for s in slaveholder.name_transcribed.split(',') ]
                print(f'{row.row_num} :: SLAVEHOLDER [ LastName: "{last_name}" FirstName: "{first_name}" AbbrevLastName: "{abbrev_last_name}", AbbrevFirstName: "{abbrev_first_name}" Gender: {slaveholder.gender} ]')
                gender, _ = Gender.objects.get_or_create(gender = slaveholder.gender)
                person, _ = Person.objects.get_or_create(
                    first_name = first_name,
                    last_name = last_name,
                    abbreviated_first_name = abbrev_first_name,
                    abbreviated_last_name = abbrev_last_name,
                    gender = gender,
                )
                role, _ = Role.objects.get_or_create(name = 'Slaveholder')
                person.role.add(role)
                manumission.person.add(person)

            # Get or create the witness person from the data in the row
            for witness in row.witness:
                if witness.name_unabbreviated == '':
                    continue
                # print(f'{row.row_num} :: WITNESS {witness.name_unabbreviated}')
                last_name, first_name = [ s.strip() for s in witness.name_unabbreviated.split(',') ]
                person, _ = Person.objects.get(first_name = first_name, last_name = last_name)
                print(f'{row.row_num} :: WITNESS [ LastName: "{last_name}" FirstName: "{first_name}" ]')
                role, _ = Role.objects.get_or_create(name = 'Witness')
                person.role.add(role)
                manumission.person.add(person)
            print('')
        print('')
        print('')
            
        LOGGER.info('Reload Completed Successfully')
        self.stdout.write(self.style.SUCCESS('Reload Completed Successfully'))
