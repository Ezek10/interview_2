import json
import xml.etree.ElementTree as ET

def xml_to_json():

    # Cargar el archivo XML
    tree = ET.parse("task_2/seatmap.xml")
    root = tree.getroot()
    base = ".//{http://www.opentravel.org/OTA/2003/05/common/}"
    # Buscar los elementos relevantes para los asientos
    cabin_classes = root.findall(base + "CabinClass")
    response = {}
    # Recorrer los elementos de CabinClass y extraer información de los asientos
    for cabin_class in cabin_classes:
        for row_info in cabin_class.findall(base + "RowInfo"):
            for seat_info in row_info.findall(base + "SeatInfo"):
                seat_summary = seat_info.find(base + "Summary")
                seat_available = seat_summary.get("AvailableInd")
                seat_number = seat_summary.get("SeatNumber")
                response[f"seat {seat_number}"] = {
                    "display_name": seat_number,
                    "product_details": {
                        "column": seat_number[-1],
                        "row": seat_number[0:-1]
                    },
                    "product_type": "seat",
                    "price_and_availability": {
                        "passanger_id": {
                            "available": seat_available,
                            "passenger_id": "passenger_id",
                        }
                    }
                }
                if seat_available == "true":
                    seat_service = seat_info.find(base + "Service")
                    seat_fee = seat_service.find(base + "Fee")
                    seat_fee_amount = int(seat_fee.get("Amount"))
                    seat_fee_currency_code = seat_fee.get("CurrencyCode")
                    seat_fee_decimal_places = int(seat_fee.get("DecimalPlaces"))
                    seat_tax = seat_fee.find(base + "Taxes")
                    seat_tax_amount = int(seat_tax.get("Amount"))
                    seat_tax_currency_code = seat_tax.get("CurrencyCode")
                    response[f"seat {seat_number}"]["price_and_availability"]["commission"] = {
                        "total": {
                            "amount": seat_tax_amount,
                            "currency": seat_tax_currency_code,
                            "decimal_places": seat_fee_decimal_places,
                        }
                    }
                    response[f"seat {seat_number}"]["price_and_availability"]["price"] = {
                        "base": {
                            "amount": seat_fee_amount,
                            "currency": seat_fee_currency_code,
                            "decimal_places": seat_fee_decimal_places
                        },
                        "total": {
                            "amount": seat_fee_amount + seat_tax_amount,
                            "currency": seat_fee_currency_code,
                            "decimal_places": seat_fee_decimal_places
                        }
                    }
    response = {
        "results": {
            "products": {
                "seat": response
            }
        }
    }
    return response


data_json = xml_to_json()
with open('task_2/seatmap.json', 'w') as f:
    json.dump(data_json, f, indent=4)
