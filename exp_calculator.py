from datetime import datetime, timedelta

exp_table: list = [
    0, 2, 6, 18, 37, 67, 110, 170, 246,
    344, 464, 610, 782, 986, 1221, 1491, 1798, 2146, 2534,
    2968, 3448, 3978, 4558, 5194, 5885, 6635, 7446, 8322, 9262,
    10272, 11352, 12506, 13734, 15042, 16429, 17899, 19454, 21098, 22830,
    24656, 26576, 28594, 30710, 32930, 35253, 37683, 40222, 42874, 45638,
    48520, 51520, 54642, 57886, 61258, 64757, 68387, 72150, 76050, 80086,
    84264, 106110, 113412, 121149, 129352, 138044, 147256, 157019, 167366, 178334,
    189958, 202282, 215348, 229205, 243901, 259495, 276041, 293606, 312258, 332071,
    353126, 375511, 399318, 424655, 451631, 480370, 511007, 543686, 578571, 615838,
    655680, 698312, 743971, 792917, 845443, 901868, 962554, 1027899, 1098353, 1174420,
    1256663, 1345723, 1442322, 1547281, 1661531, 1786143, 1922340, 2071533, 2235352, 2415689,
    2614754, 2835137, 3079892, 3352633, 3657676, 4000195, 4386445, 4824041, 5322323, 5892866,
    6550125, 12326614, 15496114, 20025638, 26821885, 37698249, 56734876, 68097265, 68290815, 68487425,
    68687119, 68889921, 69095855, 69304945, 69517215, 69732689, 69951391, 70173345, 70398575, 70627105,
    70858959, 71244161, 100000000, 150000000, 200000000, 250000000, 300000000, 350000000, 400000000, 450000000,
    500000000
]

def get_exp_buff_formula():
    return "[(경험치) * (파티 보너스) * (경구 or 케이크) + (변신템) + (나뭇가지)] * (영메)"

def calculate_exp_buff(
    exp: int,
    transform_item: int = 0,
    event: int = 0,
    item_buff: int = 1, # cake, 2x exp orb, etc
    party_count: int = 1,
    newbie_item: bool=False,
    hero_echo: bool=False,
):
    party_buff = [1, 1, 1.1, 1.15, 1.20, 1.25]
    total_exp = 0

    if party_count < 1: party_count = 1
    if party_count > 5: party_count = 5

    # apply party buff
    exp = exp * party_buff[party_count]

    # calculate additive buff - transformation + newbie item
    # i.e. if transform_item == 15, exp *= 1.15
    if transform_item > 0: total_exp += exp * (transform_item / 100)

    if newbie_item: total_exp += exp

    # calculate multiplicative buff
    total_exp += exp * max(event, 1) * max(item_buff, 1)

    if hero_echo: total_exp *= 2

    return total_exp

def _remaining_exp(current_lvl: int, current_per: float, desired_lvl: int):
    current_lvl = min(current_lvl, 149)
    desired_lvl = min(desired_lvl, 149)
    if current_lvl >= desired_lvl:
        return 0
    remaining_exp = int(exp_table[current_lvl] * ((100 - current_per) / 100))
    for i in range((current_lvl+1), desired_lvl):
        remaining_exp += exp_table[i]
    return remaining_exp

def calculate_time_for_lvl(current_lvl: int, current_per: float, desired_lvl: int, exp_per_hour: int):
    if exp_per_hour == 0:
        return 0
    current_lvl = min(current_lvl, 149)
    desired_lvl = min(desired_lvl, 149)
    exp_per_min: float = exp_per_hour / 60
    
    remaining_exp = _remaining_exp(current_lvl, current_per, desired_lvl)
    
    required_time_in_min: float = remaining_exp / exp_per_min
    return required_time_in_min

def _format_time(total_minutes: float):
    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    minutes = total_minutes % 60

    parts = []
    if days > 0:
        parts.append(f"{int(days)} 일")
    if hours > 0:
        parts.append(f"{int(hours)} 시간")
    if minutes > 0 or not parts:
        parts.append(f"{int(minutes)} 분")

    return " ".join(parts)


def format_result(current_lvl: int, current_per: float, desired_lvl: int, time_in_min: float, total_exp: float):
    remaining_exp = _remaining_exp(current_lvl, current_per, desired_lvl)

    # Get current time
    now = datetime.now()
    new_time = now + timedelta(minutes=time_in_min)
    
    return f"""
        총 경험치 공식:
        {get_exp_buff_formula()}
        
        시간당 경험치: {int(total_exp):,}

        필요 경험치: {remaining_exp:,}
        필요 시간 : {_format_time(time_in_min)}

        레벨 달성 날짜: {new_time.strftime("%Y-%m-%d %H:%M")}
    """