import sqlite3
import sys

# Устанавливаем кодировку
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('data/messages.db')
cursor = conn.cursor()

print('\n' + '='*120)
print('TABLE CONTENTS - Messages Database')
print('='*120)

# Получаем таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

if not tables:
    print('No tables found')
else:
    for table_name in tables:
        table = table_name[0]
        print(f'\n--- TABLE: {table} ---')

        # Получаем информацию о колонках
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        if table == 'messages':
            # Для таблицы messages показываем последние 20 записей
            cursor.execute(f'SELECT * FROM {table} ORDER BY created_at DESC LIMIT 20')
            rows = cursor.fetchall()

            if rows:
                # Заголовок таблицы
                print(f'{"ID":<5} {"USER_ID":<10} {"ROLE":<12} {"CONTENT (preview)":<40} {"LENGTH":<8} {"CREATED_AT":<20} {"DELETED":<8}')
                print('-'*120)

                # Данные
                for row in rows:
                    content_preview = (row[3][:37] + '...') if len(row[3]) > 40 else row[3]
                    deleted_status = "Yes" if row[6] else "No"
                    print(f'{row[0]:<5} {row[1]:<10} {row[2]:<12} {content_preview:<40} {row[4]:<8} {row[5]:<20} {deleted_status:<8}')
            else:
                print('No records found')

            # Статистика
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            total = cursor.fetchone()[0]
            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE is_deleted = 0')
            active = cursor.fetchone()[0]

            print(f'\nStatistics: Total: {total} | Active: {active} | Deleted: {total - active}')

        elif table == 'users':
            # Для таблицы users
            cursor.execute(f'SELECT * FROM {table} LIMIT 20')
            rows = cursor.fetchall()

            if rows:
                # Заголовок таблицы
                print(f'{"TELEGRAM_ID":<15} {"USERNAME":<15} {"FIRST_NAME":<15} {"LAST_NAME":<15} {"LANG":<6} {"CREATED_AT":<20}')
                print('-'*120)

                # Данные
                for row in rows:
                    print(f'{str(row[0]):<15} {str(row[1] or ""):<15} {str(row[2] or ""):<15} {str(row[3] or ""):<15} {str(row[4] or ""):<6} {str(row[5]):<20}')
            else:
                print('No records found')

            # Статистика
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            total = cursor.fetchone()[0]
            print(f'\nTotal users: {total}')

print('\n' + '='*120 + '\n')

conn.close()
