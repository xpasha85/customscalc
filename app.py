import json
from datetime import datetime
from currency_converter import convert_currency
import streamlit as st
import requests
from config import calculate_customs_clearance, get_car_age

st.set_page_config(page_title='Таможенный калькулятор', page_icon='🚗')
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        <script>
        setInterval(function() {
            fetch(window.location.href);
        }, 5 * 60 * 1000);
        </script>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.header('Калькулятор растаможки авто')

FUEL_TYPES = {
    '001': 'Бензин',
    '002': 'Дизель',
    '003': 'Сжиженный газ',
    '005': 'Бензин + сжиженный газ',
    '006': 'Бензин + Электричество',
    '007': 'Дизель + Электричество',
    '009': 'Электричество',
}
FUTURE_OWNER = [
    "Физическое лицо",
    "Юридическое лицо"
]
CURRENCIES = {
    'Евро': 'EUR',
    'Доллар': 'USD',
    'Корейская вона': 'KRW',
    'Российский рубль': 'RUB'
}
MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
          "Декабрь"]
main_url = 'http://45.90.216.240:3051/'
url2 = main_url + 'catalog.json'
icon_error = ':material/error_outline:'
is_calc_encar = False


def eur_to_rub():
    return convert_currency(1, 'EUR', 'RUB')


@st.cache_data(ttl=84600)
def load_json(url) -> json:
    dt = requests.get(url)
    return dt.json()


def get_car_id(url):
    if len(url) == 8 and url.isdigit():
        return {
            'code': 'ok',
            'car_id': url
        }
    if (8 < len(url) or len(url) < 8) and url.isdigit():
        return {
            'code': 'error',
            'message': f'CAR_ID должен содержать 8 символов. Сейчас их - {len(url)}'
        }
    k = url.split('detail/')
    if len(k) != 2:
        return {
            'code': 'error',
            'message': 'Неверный формат ссылки (отсутствует "detail/")'
        }
    j = k[1]
    j = j[0:8]
    if len(j) == 8:
        return {
            'code': 'ok',
            'car_id': j
        }
    return {
        'code': 'error',
        'message': f'Неизвестная ошибка. Отправьте разработчику:\n'
                   f'{url}'
    }


def get_car_year(year: int):
    year_now = datetime.now().year
    return year_now - year


is_legal_entity, is_commercial = False, False

