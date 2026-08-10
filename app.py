from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from datetime import datetime
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRICES_FILE = os.path.join(BASE_DIR, "prices.txt")
HISTORY_FILE = os.path.join(BASE_DIR, "history.txt")

USERNAME = os.environ.get("USERNAME", "")
PASSWORD = os.environ.get("PASSWORD", "")

if not os.path.exists(PRICES_FILE):
    with open(PRICES_FILE, "w", encoding="utf-8") as file:
        file.write("Gold BUY: 4350\n")
        file.write("Gold SELL: 4370\n")
        file.write("Dollar BUY: 4250\n")
        file.write("Dollar SELL: 4280\n")
        file.write("Diesel: 1400\n")
        file.write("Gasoline: 0\n")
        file.write("Last update: --\n")

if not os.path.exists(HISTORY_FILE):
    open(HISTORY_FILE, "w", encoding="utf-8").close()


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

        if self.command != "HEAD":
            self.wfile.write(data)


    def send_html(self, filename):
        file_path = os.path.join(BASE_DIR, filename)

        if not os.path.exists(file_path):
            self.send_error(404, "Page not found")
            return

        with open(file_path, "rb") as file:
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

        if self.command != "HEAD":
            self.wfile.write(data)


    def do_GET(self):

        path = urlparse(self.path).path


        if path == "/prices.txt":

            if not os.path.exists(PRICES_FILE):
                self.send_text("Prices not found", 404)
                return

            with open(PRICES_FILE, "rb") as file:
                data = file.read()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_header(
                "Cache-Control",
                "no-cache, no-store, must-revalidate"
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(data)

            return


        if path == "/history.txt":

            with open(HISTORY_FILE, "rb") as file:
                data = file.read()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_header(
                "Cache-Control",
                "no-cache, no-store, must-revalidate"
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(data)

            return


        if path == "/admin.html":
            self.send_html("admin.html")
            return


        if path == "/history.html":
            self.send_html("history.html")
            return


        if path == "/chart.html":
            self.send_html("chart.html")
            return


        if path == "/":
            self.send_html("index.html")
            return


        self.send_error(404, "Not found")


    def do_HEAD(self):

        path = urlparse(self.path).path

        if path in (
            "/",
            "/admin.html",
            "/history.html",
            "/chart.html",
            "/prices.txt",
            "/history.txt"
        ):

            self.send_response(200)
            self.end_headers()
            return

        self.send_error(404)


    def do_POST(self):

        path = urlparse(self.path).path

        if path != "/update":
            self.send_error(404)
            return


        username = self.headers.get(
            "X-Username",
            ""
        )

        password = self.headers.get(
            "X-Password",
            ""
        )


        if (
            not USERNAME
            or not PASSWORD
            or username != USERNAME
            or password != PASSWORD
        ):

            self.send_text(
                "غير مصرح لك بتحديث الأسعار",
                403
            )

            return


        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

        except ValueError:

            self.send_text(
                "بيانات غير صحيحة",
                400
            )

            return


        body = self.rfile.read(
            content_length
        )


        try:

            data = json.loads(
                body.decode("utf-8")
            )

        except Exception:

            self.send_text(
                "بيانات JSON غير صحيحة",
                400
            )

            return


        fields = [
            "goldBuy",
            "goldSell",
            "dollarBuy",
            "dollarSell",
            "diesel",
            "gasoline"
        ]


        for field in fields:

            if field not in data:

                self.send_text(
                    "البيانات ناقصة: " + field,
                    400
                )

                return


        gold_buy = str(data["goldBuy"])
        gold_sell = str(data["goldSell"])

        dollar_buy = str(data["dollarBuy"])
        dollar_sell = str(data["dollarSell"])

        diesel = str(data["diesel"])
        gasoline = str(data["gasoline"])


        time_now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        try:

            with open(
                PRICES_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    "Gold BUY: "
                    + gold_buy
                    + "\n"
                )

                file.write(
                    "Gold SELL: "
                    + gold_sell
                    + "\n"
                )

                file.write(
                    "Dollar BUY: "
                    + dollar_buy
                    + "\n"
                )

                file.write(
                    "Dollar SELL: "
                    + dollar_sell
                    + "\n"
                )

                file.write(
                    "Diesel: "
                    + diesel
                    + "\n"
                )

                file.write(
                    "Gasoline: "
                    + gasoline
                    + "\n"
                )

                file.write(
                    "Last update: "
                    + time_now
                    + "\n"
                )


            with open(
                HISTORY_FILE,
                "a",
                encoding="utf-8"
            ) as file:

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
                    + " | Diesel: "
                    + diesel
                    + " | Gasoline: "
                    + gasoline
                    + "\n"
                )


        except Exception as error:

            print(
                "ERROR:",
                error
            )

            self.send_text(
                "حدث خطأ أثناء حفظ الأسعار",
                500
            )

            return


        self.send_text(
            "تم تحديث الأسعار بنجاح",
            200
        )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "8080"
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        NyalaHandler
    )

    print("NYALA MARKET SERVER")

    print(
        "Listening on 0.0.0.0:"
        + str(port)
    )

    print(
        "Prices file: "
        + PRICES_FILE
    )

    print(
        "History file: "
        + HISTORY_FILE
    )

    server.serve_forever()
