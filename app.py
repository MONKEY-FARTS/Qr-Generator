from flask import Flask, render_template, request, Response, url_for, send_file
import qrcode
import io
import base64
import uuid

app = Flask(__name__)

images = {}
qrs = {}  

@app.route("/", methods=["GET", "POST"])
def index():
    img_data_url = None
    img_data_img = None
    download_url_url = None
    download_url_img = None
    if request.method == "POST":
        form_type = request.form.get("type")
        if form_type == "url":
            web = request.form.get("webName")
            if web:
                qr = qrcode.make(web)
                buffer = io.BytesIO()
                qr.save(buffer, format="PNG")
                buffer.seek(0)
                qr_id = str(uuid.uuid4())
                qrs[qr_id] = buffer.getvalue()
                img_data_url = base64.b64encode(
                    qrs[qr_id]
                ).decode("utf-8")
                download_url_url = url_for("download_qr", qr_id=qr_id)
        elif form_type == "img":
            image = request.files.get("image")
            if image:
                img_id = str(uuid.uuid4())
                images[img_id] = image.read()
                img_url = url_for("get_image", img_id=img_id, _external=True)
                qr = qrcode.make(img_url)
                buffer = io.BytesIO()
                qr.save(buffer, format="PNG")
                buffer.seek(0)
                qr_id = str(uuid.uuid4())
                qrs[qr_id] = buffer.getvalue()
                img_data_img = base64.b64encode(
                    qrs[qr_id]
                ).decode("utf-8")
                download_url_img = url_for("download_qr", qr_id=qr_id)

    return render_template(
        "index.html",
        img_data_url=img_data_url,
        img_data_img=img_data_img,
        download_url_url=download_url_url,
        download_url_img=download_url_img
    )


@app.route("/image/<img_id>")
def get_image(img_id):
    if img_id in images:
        return Response(images[img_id], mimetype="image/png")
    return "Not found", 404

@app.route("/download/<qr_id>")
def download_qr(qr_id):
    if qr_id in qrs:
        return send_file(
            io.BytesIO(qrs[qr_id]),
            mimetype="image/png",
            as_attachment=True,
            download_name="qr.png"
        )
    return "Not found", 404

if __name__ == "__main__":
    app.run(debug=True) 