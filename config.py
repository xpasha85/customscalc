from datetime import datetime
from currency_converter import convert_currency


def calculate_customs_clearance(car_price_rub, engine_volume, car_age, engine_power, is_electric, is_legal_entity,
                                is_commercial=False, fuel_type=1, exchange_rate=100):
    """
    Расчет стоимости растаможки автомобиля в России.

    :param car_price_rub: Стоимость автомобиля в рублях
    :param engine_volume: Объем двигателя в см³
    :param car_age: Возраст автомобиля в годах
    :param engine_power: Мощность двигателя в л.с.
    :param is_electric: Является ли автомобиль электромобилем (True/False)
    :param is_legal_entity: Является ли владелец юридическим лицом (True/False)
    :param is_commercial: Ввозится ли авто для перепродажи (True/False)
    :param fuel_type: Тип топлива (1 - Бензин, 2 - Дизель, 3 - Гибрид)
    :return: Словарь с расчетами всех сборов и итоговой стоимостью
    """
    # exchange_rate = 92.0029  # Примерный курс евро к рублю (уточните актуальный курс)
    # car_price_rub = car_price_eur * exchange_rate

    # 1. Сбор за таможенное оформление
    if car_price_rub <= 200_000:
        customs_clearance_fee = 1067
    elif car_price_rub <= 450_000:
        customs_clearance_fee = 2134
    elif car_price_rub <= 1_200_000:
        customs_clearance_fee = 4269
    elif car_price_rub <= 2_700_000:
        customs_clearance_fee = 11746
    elif car_price_rub <= 4_200_000:
        customs_clearance_fee = 16524
    elif car_price_rub <= 5_500_000:
        customs_clearance_fee = 21344
    elif car_price_rub <= 7_000_000:
        customs_clearance_fee = 27540
    else:
        customs_clearance_fee = 30000

    # 2. Таможенная пошлина
    if is_electric:
        # Для электромобилей фиксированная ставка 15%
        customs_duty = car_price_rub * 0.15
    else:
        if not is_legal_entity:
            # Для физических лиц
            if car_age < 3:
                # Для автомобилей младше 3 лет
                car_price_eur = convert_currency(car_price_rub, 'RUB', 'EUR')
                if car_price_eur <= 8500:
                    rate = 0.54
                    min_per_cm3 = 2.5
                elif car_price_eur <= 16700:
                    rate = 0.48
                    min_per_cm3 = 3.5
                elif car_price_eur <= 42300:
                    rate = 0.48
                    min_per_cm3 = 5.5
                elif car_price_eur <= 84500:
                    rate = 0.48
                    min_per_cm3 = 7.5
                elif car_price_eur <= 169000:
                    rate = 0.48
                    min_per_cm3 = 15
                else:
                    rate = 0.48
                    min_per_cm3 = 20
                customs_duty = max(car_price_rub * rate, min_per_cm3 * engine_volume * exchange_rate)
            elif 3 <= car_age <= 5:
                # Для автомобилей от 3х до 5ти лет
                if engine_volume <= 1000:
                    duty_per_cm3 = 1.5
                elif engine_volume <= 1500:
                    duty_per_cm3 = 1.7
                elif engine_volume <= 1800:
                    duty_per_cm3 = 2.5
                elif engine_volume <= 2300:
                    duty_per_cm3 = 2.7
                elif engine_volume <= 3000:
                    duty_per_cm3 = 3
                else:
                    duty_per_cm3 = 3.6
                customs_duty = duty_per_cm3 * engine_volume * exchange_rate
            else:
                # Для автомобилей старше 5ти лет
                if engine_volume <= 1000:
                    duty_per_cm3 = 3
                elif engine_volume <= 1500:
                    duty_per_cm3 = 3.2
                elif engine_volume <= 1800:
                    duty_per_cm3 = 3.5
                elif engine_volume <= 2300:
                    duty_per_cm3 = 4.8
                elif engine_volume <= 3000:
                    duty_per_cm3 = 5
                else:
                    duty_per_cm3 = 7.5
                customs_duty = duty_per_cm3 * engine_volume * exchange_rate
        else:
            # для юридических лиц
            if fuel_type in [1, 3]:
                # бензиновый двигатель или гибрид
                if car_age < 3:
                    # Для автомобилей младше 3 лет
                    if engine_volume <= 2800:
                        rate = 0.15
                    else:
                        rate = 0.125
                    customs_duty = car_price_rub * rate
                elif 3 <= car_age <= 7:
                    # для автомобилей от 3 до 7 лет
                    if engine_volume <= 1000:
                        rate = 0.2
                        min_per_cm3 = 0.36
                    elif 1000 < engine_volume <= 1500:
                        rate = 0.2
                        min_per_cm3 = 0.4
                    elif 1500 < engine_volume <= 1800:
                        rate = 0.2
                        min_per_cm3 = 0.36
                    elif 1800 < engine_volume <= 3000:
                        rate = 0.2
                        min_per_cm3 = 0.44
                    else:
                        rate = 0.2
                        min_per_cm3 = 0.8
                    customs_duty = max(car_price_rub * rate, min_per_cm3 * engine_volume * exchange_rate)
                else:
                    # Для автомобилей старше 7ми лет
                    if engine_volume <= 1000:
                        min_per_cm3 = 1.4
                    elif engine_volume <= 1500:
                        min_per_cm3 = 1.5
                    elif engine_volume <= 1800:
                        min_per_cm3 = 1.6
                    elif engine_volume <= 3000:
                        min_per_cm3 = 2.2
                    else:
                        min_per_cm3 = 3.2
                    customs_duty = min_per_cm3 * engine_volume * exchange_rate
            if fuel_type == 2:
                # Дизельный двигатель
                if car_age < 3:
                    # Для автомобилей младше 3 лет
                    customs_duty = car_price_rub * 0.15
                elif 3 <= car_age <= 7:
                    # для автомобилей от 3 до 7 лет
                    if engine_volume <= 1500:
                        rate = 0.2
                        min_per_cm3 = 0.32
                    elif engine_volume <= 2500:
                        rate = 0.2
                        min_per_cm3 = 0.4
                    else:
                        rate = 0.2
                        min_per_cm3 = 0.8
                    customs_duty = max(car_price_rub * rate, min_per_cm3 * engine_volume * exchange_rate)
                else:
                    # Для автомобилей старше 7ми лет
                    if engine_volume <= 1500:
                        min_per_cm3 = 1.5
                    elif engine_volume <= 2500:
                        min_per_cm3 = 2.2
                    else:
                        min_per_cm3 = 3.2
                    customs_duty = min_per_cm3 * engine_volume * exchange_rate

    # 3. Утилизационный сбор
    if is_legal_entity:
        base_rate = 150_000  # Для коммерческих автомобилей
    else:
        base_rate = 20_000  # Для легковых автомобилей некоммерческого использования

    if is_commercial or is_legal_entity:
        if is_electric:
            if car_age < 3:
                coefficient = 33.37
            else:
                coefficient = 58.7
        else:
            if car_age < 3:
                if engine_volume <= 1000:
                    coefficient = 9.01
                elif engine_volume <= 2000:
                    coefficient = 33.37
                elif engine_volume <= 3000:
                    coefficient = 93.77
                elif engine_volume <= 3500:
                    coefficient = 107.67
                else:
                    coefficient = 137.11
            else:
                if engine_volume <= 1000:
                    coefficient = 23
                elif engine_volume <= 2000:
                    coefficient = 58.7
                elif engine_volume <= 3000:
                    coefficient = 141.97
                elif engine_volume <= 3500:
                    coefficient = 165.84
                else:
                    coefficient = 180.24
    else:
        if is_electric:
            if car_age < 3:
                coefficient = 0.17
            else:
                coefficient = 0.26
        else:
            if car_age < 3:
                if engine_volume <= 3000:
                    coefficient = 0.17
                elif engine_volume <= 3500:
                    coefficient = 107.67
                else:
                    coefficient = 137.11
            else:
                if engine_volume <= 3000:
                    coefficient = 0.26
                elif engine_volume <= 3500:
                    coefficient = 165.84
                else:
                    coefficient = 180.24
    recycling_fee = base_rate * coefficient

    # 4. Акциз
    if is_legal_entity or is_electric:
        if engine_power <= 90:
            excise_tax = 0
        elif engine_power <= 150:
            excise_tax = 61 * engine_power
        elif engine_power <= 200:
            excise_tax = 583 * engine_power
        elif engine_power <= 300:
            excise_tax = 955 * engine_power
        elif engine_power <= 400:
            excise_tax = 1628 * engine_power
        elif engine_power <= 500:
            excise_tax = 1685 * engine_power
        else:
            excise_tax = 1740 * engine_power
    else:
        excise_tax = 0

    # 5. НДС (для юридических лиц или физических лиц, если электромобиль)
    if is_legal_entity or is_electric:
        vat = (car_price_rub + customs_duty + excise_tax) * 0.20
    else:
        vat = 0

    # Итоговая стоимость растаможки
    total_cost = customs_clearance_fee + customs_duty + recycling_fee + excise_tax + vat

    return {
        "Таможенное оформление": customs_clearance_fee,
        "Таможенная пошлина": customs_duty,
        "Утилизационный сбор": recycling_fee,
        "Акциз": excise_tax,
        "НДС": vat,
        "Итоговая стоимость растаможки": total_cost
    }


