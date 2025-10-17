import sqlite3

conn = sqlite3.connect('data/messages.db')
cursor = conn.cursor()

# Получаем последние 20 записей
cursor.execute('SELECT * FROM messages ORDER BY created_at DESC LIMIT 20')
rows = cursor.fetchall()

print('\n' + '='*120)
print('📊 MESSAGES TABLE (last 20 records)')
print('='*120)

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
    print('\n❌ No records found')

print('-'*120)

# Статистика
cursor.execute('SELECT COUNT(*) FROM messages')
total = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM messages WHERE is_deleted = 0')
active = cursor.fetchone()[0]

print(f'\n📈 Statistics: Total records: {total} | Active: {active} | Deleted: {total - active}')
print('='*120 + '\n')

conn.close()
