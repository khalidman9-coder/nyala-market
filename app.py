from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from datetime import datetime


USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")


class NyalaHandler(BaseHTTPRequestHandler):

    def send_text(self, text, status=200):
        data = text.encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(data))
        )
        self.end_headers()

        self.wfile.write(data)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.end_headers()

    def do_GET(self):

        if self.path == "/prices.txt":

            file_path = "../prices.txt"

            if os.path.exists(file_path):

                with open(file_path, "rb") as file:
                    data = file.read()

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "text/plain; charset=utf-8"
                )
                self.send_header(
                    "Content-Length",
                    str(len(data))
                )
                self.end_headers()

                self.wfile.write(data)

            else:
                self.send_error(404, "Prices not found")

            return

        if self.path == "/admin.html":

            try:
                with open("admin.html", "rb") as file:
                    data = file.read()

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8"
                )
                self.send_header(
                    "Content-Length",
                    str(len(data))
                )
                self.end_headers()

                self.wfile.write(data)

            except FileNotFoundError:
                self.send_error(404, "Admin page not found")

            return

        try:

            with open("index.html", "rb") as file:
                data = file.read()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(data))
            )
            self.end_headers()

            self.wfile.write(data)

        except FileNotFoundError:

            self.send_error(404, "Page not found")

    def do_POST(self):

        if self.path != "/update":
            self.send_error(404)
            return

        username = self.headers.get("X-Username", "")
        password = self.headers.get("X-Password", "")

        if username != USERNAME or password != PASSWORD:

            self.send_text(
                "غير مصرح لك بتحديث الأسعار",
                403
            )

            return

        try:

            length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(length)

            data = json.loads(
                body.decode("utf-8")
            )

        except Exception:

            self.send_text(
                "بيانات غير صحيحة",
                400
            )

            return

        try:

            gold_buy = str(data["goldBuy"])
            gold_sell = str(data["goldSell"])

            dollar_buy = str(data["dollarBuy"])
            dollar_sell = str(data["dollarSell"])

            fuel = str(data["fuel"])

        except KeyError:

            self.send_text(
                "بيانات ناقصة",
                400
            )

            return

        time_now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open("../prices.txt", "w") as file:

            file.write(
                "Gold BUY: " + gold_buy + "\n"
            )

            file.write(
                "Gold SELL: " + gold_sell + "\n"
            )

            file.write(
                "Dollar BUY: " + dollar_buy + "\n"
            )

            file.write(
                "Dollar SELL: " + dollar_sell + "\n"
            )

            file.write(
                "Fuel: " + fuel + "\n"
            )

            file.write(
                "Last update: " + time_now + "\n"
            )

        with open("../history.txt", "a") as file:

            file.write(
                time_now
                + " | Gold: "
                + gold_buy
                + "/"
                + gold_sell
                + " | Dollar: "
                + dollar_buy
                + "/"
                + dollar_sell
                + " | Fuel: "
                + fuel
                + "\n"
            )

        self.send_text(
            "تم تحديث الأسعار بنجاح"
        )


# Render يحدد المنفذ من متغير PORT
PORT = int(os.environ.get("PORT", 8080))

server = HTTPServer(
    ("0.0.0.0", PORT),
    NyalaHandler
)

print("NYALA MARKET SERVER")
print("Listening on port:", PORT)

server.serve_forever()
