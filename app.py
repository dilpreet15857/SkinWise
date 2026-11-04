
from flask import Flask, render_template, request, session, redirect, url_for

from recommendation import generate_recommendation
from products import recommend_products


def calculate_skin_type(answers):

    scores = {
        "Normal": 0,
        "Oily": 0,
        "Dry": 0,
        "Combination": 0
    }

    for answer in answers:
        scores[answer] += 1

    skin_type = max(scores, key=scores.get)

    return skin_type


import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "skinwise_local_dev_key")


@app.route("/")
def home():
    return render_template("index.html")


# Know Your Skin assessment

@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    if request.method == "POST":

        # Collect answers to the five skin-type questions
        answers = [
            request.form.get("q1"),
            request.form.get("q2"),
            request.form.get("q3"),
            request.form.get("q4"),
            request.form.get("q5")
        ]

        # Determine the skin type
        skin_type = calculate_skin_type(answers)

        # Save it for future use
        session["skin_type"] = skin_type

        # Show the skin type result
        return render_template(
            "skin-result.html",
            skin_type=skin_type
        )

    return render_template("assessment.html")


# Independent Find Your Routine tool

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
                    "Please select your skin type manually or complete "
                    "the questionnaire."
                )

        else:
            skin_type = request.form.get("skin_type")

        if not error:

            concerns = request.form.getlist("concerns")
            sensitivity = request.form.get("sensitivity")

            # Generate the personalised routine
            recommendations = generate_recommendation(
                skin_type, concerns, sensitivity
            )

            # Save all routine assessment details for future use
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

# Independent Find Your Products tool


# Independent Find Your Products tool

@app.route("/find-products", methods=["GET", "POST"])
def find_products():

    saved_skin_type = session.get("skin_type")
    error = None

    if request.method == "POST":

        # Choose saved or manually entered skin type
        details_source = request.form.get("details_source")

        if details_source == "saved":
            skin_type = session.get("skin_type")

            if not skin_type:
                error = "No previous skin assessment found. Please select your skin type manually."

        else:
            skin_type = request.form.get("skin_type")

        # Only one main concern is selected
        main_concern = request.form.get("main_concern")

        # Get total budget
        budget = request.form.get("budget")

        # Validate the submitted details
        if not error:

            if skin_type not in ["Normal", "Oily", "Dry", "Combination"]:
                error = "Please select a valid skin type."

            elif main_concern not in ["Acne", "Dullness", "Dark Spots", "Blackheads"]:
                error = "Please select your main skin concern."

            elif not budget or not budget.isdigit() or int(budget) <= 0:
                error = "Please enter a valid budget."

        if not error:

            budget = int(budget)

            # Convert the single concern into a list
            concerns = [main_concern]

            # Generate product recommendations.
            # Sensitivity is not asked in this questionnaire.
            recommended_products = recommend_products(
                skin_type,
                concerns,
                None,
                budget
            )

            # Save the skin type for future use
            session["skin_type"] = skin_type

            return render_template(
                "product-results.html",
                skin_type=skin_type,
                concerns=concerns,
                sensitivity="Not specified",
                budget=budget,
                product_plan=recommended_products
            )

    return render_template(
        "find-products.html",
        saved_skin_type=saved_skin_type,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=False)
