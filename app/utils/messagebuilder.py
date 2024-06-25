from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

from app.vbb.enums import TransportMode
from app.vbb.func import minutes_left
from app.vbb.models import Cycle, GeoLocation, Helper, Journey, Leg, Location, Stop
from . import AddressResolved


class MessageBuilder:
    def __init__(self):

        pass

    @staticmethod
    async def user_addresses_list(user_id: int, f) -> str:
        """Used to list addresses in addresses menu"""
        from app.utils import address_util

        user_addresses = await f.db.get_user_addresses(user_id)
        address_lines = []

        for number, address in enumerate(user_addresses, start=1):
            address_line = f"{number}. {address.street_name} {address.house_number}, {address.plz} {address.city}"
            address_usage = await f.db.check_address_usage(user_id, address.id)
            address_usage_with_emoji = address_util.address_usage_add_emoji(address_usage)

            if address_usage_with_emoji is not None:
                address_line += f"\n - {address_usage_with_emoji}"

            address_lines.append(address_line)

        return "\n\n".join(address_lines) + "\n"

    @staticmethod
    def resolved_address_to_text(address_data: AddressResolved) -> str:
        """Used to show address data in addresses confirmation menu"""

        address_information_text = \
            """Street: %s
House number: %s
City: %s
Postal code: %s

📍 Pin: %s, %s""" % (
                address_data.street_name,
                address_data.house_number,
                address_data.city,
                address_data.plz,
                address_data.latitude,
                address_data.longitude
            )

        return address_information_text

    async def stop_to_text(self, stop: dict) -> str:
        # TODO: REFACTOR IT 🥺
        def get_stop_info(stop):
            return {
                "name": stop.get("name", "N/A"),
                "id": stop.get("id", "N/A"),
                "location": stop.get("location", {}),
                "products": stop.get("products", {}),
                "lines": stop.get("lines", []),
                "DHID": stop.get("stationDHID", "N/A"),
                "departures": stop.get("departures", []),
                "distance": stop.get("distance", 0)
            }

        def get_location_info(location):
            return location.get("latitude", "N/A"), location.get("longitude", "N/A")

        def get_transport_types(products):
            return ", ".join([product.capitalize() for product, available in products.items() if available]) or 'N/A'

        def format_departures(departures):
            departures_grouped = defaultdict(list)
            for departure in departures:
                planned_when = departure.get('plannedWhen')
                when = departure.get('when')
                departure_planned_time = datetime.fromisoformat(planned_when)
                departure_time = datetime.fromisoformat(when)
                delay = departure.get("delay", 0) or 0  # delay in seconds
                direction = departure.get('direction')
                line = departure.get('line')
                line_product = line["product"]
                line_emoji = TransportMode.get_emoji(line_product)
                line_name = line["name"]
                planned_minutes = minutes_left(departure_planned_time)
                current_minutes = minutes_left(departure_time)
                line_information = (direction, line_name, line_emoji)
                current_position = departure.get("currentTripPosition", {})
                departure_information = (
                    planned_minutes, current_minutes, delay // 60, current_position)
                departures_grouped[line_information].append(
                    departure_information
                )
            return departures_grouped

        async def generate_departures_text(departures_grouped):
            txt = "Departures:\n"
            departures_grouped = sort_dict_by_line(departures_grouped)
            for (direction, line_name, line_emoji), departure_info in departures_grouped.items():
                txt += f"{line_emoji}\t{line_name}\t --> <code>{direction}</code>\n"
                times_text = []
                for planned_minutes, current_minutes, delay, current_location in departure_info:
                    time_text = "<b>in "
                    if delay:
                        time_text += f"{abs(current_minutes)}' ({'+' if delay > 0 else ''}{delay})"  # noqa
                    else:
                        time_text += f"{planned_minutes}'"
                    time_text += "</b>"

                    if "latitude" in current_location and "longitude" in current_location:
                        latitude = current_location["latitude"]
                        longitude = current_location["longitude"]
                        time_text += await build_message_with_geo_deep_link(latitude, longitude, ' 🛰')

                    times_text.append(time_text)
                txt += ", ".join(times_text) + "\n\n"
            return txt

        def generate_line_text(lines):
            lines_data = {}

            for line in lines:
                product = line['product']
                name = line['name']

                if product not in lines_data:
                    lines_data[product] = []

                lines_data[product].append(name)

            text_output = ""
            for product, names in lines_data.items():
                text_output += "    - "
                text_output += "%s %s: %s\n" % (
                    product.capitalize(),
                    TransportMode.get_emoji(product),
                    ', '.join(names)
                )

            return text_output

        stop_info = get_stop_info(stop)
        stop_latitude, stop_longitude = get_location_info(
            stop_info["location"])
        transport_types = get_transport_types(stop_info["products"])
        transport_lines_text = generate_line_text(stop_info["lines"])

        txt = f"""
Stop: <b>{stop_info['name']}</b>
ID: <code>{stop_info['id']}</code> (DHID: <code>{stop_info['DHID']}</code>)

Transport types: {transport_types}

Transport lines:
{transport_lines_text}\n"""

        if stop_info['departures']:
            departures_grouped = format_departures(stop_info['departures'])
            txt += await generate_departures_text(departures_grouped)

        pin_text = f" 📍 Pin: {stop_latitude}, {stop_longitude}"

        txt += f"{await build_message_with_geo_deep_link(stop_latitude, stop_longitude, pin_text)}\n"
        txt += f" 🚶 Distance: {stop_info['distance']} meters"

        return txt

    async def build_journey_text(self, journey: Journey) -> str:
        journey_text = ""
        journey_text += self.build_journey_text_header(journey)

        journey_body = await self.build_journey_text_body(journey)
        journey_text += journey_body

        return journey_text

    def build_journey_text_header(self, journey: Journey) -> str:
        from aiogram import html
        first_leg = journey.legs[0]
        last_leg = journey.legs[-1]

        departure_datetime = first_leg.departure
        arrival_datetime = last_leg.arrival

        departure_address, _ = get_text_and_geo(first_leg.origin, first_leg.departure_platform)
        arrival_address, _ = get_text_and_geo(last_leg.destination, last_leg.departure_platform)

        journey_start = departure_datetime.strftime("%H:%M")
        journey_end = arrival_datetime.strftime("%H:%M")

        emoji_line = [f"{leg.transport_mode.value} {leg.line.name}"
                      if leg.line is not None
                      else leg.transport_mode.value
                      for leg in journey.legs]

        journey_time = Helper.time_difference(departure_datetime, arrival_datetime)
        emoji_line_text = '|'.join(emoji_line)

        text = f"""\
Summary:
{departure_address} -> {arrival_address}
<b>{journey_start} -> {journey_end}</b>

<b>{emoji_line_text}</b>

<b>🕒 {journey_time}</b> 🔃 {transfer_string(journey.count_transfers())}.
<b>{'⚠️ TRIP WAS CANCELLED!' if any(True if leg.cancelled else False for leg in journey.legs) else ''}</b>
{html.quote('>——————————————————<')}
\n"""

        return text

    async def build_journey_text_body(self, journey: Journey) -> str:
        text = ""
        for leg in journey.legs:
            origin_data_temp = get_text_and_geo(leg.origin, leg.departure_platform)
            if origin_data_temp is None:
                continue

            origin_text, origin_geo = origin_data_temp

            blockquote_text = get_blockquote_text(leg)

            text += f"""\
{Helper.get_time_string_from_datetime(leg.departure or leg.planned_departure)} <b>{await build_message_with_geo_deep_link(origin_geo.latitude, origin_geo.longitude, origin_text)}</b>

<blockquote>{blockquote_text}</blockquote>

"""  # noqa

        leg = journey.legs[-1]
        destination_text, destination_geo = get_text_and_geo(leg.destination, departure_platform=None)
        text += f"{Helper.get_time_string_from_datetime(leg.arrival)} <b>{await build_message_with_geo_deep_link(destination_geo.latitude, destination_geo.longitude, destination_text)}</b>"  # noqa

        return text


def get_blockquote_text(leg: Leg) -> str:
    if leg.walking:
        blockquote_text = f"{leg.transport_mode.value} Walk {leg.distance} m."
        return blockquote_text

    blockquote_text = f"""\
<b>{leg.transport_mode.value} {leg.line.name}</b> -> {leg.direction}"""
    alternatives = get_alternatives_minutes(leg.cycle)
    if alternatives is not None:
        blockquote_text += f"""\nAlternatives every {alternatives} min."""

    for remark in leg.remarks:
        if remark.type in ["warning", "status"]:
            blockquote_text += f"\n{remark.text}"

    return blockquote_text


def get_alternatives_minutes(cycle: Cycle) -> int | str:
    def safe_divide_by_60(value):
        return value // 60 if value is not None else None

    minimum, maximum = safe_divide_by_60(cycle.min), safe_divide_by_60(cycle.max)

    if minimum is None:
        return maximum if maximum is not None else None
    if maximum is None or minimum == maximum:
        return minimum

    return f"{minimum} - {maximum}"


def get_text_and_geo(entity: Union[Location, Stop],
                     departure_platform: Optional[str] = None
                     ) -> tuple[str, GeoLocation]:  # noqa
    if isinstance(entity, Location):
        text = entity.address
        geo = entity.geo
    elif isinstance(entity, Stop):
        text = entity.name
        if departure_platform is not None:
            text += f" (Pl. {departure_platform})"
        geo = entity.location.geo
    else:
        raise ValueError("Entity must be of type Location or Stop")
    return text, geo


async def get_geo_loc_deep_link(latitude, longitude):
    from aiogram.utils.deep_linking import create_start_link
    from app import bot

    latitude = str(latitude).replace('.', '-')
    longitude = str(longitude).replace('.', '-')

    payload = f"location_pin_{latitude}_{longitude}"

    link = await create_start_link(bot, payload)

    return link


async def build_message_with_geo_deep_link(latitude, longitude, msg):
    deep_link = await get_geo_loc_deep_link(latitude, longitude)

    return f'<a href="{deep_link}">{msg}</a>'


def sort_dict_by_line(d: dict):
    # Sort the dictionary by the second element of the keys
    sorted_dict = dict(sorted(d.items(), key=lambda item: item[0][1]))

    # Sort each list in the dictionary by the second element of the tuples
    for key in sorted_dict:
        temp = sorted_dict[key]
        temp = sorted(temp, key=lambda item: item[1])
        sorted_dict[key] = temp

    return sorted_dict


def transfer_string(transfer_count):
    # Determine if the word should be singular or plural
    if transfer_count % 10 == 1 and transfer_count % 100 != 11:
        return f"{transfer_count} transfer"
    else:
        return f"{transfer_count} transfers"
