import requests
from datetime import datetime, timedelta
import json
import os

# Настройки кэширования
CACHE_FILE = "currency_cache.json"
CACHE_DURATION = timedelta(hours=6)


def get_cached_rates():
    """Проверяет наличие актуального кэша"""
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

        cache_time = datetime.fromisoformat(cache["timestamp"])
        if datetime.now() - cache_time < CACHE_DURATION:
            return cache["data"]
    except Exception as e:
        print(f"Ошибка чтения кэша: {e}")

    return None


def save_to_cache(data):
    """Сохраняет данные в кэш"""
    try:
        cache = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения кэша: {e}")


def get_currency_rates():
    """Получает курсы валют с использованием кэширования"""
    # Сначала проверяем кэш
    cached_data = get_cached_rates()
    if cached_data is not None:
        return cached_data

    # Если нет актуального кэша, загружаем новые данные
    try:
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        valutes = data["Valute"]

        # Сохраняем в кэш
        save_to_cache(valutes)
        return valutes
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении курсов валют: {e}")
        return None


def convert_currency(amount, from_currency, to_currency):
    """Конвертирует сумму из одной валюты в другую"""
    rates = get_currency_rates()

    if rates is None:
        print("Не удалось получить курсы валют. Попробуйте позже.")
        return None

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    # Конвертация через рубли
    try:
        # 1. Конвертируем исходную валюту в рубли
        if from_currency == "RUB":
            rub_amount = amount
        else:
            from_rate = rates[from_currency]["Value"]
            from_nominal = rates[from_currency]["Nominal"]
            rub_amount = amount * (from_rate / from_nominal)

        # 2. Конвертируем рубли в целевую валюту
        if to_currency == "RUB":
            return rub_amount
        else:
            to_rate = rates[to_currency]["Value"]
            to_nominal = rates[to_currency]["Nominal"]
            return rub_amount / (to_rate / to_nominal)

    except KeyError as e:
        print(f"Ошибка: валюта {e} не найдена в списке доступных")
        return None


def print_available_currencies(rates):
    """Печатает список доступных валют"""
    print("\nДоступные валюты:")
    for code, currency in rates.items():
        print(f"{code}: {currency['Name']} ({currency['Nominal']} {code} = {currency['Value']} RUB)")


def main():
    print("Конвертер валют по курсу ЦБ РФ с кэшированием")

    # Предварительная загрузка курсов
    rates = get_currency_rates()
    if rates is None:
        print("Не удалось загрузить курсы валют. Проверьте подключение к интернету.")
        return

    print_available_currencies(rates)

    while True:
        try:
            print("\nВведите данные для конвертации:")
            amount = float(input("Сумма: "))
            from_curr = input("Из валюты (код из 3 букв, например USD): ").strip().upper()
            to_curr = input("В валюту (код из 3 букв, например EUR): ").strip().upper()

            result = convert_currency(amount, from_curr, to_curr)

            if result is not None:
                print(f"\nРезультат: {amount:.2f} {from_curr} = {result:.2f} {to_curr}")

            if input("\nПродолжить? (y/n): ").lower() != 'y':
                break

        except ValueError:
            print("Ошибка: введите корректную сумму")
        except KeyboardInterrupt:
            print("\nВыход из программы")
            break


if __name__ == "__main__":
    main()