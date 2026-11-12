
import os

from flask import Flask, render_template, request, session

from recommendation import generate_recommendation
from products import recommend_products


app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "skinwise_local_dev_key"
)


def calculate_skin_type(answers):

    scores = {
        "Normal": 0,
        "Oily": 0,
        "Dry": 0,
        "Combination": 0
    }

    for answer in answers:
        if answer in scores:
            scores[answer] += 1

    return max(scores, key=scores.get)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html", contact_email=os.environ.get("CONTACT_EMAIL", "").strip())


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html")


@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/robots.txt")
def robots():
    from flask import Response
    body = "User-agent: *\nAllow: /\nSitemap: https://skinwise-mla3.onrender.com/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    from flask import Response
    pages = ["", "about", "contact", "privacy-policy", "disclaimer", "terms"]
    urls = "".join(f"<url><loc>https://skinwise-mla3.onrender.com/{page}</loc></url>" for page in pages)
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>'
    return Response(xml, mimetype="application/xml")


# ----------------------------------
# KNOW YOUR SKIN ASSESSMENT
# ----------------------------------

@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    if request.method == "POST":

        answers = [
            request.form.get("q1"),
            request.form.get("q2"),
            request.form.get("q3"),
            request.form.get("q4"),
            request.form.get("q5")
        ]

        if any(answer not in [
            "Normal", "Oily", "Dry", "Combination"
        ] for answer in answers):
            return render_template(
                "assessment.html",
                error="Please answer all five questions."
            )

        skin_type = calculate_skin_type(answers)

        session["skin_type"] = skin_type

        skin_type_details = {
            "Normal": "Normal skin often feels comfortable and balanced, with neither persistent oiliness nor dryness. Keep the routine gentle and consistent.",
            "Oily": "Oily skin may produce more sebum and can look shiny, especially through the T-zone. Lightweight, non-comedogenic products may feel more comfortable.",
            "Dry": "Dry skin can feel tight, rough or flaky. Gentle cleansing and a moisturiser that supports the skin barrier can help reduce that feeling.",
            "Combination": "Combination skin commonly has more oil through the forehead, nose and chin, while the cheeks may feel normal or dry. You may prefer to adjust product textures across different areas."
        }
        return render_template("skin-result.html", skin_type=skin_type,
                               skin_type_details=skin_type_details[skin_type])

    return render_template("assessment.html")


# ----------------------------------
# FIND YOUR ROUTINE
# ----------------------------------

@app.route("/find-your-routine", methods=["GET", "POST"])
def find_your_routine():

    saved_skin_type = session.get("skin_type")
    error = None

    if request.method == "POST":

        skin_type_source = request.form.get("skin_type_source")

        if skin_type_source == "saved":
            skin_type = session.get("skin_type")

            if not skin_type:
                error = (
                    "You haven't completed Know Your Skin yet. "
                    "Please select your skin type manually."
                )
        else:
            skin_type = request.form.get("skin_type")

        if not error:

            if skin_type not in [
                "Normal", "Oily", "Dry", "Combination"
            ]:
                error = "Please select a valid skin type."

        if not error:

            concerns = request.form.getlist("concerns")
            sensitivity = request.form.get("sensitivity")

            recommendations = generate_recommendation(
                skin_type,
                concerns,
                sensitivity
            )

            session["skin_type"] = skin_type
            session["concerns"] = concerns
            session["sensitivity"] = sensitivity

            return render_template(
                "routine-result.html",
                skin_type=skin_type,
                concerns=concerns,
                sensitivity=sensitivity,
                recommendations=recommendations
            )

    return render_template(
        "find-your-routine.html",
        saved_skin_type=saved_skin_type,
        error=error
    )


# ----------------------------------
# FIND YOUR PRODUCTS
# ----------------------------------

@app.route("/find-products", methods=["GET", "POST"])
def find_products():

    saved_skin_type = session.get("skin_type")
    error = None

    if request.method == "POST":

        details_source = request.form.get("details_source")

        if details_source == "saved":
            skin_type = session.get("skin_type")

            if not skin_type:
                error = (
                    "No previous skin assessment found. "
                    "Please select your skin type manually."
                )
        else:
            skin_type = request.form.get("skin_type")

        main_concern = request.form.get("main_concern")
        budget = request.form.get("budget")

        preferred_brands = request.form.getlist(
            "preferred_brands"
        )

        if not error:

            if skin_type not in [
                "Normal", "Oily", "Dry", "Combination"
            ]:
                error = "Please select a valid skin type."

            elif main_concern not in [
                "Acne", "Dullness", "Dark Spots", "Blackheads"
            ]:
                error = "Please select your main skin concern."

            elif not budget or not budget.isdigit() or int(budget) <= 0:
                error = "Please enter a valid budget."

        if not error:

            budget = int(budget)
            concerns = [main_concern]

            recommended_products = recommend_products(
                skin_type,
                concerns,
                None,
                budget,
                preferred_brands=preferred_brands
            )

            session["skin_type"] = skin_type
            session["concerns"] = concerns
            session["preferred_brands"] = preferred_brands

            return render_template(
                "product-results.html",
                skin_type=skin_type,
                concerns=concerns,
                sensitivity="Not specified",
                budget=budget,
                preferred_brands=preferred_brands,
                product_plan=recommended_products
            )

    return render_template(
        "find-products.html",
        saved_skin_type=saved_skin_type,
        error=error
    )


# ----------------------------------
# RUN APPLICATION
# ----------------------------------

if __name__ == "__main__":
    app.run(debug=True)
