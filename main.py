# Вариант 21
import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных
transactions = pd.read_csv('data/transactions.csv', sep=',', nrows=1000000)
gender_train = pd.read_csv('data/gender_train.csv', sep=',')
tr_mcc_codes = pd.read_csv('data/tr_mcc_codes.csv', sep=';')
tr_types = pd.read_csv('data/tr_types.csv', sep=';')

# Соединение таблиц
# Left join с gender_train
merged = pd.merge(transactions,
                  gender_train,
                  on='customer_id',
                  how='left')

# Inner join с MCC tr_mcc_codes и tr_types
merged = pd.merge(merged,
                  tr_mcc_codes,
                  on='mcc_code',
                  how='inner')

merged = pd.merge(merged,
                  tr_types,
                  on='tr_type',
                  how='inner')

print('Количество строк после соединения датафреймов: ', len(merged)) # 999584

# Извлечение относительного дня из tr_datetime
merged['tr_day'] = merged['tr_datetime'].str.split(' ').str[0]
# Группировка данных по столбцу tr_day и подсчет уникальных mcc-кодов
mcc_counts = merged.groupby('tr_day')['mcc_code'].nunique()
# Фильтр mcc_counts по дням, где количество уникальных MCC-кодов > 70
active_days = mcc_counts[mcc_counts > 70].index
# Фильтр датафрейма, оставляя только строки, где значение tr_day есть в списке active_days
filtered_merged = merged[merged['tr_day'].isin(active_days)]

# Группировка по mcc-коду и полу
gender_mcc_stats = filtered_merged.groupby(['mcc_code', 'gender']).agg(
    transaction_count=('amount', 'count'),  # Количество транзакций
    mean_amount=('amount', 'mean'),         # Средняя сумма
    median_amount=('amount', 'median')      # Медианная сумма
).reset_index()

# Сортировка по количеству транзакций
gender_mcc_stats = gender_mcc_stats.sort_values(
    by=['mcc_code', 'transaction_count'],
    ascending=[True, False]
)

print(gender_mcc_stats.head(10))

# Построение столбчатой диаграммы
gender0 = gender_mcc_stats[gender_mcc_stats['gender'] == 0]
gender1 = gender_mcc_stats[gender_mcc_stats['gender'] == 1]

x = range(len(gender0['mcc_code']))

plt.figure(figsize=(10, 6))

plt.bar(
    x,
    gender0['transaction_count'],
    label='Gender 0'
)

plt.bar(
    [i + 0.35 for i in x],
    gender1['transaction_count'],
    label='Gender 1'
)

plt.xlabel('MCC-коды')
plt.ylabel('Количество транзакций')
plt.title('Количество транзакций по MCC-коду и полу')
plt.legend()

plt.show()
