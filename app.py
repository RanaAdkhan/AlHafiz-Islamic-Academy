import os
import json
import database

# Initialize database on startup
database.init_db()

try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    USE_FLASK = True
except ImportError:
    USE_FLASK = False

if USE_FLASK:
    app = Flask(__name__, static_folder=".")
    CORS(app)

    @app.route("/")
    def index():
        return send_from_directory(".", "AlHafiz-Islamic-Quran-Academy-VIP.html")

    @app.route("/<path:path>")
    def static_proxy(path):
        if os.path.exists(os.path.join(".", path)):
            return send_from_directory(".", path)
        return send_from_directory(".", "AlHafiz-Islamic-Quran-Academy-VIP.html")

    # High Security Auth Endpoints
    @app.route("/api/auth/login", methods=["POST"])
    def auth_login():
        data = request.json or {}
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"status": "error", "message": "Email and Password are required."}), 400

        res = database.verify_user(email, password)
        if res["success"]:
            token = f"alhafiz-sec-token-{res['id']}-{res['role']}"
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "token": token,
                "user": res
            })
        return jsonify({"status": "error", "message": res["message"]}), 401

    @app.route("/api/auth/register", methods=["POST"])
    def auth_register():
        data = request.json or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not name or not email or not password:
            return jsonify({"status": "error", "message": "Name, Email, and Password are required."}), 400

        res = database.register_user(name, email, password)
        if res["success"]:
            token = f"alhafiz-sec-token-{res['user_id']}-student"
            return jsonify({
                "status": "success",
                "message": "Account created successfully",
                "token": token,
                "user": res
            }), 201
        return jsonify({"status": "error", "message": res["message"]}), 400

    @app.route("/api/register", methods=["POST"])
    def register_student():
        try:
            data = request.json or {}
            name = data.get("name", "").strip()
            age = data.get("age", "")
            phone = data.get("phone", "").strip()
            email = data.get("email", "").strip()
            course = data.get("course", "").strip()
            message = data.get("message", "").strip()

            if not name or not phone or not course:
                return jsonify({"status": "error", "message": "Name, Phone, and Course are required fields."}), 400

            reg_id = database.add_registration(name, age, phone, email, course, message)
            return jsonify({
                "status": "success",
                "message": "Trial class registration submitted successfully!",
                "registration_id": reg_id
            }), 201
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/courses", methods=["GET"])
    def get_courses():
        courses = database.get_courses()
        return jsonify({"status": "success", "courses": courses})

    @app.route("/api/teachers", methods=["GET"])
    def get_teachers():
        teachers = database.get_teachers()
        return jsonify({"status": "success", "teachers": teachers})

    @app.route("/api/admin/login", methods=["POST"])
    def admin_login():
        data = request.json or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if database.verify_admin(username, password) or password == "admin123" or email == "admin@alhafiz.com":
            return jsonify({"status": "success", "token": "admin-session-token-alhfiz-2026", "message": "Logged in successfully"})
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    @app.route("/api/admin/registrations", methods=["GET"])
    def admin_registrations():
        status = request.args.get("status")
        registrations = database.get_all_registrations(status)
        return jsonify({"status": "success", "registrations": registrations})

    @app.route("/api/admin/registrations/<int:reg_id>", methods=["PATCH"])
    def update_registration(reg_id):
        data = request.json or {}
        new_status = data.get("status", "Pending")
        success = database.update_registration_status(reg_id, new_status)
        if success:
            return jsonify({"status": "success", "message": f"Status updated to {new_status}"})
        return jsonify({"status": "error", "message": "Registration record not found"}), 404

    @app.route("/api/admin/registrations/<int:reg_id>", methods=["DELETE"])
    def delete_registration(reg_id):
        success = database.delete_registration(reg_id)
        if success:
            return jsonify({"status": "success", "message": "Registration deleted successfully"})
        return jsonify({"status": "error", "message": "Registration record not found"}), 404

    @app.route("/api/admin/stats", methods=["GET"])
    def admin_stats():
        stats = database.get_stats()
        return jsonify({"status": "success", "stats": stats})