if st.checkbox('Хочу посчитать машину с Encar'):
    is_calc_encar = True
    with st.container():
        input_link = st.text_input('Вставьте ссылку на Encar или id авто')
        if st.button('Найти'):
            car_id = ''
            id_car_json = get_car_id(input_link)
            if id_car_json['code'] == 'error':
                st.error(id_car_json['message'], icon=icon_error)
                st.stop()
            else:
                car_id = id_car_json['car_id']
            if not car_id:
                st.error('CAR_ID не может быть пустым', icon=icon_error)
                st.stop()
            data = load_json(f'http://45.90.216.240:3051/catalog?car={car_id}')
            if data.get('code') == 404:
                st.error('Автомобиль с таким ID не найден!', icon=icon_error)
                st.stop()
            # ---------- print json -------------
            # st.write(data)
            # -------------------------------
            group_car_data = data['vehicle']['category']
            car_manufactory = group_car_data['manufacturerEnglishName']
            car_model = group_car_data['modelGroupEnglishName']
            car_name = group_car_data['gradeEnglishName']
            car_yearmonth = group_car_data['yearMonth']
            car_year = car_yearmonth[0:4]
            car_month = int(car_yearmonth[4:])
            car_month_word = MONTHS[car_month - 1]
            car_price = int(data['vehicle']['advertisement']['price']) * 10000
            car_displacement = data['vehicle']['spec']['displacement']
            car_type = data['vehicle']['spec']["fuelCd"]
            car_photos_path = data['vehicle']['photos'][0]['path']
            car_photo = 'https://ci.encar.com/carpicture' + car_photos_path[0:-7] + '001.jpg' + \
                        '?impolicy=heightRate&rh=696&cw=1160&ch=696&cg=Center '
            if car_type == '009':
                color = 'green'
            else:
                color = 'orange'
            fuel_type = FUEL_TYPES[car_type]
            st.markdown('#### Найден автомобиль:')
            col1, col2, col3 = st.columns(3)
            car_price_in_rub = convert_currency(car_price, 'KRW', 'RUB')
            with col1:
                st.write(f"Марка:&nbsp;&nbsp;&nbsp;:orange[{car_manufactory}]")
                st.write(f"Модель:&nbsp;&nbsp;&nbsp;:orange[{car_model} {car_name}]")
                st.write(f"Тип двигателя:&nbsp;&nbsp;&nbsp;:orange[{fuel_type}]")
            with col2:
                st.write(f"Объем / Л.С.:&nbsp;&nbsp;&nbsp;:{color}[{car_displacement}]")
                st.write(f"Дата выпуска:&nbsp;&nbsp;&nbsp;:orange[{car_month_word} {car_year}]")
                formatted_number = f"₩ {car_price:,}"
                formatted_car_in_rub = "{:,.0f}".format(car_price_in_rub).replace(",", " ")
                st.write(
                    f"Цена:&nbsp;&nbsp;&nbsp;:orange[{formatted_number}]&nbsp;|&nbsp;:gray[{formatted_car_in_rub} ₽]")
            with col3:
                st.image(car_photo, width=300)
            # st.write(car_photo)
            # --------------- Расчет авто ----------------------------
            st.markdown('#### Расчет таможенных платежей:')
            engine_volume = car_displacement
            # ----- Электричка ---------
            if car_type == '009':
                is_electric = True
                engine_power = car_displacement
            else:
                is_electric = False
                engine_power = 170
                if car_type == '002':
                    fuel_type = 2
            data = get_car_age(car_yearmonth)
            car_age = data['year']
            is_eligible = data['is_eligible']
            txt = ':green[Автомобиль проходной]' if is_eligible else ':red[Автомобиль непроходной]'
            # st.write(car_age, type(car_age))
            st.write(txt)
            calc_is_legal = calculate_customs_clearance(car_price_in_rub, engine_volume, car_age, engine_power,
                                                        is_electric,
                                                        is_legal_entity, is_commercial, fuel_type, eur_to_rub())
            calc_not_legal = calculate_customs_clearance(car_price_in_rub, engine_volume, car_age, engine_power,
                                                         is_electric,
                                                         is_legal_entity, True, fuel_type, eur_to_rub())
            # formatted_value = "{:,.0f}".format(value).replace(",", " ")
            # st.write(f"{key}&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[ {formatted_value} руб.]")
            customs_clearance = calc_is_legal['Таможенное оформление']
            custom_duty = calc_is_legal['Таможенная пошлина']
            util1 = calc_is_legal['Утилизационный сбор']
            util2 = calc_not_legal['Утилизационный сбор']
            tax = calc_is_legal['Акциз']
            vat = calc_is_legal['НДС']
            summary1 = calc_is_legal['Итоговая стоимость растаможки']
            summary2 = calc_not_legal['Итоговая стоимость растаможки']
            formatted_value = "{:,.0f}".format(customs_clearance).replace(",", " ")
            st.write(f'Таможенное оформление&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value} руб.]')
            formatted_value = "{:,.0f}".format(custom_duty).replace(",", " ")
            st.write(f'Таможенная пошлина&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value} руб.]')
            formatted_value = "{:,.0f}".format(util1).replace(",", " ")
            formatted_value2 = "{:,.0f}".format(util2).replace(",", " ")
            st.write(
                f'Утилизационный сбор&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value} руб.] / :red[{formatted_value2} руб.]')
            if tax != 0:
                formatted_value = "{:,.0f}".format(tax).replace(",", " ")
                st.write(f'Акциз&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value} руб.]')
            if vat != 0:
                formatted_value = "{:,.0f}".format(vat).replace(",", " ")
                st.write(f'НДС&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value} руб.]')
            formatted_itog1 = "{:,.0f}".format(summary1).replace(",", " ")
            formatted_itog2 = "{:,.0f}".format(summary2).replace(",", " ")
            st.write(f'Итоговая стоимость растаможки&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green['
                     f'{formatted_itog1} руб.] / :red[{formatted_itog2} руб.]')
            frm_it1 = "{:,.0f}".format(summary1 + car_price_in_rub).replace(",", " ")
            frm_it2 = "{:,.0f}".format(summary2 + car_price_in_rub).replace(",", " ")
            st.write(f'Итого (для себя):&nbsp;&nbsp;&nbsp;:orange[{frm_it1}] :gray[₽ &nbsp;&nbsp;&nbsp;&nbsp;'
                     f'{formatted_car_in_rub}₽ + {formatted_itog1}₽]')
            st.write(f'Итого (перепродажа):&nbsp;&nbsp;&nbsp;:orange[{frm_it2}] :gray[₽ &nbsp;&nbsp;&nbsp;&nbsp;'
                     f'{formatted_car_in_rub}₽ + {formatted_itog2}₽]')

            st.divider()
else:
    is_calc_encar = False

