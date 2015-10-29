import psycopg2
import csv
import codecs
import os
import re

class PGBackend:

    def __init__(self, user="postgres", password="postgres", host="localhost", port='5432', repo_base=None):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.repo_base = repo_base

        self.__open_connection__()

    def __open_connection__(self):
        self.connection = psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.repo_base)

    def execute_sql(self, query, params=None):
        result = {
            'status': False,
            'row_count': 0,
            'tuples': [],
            'fields': []
        }

        conn = self.connection
        c = conn.cursor()
        c.execute(query.strip(), params)

        try:
            result['tuples'] = c.fetchall()
        except:
            pass

        result['status'] = True
        result['row_count'] = c.rowcount
        if c.description:
            result['fields'] = [
                {'name': col[0], 'type': col[1]} for col in c.description]

        tokens = query.strip().split(' ', 2)
        c.close()
        return result

    def import_file(self, table_name, file_path, file_format='CSV',
      delimiter=',', header=True, encoding='ISO-8859-1', quote_character='"'):
        try:
            header_option = 'HEADER' if header else ''
            if quote_character == "'":
                quote_character = "''"

            escape = ''
            if delimiter.startswith('\\'):
                escape = 'E'

            return self.execute_sql(
                ''' COPY %s FROM '%s'
                    WITH %s %s DELIMITER %s'%s' ENCODING '%s' QUOTE '%s';
                ''' %(table_name, file_path, file_format,
                    header_option, escape, delimiter, encoding, quote_character))
        except Exception, e:
            self.execute_sql(
                ''' DROP TABLE IF EXISTS %s;
                ''' %(table_name))
            raise ImportError(e);

def clean_str(text, prefix):
    s = text.strip().lower()

    # replace whitespace with '_'
    s = re.sub(' ', '_', s)

    # remove invalid characters
    s = re.sub('[^0-9a-zA-Z_]', '', s)

    # remove leading characters until a letter or underscore
    s = re.sub('^[^a-zA-Z_]+', '', s)

    if s == '':
        return clean_str(prefix + text, '')

    return s

def file_import(repo_base, repo, file_name):
    delimiter = ','
    header = True
    quote_character = ''
    delimiter = delimiter.decode('string_escape')
    repo_dir = '/user_data/%s/%s/' %(repo_base, repo)
    file_path = repo_dir + file_name
    table_name, _ = os.path.splitext(file_name)
    table_name = clean_str(table_name, 'table')
    dh_table_name = '%s.%s.%s' %(repo_base, repo, table_name)

    f = codecs.open(file_path, 'r', 'ISO-8859-1')
    data = csv.reader(f, delimiter=delimiter)
    cells = data.next()

    columns = [clean_str(str(i), 'col') for i in range(0, len(cells))]
    if header:
        columns = map(lambda x: clean_str(x, 'col'), cells)

    #columns = rename_duplicates(columns)

    query = 'CREATE TABLE %s (%s text' % (dh_table_name, columns[0])

    for i in range(1, len(columns)):
        query += ', %s %s' %(columns[i], 'text')
    query += ')'

    print query
    manager = PGBackend(repo_base=repo_base)
    manager.execute_sql(query=query)
    manager.import_file(table_name=table_name,
                        file_path=file_path
                        )