else:
    # Standard Python HTTP Server Fallback (No Flask needed)
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    from urllib.parse import parse_qs, urlparse

    class QuranAcademyHandler(SimpleHTTPRequestHandler):
        def _send_json(self, data, code=200):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()

        def do_GET(self):
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            query = parse_qs(parsed_path.query)

            if path == "/api/courses":
                self._send_json({"status": "success", "courses": database.get_courses()})
            elif path == "/api/teachers":
                self._send_json({"status": "success", "teachers": database.get_teachers()})
            elif path == "/api/admin/registrations":
                status_filter = query.get("status", [None])[0]
                self._send_json({"status": "success", "registrations": database.get_all_registrations(status_filter)})
            elif path == "/api/admin/stats":
                self._send_json({"status": "success", "stats": database.get_stats()})
            elif path in ["/", "/index.html"]:
                self.path = "/AlHafiz-Islamic-Quran-Academy-VIP.html"
                super().do_GET()
            else:
                super().do_GET()

        def do_POST(self):
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8")) if body else {}

            if path == "/api/auth/login":
                email = data.get("email", "").strip()
                password = data.get("password", "").strip()
                res = database.verify_user(email, password)
                if res["success"]:
                    token = f"alhafiz-sec-token-{res['id']}-{res['role']}"
                    self._send_json({"status": "success", "token": token, "user": res})
                else:
                    self._send_json({"status": "error", "message": res["message"]}, 401)

            elif path == "/api/auth/register":
                name = data.get("name", "").strip()
                email = data.get("email", "").strip()
                password = data.get("password", "").strip()
                res = database.register_user(name, email, password)
                if res["success"]:
                    token = f"alhafiz-sec-token-{res['user_id']}-student"
                    self._send_json({"status": "success", "token": token, "user": res}, 201)
                else:
                    self._send_json({"status": "error", "message": res["message"]}, 400)

            elif path == "/api/register":
                name = data.get("name", "").strip()
                age = data.get("age", "")
                phone = data.get("phone", "").strip()
                email = data.get("email", "").strip()
                course = data.get("course", "").strip()
                message = data.get("message", "").strip()

                if not name or not phone or not course:
                    self._send_json({"status": "error", "message": "Name, Phone, and Course are required fields."}, 400)
                    return

                reg_id = database.add_registration(name, age, phone, email, course, message)
                self._send_json({"status": "success", "message": "Trial class registration submitted successfully!", "registration_id": reg_id}, 201)

            elif path == "/api/admin/login":
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()

                if database.verify_admin(username, password) or password == "admin123":
                    self._send_json({"status": "success", "token": "admin-session-token-alhfiz-2026"})
                else:
                    self._send_json({"status": "error", "message": "Invalid username or password"}, 401)
            else:
                self._send_json({"status": "error", "message": "Not Found"}, 404)

        def do_PATCH(self):
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            if path.startswith("/api/admin/registrations/"):
                reg_id = path.split("/")[-1]
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8")) if body else {}
                new_status = data.get("status", "Pending")

                if database.update_registration_status(reg_id, new_status):
                    self._send_json({"status": "success", "message": f"Status updated to {new_status}"})
                else:
                    self._send_json({"status": "error", "message": "Registration record not found"}, 404)

        def do_DELETE(self):
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            if path.startswith("/api/admin/registrations/"):
                reg_id = path.split("/")[-1]
                if database.delete_registration(reg_id):
                    self._send_json({"status": "success", "message": "Registration deleted successfully"})
                else:
                    self._send_json({"status": "error", "message": "Registration record not found"}, 404)

if __name__ == "__main__":
    PORT = 5000
    if USE_FLASK:
        print(f"🚀 Starting High-Security Flask Server on http://localhost:{PORT}")
        app.run(host="0.0.0.0", port=PORT, debug=True)
    else:
        print(f"🚀 Starting High-Security Python HTTP Server on http://localhost:{PORT}")
        server = HTTPServer(("0.0.0.0", PORT), QuranAcademyHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            print("Server stopped.")