if not is_calc_encar:
    with st.container():
        owner = st.selectbox(label='Автомобиль ввозит',
                             options=FUTURE_OWNER, index=0,
                             help='Критерии личного использования:\n- машина остается в собственности '
                                  'физлица, который её привёз не менее года;\n- физическое лицо ввозит '
                                  'не более одной машины в год;\n- объем двигателя автомобиля не более '
                                  '3 л.\n\nЕсли автомобиль не попадает под критерии личного использования, '
                                  'то применяются повышенные коэффициенты утилизационного сбора')
        # if owner == FUTURE_OWNER[1]:
        #     is_commercial = True
        if owner == FUTURE_OWNER[1]:
            is_legal_entity = True
        # st.write(owner)
        car_year = st.selectbox('Год выпуска авто', [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], 5)
        car_age = get_car_year(car_year)
        # ['Бензиновый', 'Дизельный', 'Гибридный', 'Электрический']
        engine_type = st.selectbox('Тип двигателя', ['Бензиновый', 'Дизельный', 'Гибридный', 'Электрический'], 1)
        # st.write(engine_type)
        if engine_type in ['Бензиновый', 'Гибридный']:
            fuel_type = 1
        else:
            fuel_type = 2
        is_electric = True if engine_type == 'Электрический' else False
        # st.write('mortgage')
        engine_power = st.number_input('Мощность двигателя (ЛС)', 50, 1000, 170, disabled=not is_electric)
        engine_volume = st.number_input('Объем двигателя (см³)', 500, 6000, 2199, disabled=is_electric)
        col1, col2, col3 = st.columns([2, 1, 1], vertical_alignment='bottom')
        with col1:
            car_price = st.number_input('Стоимость автомобиля', 100, 100_000_000, 20_000)
        with col2:
            price_curr = st.selectbox('Валюта', CURRENCIES.keys(), 0)
        with col3:
            curr_to = 'RUB'
            curr_from = CURRENCIES[price_curr]
            # car_price_in_rub = converter.convert(car_price, curr_from, curr_to, 'CBR')
            car_price_in_rub = convert_currency(car_price, curr_from, curr_to)
            formatted_car_price_in_rub = "{:,.0f}".format(car_price_in_rub).replace(",", ".")
            st.write(f"&nbsp;&nbsp;:gray[= {formatted_car_price_in_rub} ₽]")

        if st.button('Рассчитать'):
            st.write(f':gray[1 EUR - {eur_to_rub()} ₽]')
            if owner == FUTURE_OWNER[1]:
                data = calculate_customs_clearance(car_price_in_rub, engine_volume, car_age, engine_power, is_electric,
                                                   is_legal_entity, is_commercial, fuel_type, eur_to_rub())
                for key, value in data.items():
                    if value == 0:
                        continue
                    formatted_value = "{:,.0f}".format(value).replace(",", " ")
                    st.write(f"{key}&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[ {formatted_value} руб.]")
            else:
                data1 = calculate_customs_clearance(car_price_in_rub, engine_volume, car_age, engine_power, is_electric,
                                                    False, False, fuel_type, eur_to_rub())
                data2 = calculate_customs_clearance(car_price_in_rub, engine_volume, car_age, engine_power, is_electric,
                                                    False, True, fuel_type, eur_to_rub())
                s = data1["Таможенное оформление"]
                formatted_value = "{:,.0f}".format(s).replace(",", " ")
                st.write(f"Таможенное оформление&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[ {formatted_value} руб.]")
                s = data1["Таможенная пошлина"]
                formatted_value = "{:,.0f}".format(s).replace(",", " ")
                st.write(f"Таможенная пошлина&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[ {formatted_value} руб.]")
                s1 = data1["Утилизационный сбор"]
                s2 = data2["Утилизационный сбор"]
                formatted_value1 = "{:,.0f}".format(s1).replace(",", " ")
                formatted_value2 = "{:,.0f}".format(s2).replace(",", " ")
                st.write(f'Утилизационный сбор&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value1} руб.] / '
                         f':red[{formatted_value2} руб.]')
                tax = data1["Акциз"]
                if tax != 0:
                    formatted_value = "{:,.0f}".format(tax).replace(",", " ")
                    st.write(f'Акциз&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value} руб.]')
                vat = data1["НДС"]
                if vat != 0:
                    formatted_value = "{:,.0f}".format(vat).replace(",", " ")
                    st.write(f'НДС&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green[{formatted_value} руб.]')
                s1 = data1["Итоговая стоимость растаможки"]
                s2 = data2["Итоговая стоимость растаможки"]
                formatted_value1 = "{:,.0f}".format(s1).replace(",", " ")
                formatted_value2 = "{:,.0f}".format(s2).replace(",", " ")
                st.write(f'Итоговая стоимость растаможки&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;:green['
                         f'{formatted_value1} руб.]  / :red[{formatted_value2} руб.]')
