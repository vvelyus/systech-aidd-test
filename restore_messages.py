"""Скрипт для восстановления удаленных сообщений (soft delete)."""
import sqlite3

conn = sqlite3.connect('data/messages.db')
cursor = conn.cursor()

# Получаем количество удаленных записей
cursor.execute('SELECT COUNT(*) FROM messages WHERE is_deleted = 1')
deleted_count = cursor.fetchone()[0]

print(f"\n📊 Найдено удаленных записей: {deleted_count}")

if deleted_count > 0:
    # Восстанавливаем все удаленные записи
    cursor.execute('UPDATE messages SET is_deleted = 0 WHERE is_deleted = 1')
    conn.commit()

    print(f"✅ Восстановлено записей: {cursor.rowcount}")

    # Проверяем результат
    cursor.execute('SELECT COUNT(*) FROM messages WHERE is_deleted = 0')
    active_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM messages')
    total_count = cursor.fetchone()[0]

    print(f"\n📈 Итоговая статистика:")
    print(f"  Всего записей: {total_count}")
    print(f"  Активных: {active_count}")
    print(f"  Удаленных: {total_count - active_count}")
else:
    print("ℹ️  Нет удаленных записей для восстановления")

conn.close()
print()


