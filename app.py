from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from datetime import datetime
from urllib.parse import urlparse


# =========================
# إعدادات الملفات
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRICES_FILE = os.path.join(BASE_DIR, "prices.txt")
HISTORY_FILE = os.path.join(BASE_DIR, "history.txt")


# =========================
# بيانات الدخول من Render
# =========================

USERNAME = os.environ.get("USERNAME", "")
PASSWORD = os.environ.get("PASSWORD", "")


# =========================
# HTTP Handler
# =========================

class NyalaHandler(BaseHTTPRequestHandler):

    # -------------------------
    # إرسال نص
    # -------------------------

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


    # -------------------------
    # إرسال HTML
    # -------------------------

    def send_html(self, filename):

        file_path = os.path.join(
            BASE_DIR,
            filename
        )

        if not os.path.exists(file_path):

            self.send_error(
                404,
                "Page not found"
            )

            return


        with open(
            file_path,
            "rb"
        ) as file:

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


    # -------------------------
    # GET
    # -------------------------

    def do_GET(self):

        parsed = urlparse(self.path)

        path = parsed.path


        # الأسعار

        if path == "/prices.txt":

            if not os.path.exists(PRICES_FILE):

                self.send_text(
                    "Prices not found",
                    404
                )

                return


            with open(
                PRICES_FILE,
                "rb"
            ) as file:

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
                "Pragma",
                "no-cache"
            )

            self.send_header(
                "Expires",
                "0"
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            self.wfile.write(data)

            return


        # لوحة الإدارة

        if path == "/admin.html":

            self.send_html(
                "admin.html"
            )

            return


        # الصفحة الرئيسية

        if path == "/":

            self.send_html(
                "index.html"
            )

            return


        # أي مسار غير معروف

        self.send_error(
            404,
            "Not found"
        )


    # -------------------------
    # HEAD
    # -------------------------

    def do_HEAD(self):

        parsed = urlparse(self.path)

        path = parsed.path


        if path == "/prices.txt":

            if not os.path.exists(PRICES_FILE):

                self.send_error(
                    404,
                    "Prices not found"
                )

                return


            file_size = os.path.getsize(
                PRICES_FILE
            )

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(file_size)
            )

            self.send_header(
                "Cache-Control",
                "no-cache"
            )

            self.end_headers()

            return


        if path == "/" or path == "/admin.html":

            filename = (
                "index.html"
                if path == "/"
                else "admin.html"
            )

            file_path = os.path.join(
                BASE_DIR,
                filename
            )


            if not os.path.exists(file_path):

                self.send_error(
                    404,
                    "Page not found"
                )

                return


            file_size = os.path.getsize(
                file_path
            )


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(file_size)
            )

            self.end_headers()

            return


        self.send_error(
            404,
            "Not found"
        )


    # -------------------------
    # POST
    # -------------------------

    def do_POST(self):

        parsed = urlparse(self.path)

        path = parsed.path


        if path != "/update":

            self.send_error(
                404,
                "Not found"
            )

            return


        # -------------------------
        # التحقق من بيانات الدخول
        # -------------------------

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


        # -------------------------
        # قراءة البيانات
        # -------------------------

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


        if content_length <= 0:

            self.send_text(
                "لم يتم إرسال بيانات",
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


        # -------------------------
        # استخراج الأسعار
        # -------------------------

        required_fields = [
            "goldBuy",
            "goldSell",
            "dollarBuy",
            "dollarSell",
            "fuel"
        ]


        for field in required_fields:

            if field not in data:

                self.send_text(
                    "البيانات ناقصة: " + field,
                    400
                )

                return


        gold_buy = str(
            data["goldBuy"]
        )

        gold_sell = str(
            data["goldSell"]
        )

        dollar_buy = str(
            data["dollarBuy"]
        )

        dollar_sell = str(
            data["dollarSell"]
        )

        fuel = str(
            data["fuel"]
        )


        # -------------------------
        # وقت التحديث
        # -------------------------

        time_now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        # -------------------------
        # حفظ الأسعار
        # -------------------------

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
                    "Fuel: "
                    + fuel
                    + "\n"
                )

                file.write(
                    "Last update: "
                    + time_now
                    + "\n"
                )


            # -------------------------
            # حفظ التاريخ
            # -------------------------

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
                    + " | Fuel: "
                    + fuel
                    + "\n"
                )


        except Exception as error:

            print(
                "ERROR SAVING PRICES:",
                error
            )

            self.send_text(
                "حدث خطأ أثناء حفظ الأسعار",
                500
            )

            return


        # -------------------------
        # نجاح
        # -------------------------

        self.send_text(
            "تم تحديث الأسعار بنجاح",
            200
        )


# =========================
# تشغيل السيرفر
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "8080"
        )
    )


    server = HTTPServer(
        (
            "0.0.0.0",
            port
        ),
        NyalaHandler
    )


    print(
        "NYALA MARKET SERVER"
    )

    print(
        "Listening on 0.0.0.0:"
        + str(port)
    )

    print(
        "Prices file: "
        + PRICES_FILE
    )


    server.serve_forever()