def get_car_age(release_ym):
    """
    Определяет возраст автомобиля и его статус 'проходное'

    Args:
        release_ym (str): Дата выпуска в формате "YYYYMM"

    Returns:
        dict: {
            'year': 2, 3, 4, 5 или 6
            'is_eligible': bool (True только для 3-5 лет)
        }
    """
    try:
        # Парсим входные данные
        release_year = int(release_ym[:4])
        release_month = int(release_ym[4:6])

        if not 1 <= release_month <= 12:
            return {'error': 'Неверный месяц (должен быть 01-12)'}

        today = datetime.now()
        release_date = datetime(release_year, release_month, 1)

        # Вычисляем точное количество месяцев
        months_passed = (today.year - release_date.year) * 12 + (today.month - release_date.month)

        # Корректируем если текущий день меньше 1 числа
        if today.day < 1:
            months_passed -= 1

        # Определяем выходные значения
        if months_passed < 36:  # Менее 3 лет
            return {'year': 2, 'is_eligible': False}
        elif 36 <= months_passed <= 60:  # 3-5 лет
            full_years = months_passed // 12
            return {'year': full_years, 'is_eligible': True}
        else:  # Более 5 лет
            return {'year': 6, 'is_eligible': False}

    except (ValueError, IndexError):
        return {'error': 'Неверный формат даты. Используйте "YYYYMM"'}


# Пример использования
# car_price_eur = 20000  # Стоимость автомобиля в евро
# engine_volume = 1200  # Объем двигателя в см³
# car_age = 4  # Возраст автомобиля в годах
# engine_power = 190  # Мощность двигателя в л.с.
# is_electric = True  # Не электромобиль
# is_legal_entity = False  # Физическое лицо
# is_commercial = True  # Для перепродажи
#
#
# result = calculate_customs_clearance(car_price_eur, engine_volume, car_age, engine_power, is_electric,
#                                      is_legal_entity, is_commercial, fuel_type=2)
# for key, value in result.items():
#     formatted_value = "{:,.0f}".format(value).replace(",", " ")
#     print(f"{key}: {formatted_value} руб.")